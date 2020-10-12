import discord
from discord.ext import commands

from geeksbot.imports.utils import Paginator, Book


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def request(self, ctx, *, message=None):
        if not ctx.guild:
            await ctx.send("This command must be run from inside a guild.")
            return

        if not message:
            await ctx.send("Please include a message containing your request")
            return

        if len(message) > 1000:
            await ctx.send(
                "Request is too long, please keep your request to less than 1000 characters."
            )
            return

        data = {
            "author": ctx.author.id,
            "message": ctx.message.id,
            "channel": ctx.channel.id,
            "content": message,
        }
        msg_resp = await self.bot.aio_session.get(
            f"{self.bot.api_base}/messages/{ctx.message.id}/wait/",
            headers=self.bot.auth_header,
        )
        if msg_resp.status == 404:
            error = await msg_resp.json()
            await ctx.send(error["details"])
            return

        resp = await self.bot.aio_session.post(
            f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/",
            headers=self.bot.auth_header,
            json=data,
        )

        if resp.status == 201:
            admin_channel_resp = await self.bot.aio_session.get(
                f"{self.bot.api_base}/channels/{ctx.guild.id}/admin/",
                headers=self.bot.auth_header,
            )
            request = await resp.json()

            if admin_channel_resp.status == 200:
                admin_chan_data = await admin_channel_resp.json()
                msg = f""
                admin_roles_resp = await self.bot.aio_session.get(
                    f"{self.bot.api_base}/guilds/{ctx.guild.id}/roles/admin/",
                    headers=self.bot.auth_header,
                )
                if admin_roles_resp.status == 200:
                    admin_roles_data = await admin_roles_resp.json()
                    for role in admin_roles_data:
                        msg += f'{ctx.guild.get_role(int(role["id"])).mention} '
                msg += (
                    f"New Request ID: {request['id']} "
                    f"{ctx.author.mention} has requested assistance: \n"
                    f"```{request['content']}``` \n"
                    f"Requested at: {request['requested_at'].split('.')[0].replace('T', ' ')} GMT\n"
                    f"In {ctx.guild.get_channel(int(request['channel'])).name}"
                )
                admin_chan = ctx.guild.get_channel(int(admin_chan_data["id"]))
                await admin_chan.send(msg)
            await ctx.send(
                f"{ctx.author.mention} The admin have received your request.\n"
                f'If you would like to update or close your request please reference Request ID `{request["id"]}`'
            )

    @commands.command(aliases=["comment"])
    async def update(self, ctx, request_id=None, *, comment: str = None):
        try:
            request_id = int(request_id)
        except ValueError:
            await ctx.send(
                "Please include the ID of the request you would like to update as the first thing after the command."
            )
            return

        if not comment:
            await ctx.send(
                "There is nothing to update since you didn't include a message."
            )
            return

        data = {"author": ctx.author.id, "content": comment}

        comment_resp = await self.bot.aio_session.post(
            f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/{request_id}/comments/",
            headers=self.bot.auth_header,
            json=data,
        )

        if comment_resp.status == 201:
            comment = await comment_resp.json()
            admin_channel_resp = await self.bot.aio_session.get(
                f"{self.bot.api_base}/channels/{ctx.guild.id}/admin/",
                headers=self.bot.auth_header,
            )

            if admin_channel_resp.status == 200:
                admin_channel_data = await admin_channel_resp.json()
                admin_channel = ctx.guild.get_channel(int(admin_channel_data["id"]))
                if admin_channel:
                    request_resp = await self.bot.aio_session.get(
                        f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/{request_id}/",
                        headers=self.bot.auth_header,
                    )
                    pag = Paginator(self.bot, prefix="```md", suffix="```")
                    header = (
                        f"{ctx.author.mention} has commented on request {request_id}\n"
                    )
                    if request_resp.status == 200:
                        request = await request_resp.json()
                        requestor = await ctx.guild.fetch_member(int(request["author"]))
                        header += (
                            f'Original Request by {requestor.mention if requestor else "`User cannot be found`"}:\n'
                            f'```{request["content"]}```'
                        )
                        pag.set_header(header)

                        if request.get("comments"):
                            comments = request["comments"]
                            for comment in comments:
                                author = await ctx.guild.fetch_member(
                                    int(comment["author"])
                                )
                                pag.add(
                                    f'{author.display_name}: {comment["content"]}',
                                    keep_intact=True,
                                )
                        if ctx.author != requestor and requestor:
                            for page in pag.pages(page_headers=False):
                                await requestor.send(page)
                    book = Book(pag, (None, admin_channel, self.bot, ctx.message))
                    await book.create_book()
            await ctx.send(
                f"{ctx.author.mention} Your comment has been added to the request."
            )

    @commands.command(name="requests_list", aliases=["rl"])
    async def _requests_list(self, ctx, closed: str = ""):
        pag = Paginator(self.bot)
        admin_roles_resp = await self.bot.aio_session.get(
            f"{self.bot.api_base}/guilds/{ctx.guild.id}/roles/admin/",
            headers=self.bot.auth_header,
        )
        if admin_roles_resp.status == 200:
            admin_roles_data = await admin_roles_resp.json()
            admin_roles = [
                ctx.guild.get_role(int(role["id"])) for role in admin_roles_data
            ]
            if any([role in ctx.author.roles for role in admin_roles]):
                requests_resp = await self.bot.aio_session.get(
                    f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/",
                    headers=self.bot.auth_header,
                )
                if requests_resp.status == 200:
                    requests_data = await requests_resp.json()
                    requests_list = (
                        requests_data["requests"]
                        if isinstance(requests_data, dict)
                        else requests_data
                    )
                    while isinstance(requests_data, dict) and requests_data.get("next"):
                        requests_resp = await self.bot.aio_session.get(
                            requests_data["next"], headers=self.bot.auth_header
                        )
                        if requests_resp.status == 200:
                            requests_data = await requests_resp.json()
                            requests_list.extend(
                                requests_data["requests"]
                                if isinstance(requests_data, dict)
                                else requests_data
                            )
                    for request in requests_list:
                        member = discord.utils.get(
                            ctx.guild.members, id=int(request["author"])
                        )
                        title = (
                            f"<{'Request ID':^20} {'Requested By':^20}>\n"
                            f"<{request['id']:^20} {member.display_name if member else 'None':^20}>"
                        )
                        orig_channel = ctx.guild.get_channel(
                            int(request.get("channel"))
                        )
                        comments_count_resp = await self.bot.aio_session.get(
                            f'{self.bot.api_base}/messages/{ctx.guild.id}/requests/{request["id"]}/comments/count/',
                            headers=self.bot.auth_header,
                        )
                        pag.add(
                            f"\n\n{title}\n"
                            f"{request['content']}\n\n"
                            f"Comments: {await comments_count_resp.text() if comments_count_resp.status == 200 else 0}\n"
                            f"Requested at: "
                            f"{request['requested_at'].split('.')[0].replace('T', ' ')} GMT\n"
                            f"In {orig_channel.name if orig_channel else 'N/A'}",
                            keep_intact=True,
                        )
                    pag.add(
                        f"\n\uFFF8\nThere are currently {len(requests_list)} requests open."
                    )
                else:
                    pag.add(
                        "There are no open requests for this guild.", keep_intact=True
                    )
            else:
                requests_resp = await self.bot.aio_session.get(
                    f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/user/{ctx.author.id}/",
                    headers=self.bot.auth_header,
                )
                if requests_resp.status == 200:
                    requests_data = await requests_resp.json()
                    requests_list = (
                        requests_data["requests"]
                        if isinstance(requests_data, dict)
                        else requests_data
                    )
                    while isinstance(requests_data, dict) and requests_data.get("next"):
                        requests_resp = await self.bot.aio_session.get(
                            requests_data["next"], headers=self.bot.auth_header
                        )
                        if requests_resp.status == 200:
                            requests_data = await requests_resp.json()
                            requests_list.extend(
                                requests_data["requests"]
                                if isinstance(requests_data, dict)
                                else requests_data
                            )
                    for request in requests_list:
                        title = f"<{'Request ID':^20}>\n" f"<{request['id']:^20}>"
                        orig_channel = ctx.guild.get_channel(
                            int(request.get("channel"))
                        )
                        comments_count_resp = await self.bot.aio_session.get(
                            f'{self.bot.api_base}/messages/{ctx.guild.id}/requests/{request["id"]}/comments/count/',
                            headers=self.bot.auth_header,
                        )
                        pag.add(
                            f"\n\n{title}\n"
                            f"{request['content']}\n\n"
                            f"Comments: {await comments_count_resp.text() if comments_count_resp.status == 200 else 0}\n"
                            f"Requested at: "
                            f"{request['requested_at'].split('.')[0].replace('T', ' ')} GMT\n"
                            f"In {orig_channel.name if orig_channel else 'N/A'}",
                            keep_intact=True,
                        )
                    pag.add(
                        f"\n\uFFF8\nYou currently have {len(requests_list)} requests open."
                    )
                else:
                    pag.add(
                        "You have no open requests for this guild.", keep_intact=True
                    )
        for page in pag.pages():
            await ctx.send(page)

    @commands.command()
    async def close(self, ctx, *, ids=None):
        if not ids:
            await ctx.send("Please include at least one Request ID to close.")
            return

        admin = False
        admin_roles_resp = await self.bot.aio_session.get(
            f"{self.bot.api_base}/guilds/{ctx.guild.id}/roles/admin/",
            headers=self.bot.auth_header,
        )
        if admin_roles_resp.status == 200:
            admin_roles_data = await admin_roles_resp.json()
            admin_roles = [
                ctx.guild.get_role(int(role["id"])) for role in admin_roles_data
            ]
            if any([role in ctx.author.roles for role in admin_roles]):
                admin = True

        ids = [id.strip() for id in ids.replace(" ", "").split(",")]

        for id in ids:
            request_resp = await self.bot.aio_session.get(
                f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/{id}/",
                headers=self.bot.auth_header,
            )
            if request_resp.status == 200:
                request = await request_resp.json()
                requestor = await ctx.guild.fetch_member(int(request["author"]))
                if requestor == ctx.author or admin:
                    data = {"completed_by": ctx.author.id}
                    delete_resp = await self.bot.aio_session.delete(
                        f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/{id}/",
                        headers=self.bot.auth_header,
                        json=data,
                    )
                    if delete_resp.status == 202:
                        delete_data = await delete_resp.json()
                        if delete_data["completed"]:
                            await ctx.send(f"Request {id} closed.")
                            await requestor.send(
                                f"{ctx.author.display_name} has closed request {id} which was "
                                f"opened by you in the "
                                f'{ctx.guild.get_channel(int(request["channel"])).name} '
                                f"channel."
                                f'```{request["content"]}```'
                                f"If there are any issues please open a new request."
                            )
                else:
                    await ctx.send("That is not your request to close.")

    @commands.command()
    async def view(self, ctx, id=None):
        if not id:
            await ctx.send(
                "Please include the id of the request you would like to view."
            )
            return

        admin = False
        admin_roles_resp = await self.bot.aio_session.get(
            f"{self.bot.api_base}/guilds/{ctx.guild.id}/roles/admin/",
            headers=self.bot.auth_header,
        )
        if admin_roles_resp.status == 200:
            admin_roles_data = await admin_roles_resp.json()
            admin_roles = [
                ctx.guild.get_role(int(role["id"])) for role in admin_roles_data
            ]
            if any([role in ctx.author.roles for role in admin_roles]):
                admin = True

        request_resp = await self.bot.aio_session.get(
            f"{self.bot.api_base}/messages/{ctx.guild.id}/requests/{id}/",
            headers=self.bot.auth_header,
        )
        if request_resp.status == 200:
            request = await request_resp.json()
            requestor = await ctx.guild.fetch_member(int(request["author"]))
            if requestor == ctx.author or admin:
                pag = Paginator(self.bot, prefix="```md", suffix="```")
                header = (
                    f'Request {id} by {requestor.mention if requestor else "`User cannot be found`"}:\n'
                    f'```{request["content"]}```'
                )
                pag.set_header(header)

                if request.get("comments"):
                    pag.add("Comments: \n")
                    comments = request["comments"]
                    for comment in comments:
                        author = await ctx.guild.fetch_member(int(comment["author"]))
                        pag.add(
                            f'{author.display_name}: {comment["content"]}',
                            keep_intact=True,
                        )
                else:
                    pag.add("No Comments")

                if request.get("completed"):
                    closer = await ctx.guild.fetch_member(
                        int(request.get("completed_by"))
                    )
                    pag.add(
                        f'Closed By: {closer.name}#{closer.discriminator}\n{request.get("completed_message")}'
                    )
                book = Book(pag, (None, ctx.channel, self.bot, ctx.message))
                await book.create_book()
            else:
                await ctx.send("That is not your request to close.")


def setup(bot):
    bot.add_cog(Tickets(bot))
