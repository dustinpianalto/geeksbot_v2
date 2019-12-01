from src.shared_libs.guid import Guid
from src.shared_libs.TicTacToe.player import Player


class Board:
    def __init__(self):
        self.id = Guid()
        self.board = [[' ', ' ', ' '],
                      [' ', ' ', ' '],
                      [' ', ' ', ' ']]
        self.history = []
        self.winner = False
        self.draw = False
        self.play_count = 0
        self.remaining_moves = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.winning_states = [[(0, 0), (0, 1), (0, 2)],
                               [(0, 0), (1, 1), (2, 2)],
                               [(1, 0), (1, 1), (1, 2)],
                               [(2, 0), (2, 1), (2, 2)],
                               [(0, 0), (1, 0), (2, 0)],
                               [(0, 1), (1, 1), (2, 1)],
                               [(0, 2), (1, 2), (2, 2)],
                               [(2, 0), (1, 1), (0, 2)]]

    def __repr__(self):
        return f'<TicTacToe Board id="{self.id}">'

    def __str__(self):
        return '┌───┬───┬───┐\n' \
               '│ {0[0][0]} │ {0[0][1]} │ {0[0][2]} │\n' \
               '├───┼───┼───┤\n' \
               '│ {0[1][0]} │ {0[1][1]} │ {0[1][2]} │\n' \
               '├───┼───┼───┤\n' \
               '│ {0[2][0]} │ {0[2][1]} │ {0[2][2]} │\n' \
               '└───┴───┴───┘\n'.format(self.board)

    def make_play(self, player: Player, position: int):
        assert 1 <= position <= 9
        assert isinstance(player, Player)
        move = ((position - 1) // 3, (position - 1) % 3)
        if not self.board[move[0]][move[1]] == ' ':
            raise Warning("That cell is already taken. Please try again.")
        self.history.append(self.board)
        self.board[move[0]][move[1]] = player
        self.play_count += 1
        self.winner = self.check_winner()
        self.draw = self.check_draw()
        self.remaining_moves.remove(position)

    def check_winner(self):
        for state in self.winning_states:
            if (self.board[state[0][0]][state[0][1]] ==
                    self.board[state[1][0]][state[1][1]] ==
                    self.board[state[2][0]][state[2][1]]) and \
                    self.board[state[0][0]][state[0][1]] != ' ':
                return self.board[state[0][0]][state[0][1]]
        return False

    def check_draw(self):
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False
        else:
            return True

    def clear(self):
        self.board = [[' ', ' ', ' '],
                      [' ', ' ', ' '],
                      [' ', ' ', ' ']]
        self.history = []
        self.winner = False
        self.play_count = 0

