from src.shared_libs.guid import Guid
import random
from copy import deepcopy

__all__ = ['Player', 'AIPlayer']


class Player:
    def __init__(self, token: str, *, name: str=None, id: str=None, discord_id: int=None):
        if len(token) != 1:
            raise Warning('Token must be exactly one character long.')
        self.token = token
        self.name = name or f'Player {self.token}'
        self.id = id or Guid()
        self.starting_player = False
        self.discord_id = discord_id

    def __repr__(self):
        return f'<TicTacToe Player name="{self.name}" id="{self.id}">'

    def __str__(self):
        return self.token

    def __eq__(self, other):
        if isinstance(other, Player) and other.id == self.id:
            return True
        elif isinstance(other, str):
            return self.token == other


class AIPlayer(Player):
    def __init__(self, token: str=None, name: str=None, human: Player=None, *, id: str=None):
        token = token or '🇽'
        if human:
            if human.token == token and human.token != '🇴':
                token = '🇴'
            elif human.token == '🇴':
                token = '🇽'
        super().__init__(token, name=name or f'Robot {token}', id=id)
        self._corner_moves = [1, 3, 7, 9]
        self._side_moves = [2, 4, 6, 8]
        self._center_move = 5
        self.remaining_corners = deepcopy(self._corner_moves)
        self.remaining_sides = deepcopy(self._side_moves)

    def make_selection(self, board, last_play: int=None) -> int:
        if last_play in self.remaining_corners:
            self.remaining_corners.remove(last_play)
        elif last_play in self.remaining_sides:
            self.remaining_sides.remove(last_play)

        winning_move = self.check_winning_move(board)
        if winning_move:
            move = winning_move
        else:
            blocking_move = self.check_blocking_move(board)
            if blocking_move:
                move = blocking_move
            else:
                trap_move = self.attempt_trap(board)
                if trap_move:
                    move = trap_move
                else:
                    starting_move = self.starting_strategy(board)
                    if self.starting_player and starting_move:
                        move = starting_move
                    else:
                        if board.board[1][1] == ' ':
                            move = 5
                        else:
                            if self.check_corner_trap(board):
                                move = random.choice(self.remaining_sides)
                            else:
                                if self.remaining_corners:
                                    move = random.choice(self.remaining_corners)
                                else:
                                    move = random.choice(self.remaining_sides)
        if move in self.remaining_corners:
            self.remaining_corners.remove(move)
        elif move in self.remaining_sides:
            self.remaining_sides.remove(move)
        print(move)
        return move

    def starting_strategy(self, board):
        move = False
        if board.play_count == 0:
            move = random.choice(self.remaining_corners)
            self.remaining_corners.remove(move)
        elif board.play_count == 2:
            if (board.board[0][0] == self and ' ' != board.board[2][2] != self) \
                    or (board.board[2][2] == self and ' ' != board.board[0][0] != self) \
                    or (board.board[2][0] == self and ' ' != board.board[0][2] != self) \
                    or (board.board[0][2] == self and ' ' != board.board[2][0] != self):
                move = random.choice(self.remaining_corners)
            else:
                if board.board[0][0] == self:
                    move = 9
                elif board.board[2][2] == self:
                    move = 1
                elif board.board[0][2] == self:
                    move = 7
                elif board.board[2][0] == self:
                    move = 3
            self.remaining_corners.remove(move)
        elif board.play_count == 4 and self.remaining_corners:
            move = random.choice(self.remaining_corners)
            self.remaining_corners.remove(move)
        return move


    def check_corner_trap(self, board):
        if ' ' != board.board[0][0] == board.board[2][2] != self:
            return True
        elif ' ' != board.board[0][2] == board.board[2][0] != self:
            return True
        return False

    def check_blocking_move(self, board):
        for position in board.winning_states:
            if ' ' != board.board[position[0][0]][position[0][1]] == \
                    board.board[position[1][0]][position[1][1]] != self \
                    and board.board[position[2][0]][position[2][1]] == ' ':
                return ((position[2][0] * 3) + position[2][1]) + 1
            elif ' ' != board.board[position[0][0]][position[0][1]] == \
                    board.board[position[2][0]][position[2][1]] != self \
                    and board.board[position[1][0]][position[1][1]] == ' ':
                return ((position[1][0] * 3) + position[1][1]) + 1
            elif ' ' != board.board[position[2][0]][position[2][1]] == \
                    board.board[position[1][0]][position[1][1]] != self \
                    and board.board[position[0][0]][position[0][1]] == ' ':
                return ((position[0][0] * 3) + position[0][1]) + 1
        return False

    def check_winning_move(self, board):
        for position in board.winning_states:
            if board.board[position[0][0]][position[0][1]] == board.board[position[1][0]][position[1][1]] == self \
                    and board.board[position[2][0]][position[2][1]] == ' ':
                return ((position[2][0] * 3) + position[2][1]) + 1
            elif board.board[position[0][0]][position[0][1]] == board.board[position[2][0]][position[2][1]] == self \
                    and board.board[position[1][0]][position[1][1]] == ' ':
                return ((position[1][0] * 3) + position[1][1]) + 1
            elif board.board[position[2][0]][position[2][1]] == board.board[position[1][0]][position[1][1]] == self \
                    and board.board[position[0][0]][position[0][1]] == ' ':
                return ((position[0][0] * 3) + position[0][1]) + 1
        return False

    def attempt_trap(self, board):
        if board.board[1][1] == self:
            if board.board[0][0] == self and \
                    board.board[0][1] == ' ' and \
                    board.board[0][2] == ' ' and \
                    board.board[2][0] == ' ':
                return 3
            elif board.board[0][0] == self and \
                    board.board[1][0] == ' ' and \
                    board.board[0][2] == ' ' and \
                    board.board[2][0] == ' ':
                return 7
            elif board.board[0][2] == self and \
                    board.board[0][1] == ' ' and \
                    board.board[0][0] == ' ' and \
                    board.board[2][2] == ' ':
                return 1
            elif board.board[0][2] == self and \
                    board.board[1][2] == ' ' and \
                    board.board[0][0] == ' ' and \
                    board.board[2][2] == ' ':
                return 9
            elif board.board[2][0] == self and \
                    board.board[0][0] == ' ' and \
                    board.board[0][1] == ' ' and \
                    board.board[2][2] == ' ':
                return 1
            elif board.board[2][0] == self and \
                    board.board[2][1] == ' ' and \
                    board.board[2][2] == ' ' and \
                    board.board[0][0] == ' ':
                return 9
            elif board.board[2][2] == self and \
                    board.board[2][1] == ' ' and \
                    board.board[2][0] == ' ' and \
                    board.board[0][2] == ' ':
                return 7
            elif board.board[2][2] == self and \
                    board.board[1][2] == ' ' and \
                    board.board[0][2] == ' ' and \
                    board.board[2][0] == ' ':
                return 3
        return False

    def reset_game(self):
        self.remaining_sides = deepcopy(self._side_moves)
        self.remaining_corners = deepcopy(self._corner_moves)
        self.starting_player = False
