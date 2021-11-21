import random
from abc import ABC, abstractmethod


class Board:

    def __init__(self, pygame):
        self.pieces = []
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.size = 100
        self.inverted = random.choice([True, False])
        self.surface = pygame.Surface([self.size * 8, self.size * 8])
        self.black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'), [self.size, self.size])
        self.white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'), [self.size, self.size])
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    self.surface.blit(self.white_tile, [x * self.size, y * self.size])
                else:
                    self.surface.blit(self.black_tile, [x * self.size, y * self.size])

    def add_piece(self, piece):
        self.pieces.append(piece)
        piece.inverted = self.inverted
        if self.inverted:
            self.squares[7 - piece.pos[0]][7 - piece.pos[1]] = piece
        else:
            self.squares[piece.pos[0]][piece.pos[1]] = piece

    def invert_board(self):
        for piece in self.pieces:
            piece.pos = [7 - piece.pos[0], 7 - piece.pos[1]]
            piece.inverted = not piece.inverted
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    self.surface.blit(self.white_tile, [x * self.size, y * self.size])
                else:
                    self.surface.blit(self.black_tile, [x * self.size, y * self.size])
        for piece in self.pieces:
            piece.draw()

    def draw_move(self, pygame, move):
        pygame.draw.circle(self.surface,
                         (255, 255, 255),
                         (move[0] * self.size + self.size//2, move[1] * self.size + self.size//2),
                         self.size//8)
        pygame.draw.circle(self.surface,
                         (0, 0, 255),
                         (move[0] * self.size + self.size // 2, move[1] * self.size + self.size // 2),
                         self.size // 8,
                         self.size//25)


class Piece(ABC):

    def __init__(self, pygame, x, y, name, side, point, board):
        self.name = name
        self.side = side
        self.board = board
        self.image = pygame.transform.scale(pygame.image.load('../sprites/{}/{}.png'.format(self.side, self.name)), [self.board.size, self.board.size])
        self.mini_img = pygame.transform.scale(self.image, [self.board.size//4, self.board.size//4])
        self.micro_img = pygame.transform.scale(self.image, [self.board.size//8, self.board.size//8])
        self.point = point
        self.pos = [x, y]
        self.inverted = False
        self.target_pos = [x, y]
        self.num_moves = 0
        self.figure = None
        self.possible_moves = []
        self.clicked = False
        self.init()
        self.draw()
        self.dead = False

    @abstractmethod
    def calc_move(self):
        pass

    def move(self):
        if (self.pos[0] + self.pos[1]) % 2 == 0:
            self.board.surface.blit(self.board.white_tile, [self.pos[0] * self.board.size, self.pos[1] * self.board.size])
        else:
            self.board.surface.blit(self.board.black_tile, [self.pos[0] * self.board.size, self.pos[1] * self.board.size])
        self.pos = self.target_pos.copy()
        self.num_moves += 1
        self.draw()

    def set_target(self, x, y):
        self.target_pos = [x, y]

    def draw(self):
        self.figure = self.board.surface.blit(self.image, [self.pos[0] * self.board.size, self.pos[1] * self.board.size])

    def init(self):
        self.board.add_piece(self)


class Pawn(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'pawn', side, 1, board)

    def calc_move(self):
        self.possible_moves = []
        if self.board.inverted and self.side == 'white':
            if self.inverted:
                self.possible_moves.append([self.pos[0], self.pos[1] - 1])
                if self.num_moves == 0:
                    self.possible_moves.append([self.pos[0], self.pos[1] - 2])
            else:
                self.possible_moves.append([self.pos[0], self.pos[1] + 1])
                if self.num_moves == 0:
                    self.possible_moves.append([self.pos[0], self.pos[1] + 2])
        else:
            if self.inverted:
                self.possible_moves.append([self.pos[0], self.pos[1] + 1])
                if self.num_moves == 0:
                    self.possible_moves.append([self.pos[0], self.pos[1] + 2])
            else:
                self.possible_moves.append([self.pos[0], self.pos[1] - 1])
                if self.num_moves == 0:
                    self.possible_moves.append([self.pos[0], self.pos[1] - 2])
        self.possible_moves = [move for move in self.possible_moves if 0 <= move[0] < 8 and 0 <= move[1] < 8]


class Knight(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'horse', side, 3, board)

    def calc_move(self):
        self.possible_moves = []
        moves = []
        x, y = self.pos
        if x + 2 < 8:
            if y + 1 < 8:
                moves.append([x + 2, y + 1])
            if y - 1 >= 0:
                moves.append([x + 2, y - 1])
        if x - 2 >= 0:
            if y + 1 < 8:
                moves.append([x - 2, y + 1])
            if y - 1 >= 0:
                moves.append([x - 2, y - 1])
        if y + 2 < 8:
            if x + 1 < 8:
                moves.append([x + 1, y + 2])
            if x - 1 >= 0:
                moves.append([x - 1, y + 2])
        if y - 2 >= 0:
            if x + 1 < 8:
                moves.append([x + 1, y - 2])
            if x - 1 >= 0:
                moves.append([x - 1, y - 2])
        for move in moves:
            if self.inverted:
                piece = self.board.squares[7 - move[0]][7 - move[1]]
            else:
                piece = self.board.squares[move[0]][move[1]]
            if piece is None or (piece is not None and piece.side != self.side):
                self.possible_moves.append(move)


class Bishop(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'bishop', side, 3, board)

    def calc_move(self):
        self.possible_moves = []
        moves = []
        x, y = self.pos
        while y < 8 and x < 8:
            if x != self.pos[0] and y != self.pos[1]:
                moves.append([x, y])
            x += 1
            y += 1
        for n in range(len(moves)):
            move = moves[n]
            if self.inverted:
                piece = self.board.squares[7 - move[0]][7 - move[1]]
            else:
                piece = self.board.squares[move[0]][move[1]]
            if piece is not None:
                if piece.side == self.side:
                    self.possible_moves += moves[:n]
                else:
                    self.possible_moves += moves[:n+1]
                moves = []
                break
        x, y = self.pos
        while y >= 0 and x < 8:
            if x != self.pos[0] and y != self.pos[1]:
                moves.append([x, y])
            x += 1
            y -= 1
        for n in range(len(moves)):
            move = moves[n]
            if self.inverted:
                piece = self.board.squares[7 - move[0]][7 - move[1]]
            else:
                piece = self.board.squares[move[0]][move[1]]
            if piece is not None:
                if piece.side == self.side:
                    self.possible_moves += moves[:n]
                else:
                    self.possible_moves += moves[:n+1]
                moves = []
                break
        x, y = self.pos
        while y < 8 and x >= 0:
            if x != self.pos[0] and y != self.pos[1]:
                moves.append([x, y])
            x -= 1
            y += 1
        for n in range(len(moves)):
            move = moves[n]
            if self.inverted:
                piece = self.board.squares[7 - move[0]][7 - move[1]]
            else:
                piece = self.board.squares[move[0]][move[1]]
            if piece is not None:
                if piece.side == self.side:
                    self.possible_moves += moves[:n]
                else:
                    self.possible_moves += moves[:n+1]
                moves = []
                break
        x, y = self.pos
        while y >= 0 and x >= 0:
            if x != self.pos[0] and y != self.pos[1]:
                moves.append([x, y])
            x -= 1
            y -= 1
        for n in range(len(moves)):
            move = moves[n]
            if self.inverted:
                piece = self.board.squares[7 - move[0]][7 - move[1]]
            else:
                piece = self.board.squares[move[0]][move[1]]
            if piece is not None:
                if piece.side == self.side:
                    self.possible_moves += moves[:n]
                else:
                    self.possible_moves += moves[:n+1]
                moves = []
                break


class Rook(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'rook', side, 5, board)

    def calc_move(self):
        self.possible_moves = []
        x, y = self.pos
        while x >= 0:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            x -= 1
        x, y = self.pos
        while x < 8:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            x += 1
        x, y = self.pos
        while y >= 0:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            y -= 1
        x, y = self.pos
        while y < 8:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            y += 1


class Queen(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'queen', side, 9, board)

    def calc_move(self):
        self.possible_moves = []
        x, y = self.pos
        while x >= 0:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            x -= 1
        x, y = self.pos
        while x < 8:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            x += 1
        x, y = self.pos
        while y >= 0:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            y -= 1
        x, y = self.pos
        while y < 8:
            if not (x == self.pos[0] and y == self.pos[1]):
                self.possible_moves.append([x, y])
            y += 1
        x, y = self.pos
        while y < 8 and x < 8:
            if x != self.pos[0] and y != self.pos[1]:
                self.possible_moves.append([x, y])
            x += 1
            y += 1
        x, y = self.pos
        while y >= 0 and x < 8:
            if x != self.pos[0] and y != self.pos[1]:
                self.possible_moves.append([x, y])
            x += 1
            y -= 1
        x, y = self.pos
        while y < 8 and x >= 0:
            if x != self.pos[0] and y != self.pos[1]:
                self.possible_moves.append([x, y])
            x -= 1
            y += 1
        x, y = self.pos
        while y >= 0 and x >= 0:
            if x != self.pos[0] and y != self.pos[1]:
                self.possible_moves.append([x, y])
            x -= 1
            y -= 1


class King(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'king', side, 10000, board)

    def calc_move(self):
        self.possible_moves = []
        x, y = self.pos
        xs, ys = [x - 1, x, x + 1], [y - 1, y, y + 1]
        xs, ys = [n for n in xs if 0 <= n < 8], [n for n in ys if 0 <= n < 8]
        for i in xs:
            for j in ys:
                if not (i == x and j == y):
                    self.possible_moves.append([i, j])
