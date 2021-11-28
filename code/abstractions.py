import math
import random
from abc import ABC, abstractmethod


class Board:

    def __init__(self, pygame):
        self.pieces = []
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.size = 100
        self.inverted = random.choice([True, False])
        self.surface = pygame.Surface([self.size * 8, self.size * 8])
        self.blank_board = pygame.Surface([self.size * 8, self.size * 8])
        self.black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'), [self.size, self.size])
        self.white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'), [self.size, self.size])
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    self.blank_board.blit(self.white_tile, [x * self.size, y * self.size])
                else:
                    self.blank_board.blit(self.black_tile, [x * self.size, y * self.size])
        self.surface.blit(self.blank_board, [0, 0])
        if self.inverted:
            self.invert_board()
        self.mini_blank = pygame.transform.scale(self.blank_board, [self.size * 4, self.size * 4])
        self.mini_surf = pygame.Surface([self.size * 4, self.size * 4])
        self.dead_surf = pygame.Surface([self.size * 4, self.size * 4])
        self.dead_surf.blit(self.mini_blank, [0, 0])

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
        self.surface.blit(self.blank_board, [0, 0])
        for piece in self.pieces:
            piece.draw()

    def redraw(self):
        self.surface.blit(self.blank_board, [0, 0])
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

    def draw_mini(self):
        self.mini_surf.blit(self.mini_blank, [0, 0])
        for x in self.squares:
            for y in x:
                if y is not None:
                    if y.inverted:
                        self.mini_surf.blit(y.mini_img, [(7 - y.pos[0]) * self.size // 2, (7 - y.pos[1]) * self.size // 2])
                    else:
                        self.mini_surf.blit(y.mini_img, [y.pos[0] * self.size // 2, y.pos[1] * self.size // 2])


class Piece(ABC):

    def __init__(self, pygame, x, y, name, side, point, board):
        self.name = name
        self.side = side
        self.board = board
        self.image = pygame.transform.scale(pygame.image.load('../sprites/{}/{}.png'.format(self.side, self.name)), [self.board.size, self.board.size])
        self.mini_img = pygame.transform.scale(self.image, [self.board.size//2, self.board.size//2])
        self.point = point
        self.pos = [x, y]
        self.initial_pos = [x, y]
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
        if self.inverted:
            piece = self.board.squares[7 - self.target_pos[0]][7 - self.target_pos[1]]
            if piece is not None:
                piece.die()
            self.board.squares[7 - self.target_pos[0]][7 - self.target_pos[1]] = self
            self.board.squares[7 - self.pos[0]][7 - self.pos[1]] = None
        else:
            piece = self.board.squares[self.target_pos[0]][self.target_pos[1]]
            if piece is not None:
                piece.die()
            self.board.squares[self.target_pos[0]][self.target_pos[1]] = self
            self.board.squares[self.pos[0]][self.pos[1]] = None
        self.pos = self.target_pos.copy()
        self.num_moves += 1
        self.draw()

    def draw_dead(self):
        self.board.dead_surf.blit(self.mini_img, [self.initial_pos[0] * self.board.size // 2, self.initial_pos[1] * self.board.size // 2])

    def set_target(self, x, y):
        self.target_pos = [x, y]
        self.move()

    def draw(self):
        self.figure = self.board.surface.blit(self.image, [self.pos[0] * self.board.size, self.pos[1] * self.board.size])

    def init(self):
        self.board.add_piece(self)

    def die(self):
        self.pos = [-1, -1]
        self.dead = True
        self.board.redraw()

    def calc_trajectory(self, path):
        output = []
        if path == 'vt':
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while y < 7:
                y += 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while y > 0:
                y -= 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
        elif path == 'hz':
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x < 7:
                x += 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x > 0:
                x -= 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
        else:
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x < 7 and y < 7:
                x += 1
                y += 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x < 7 and y > 0:
                x += 1
                y -= 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x > 0 and y < 7:
                x -= 1
                y += 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
            if self.inverted:
                x, y = 7 - self.pos[0], 7 - self.pos[1]
            else:
                x, y = self.pos
            while x > 0 and y > 0:
                x -= 1
                y -= 1
                piece = self.board.squares[x][y]
                if piece is None:
                    output.append([x, y])
                else:
                    if piece.side != self.side:
                        output.append([x, y])
                    break
        if self.inverted:
            for i in range(len(output)):
                output[i] = [7 - output[i][0], 7 - output[i][1]]
        return output


class Pawn(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'pawn', side, 1, board)
        self.en_passant = False
        self.dist_calc = lambda x1, y1, x2, y2: math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def move(self):
        if abs(self.target_pos[1] - self.pos[1]) == 2 and self.num_moves == 0:
            self.en_passant = True
        super().move()

    def calc_move(self):
        self.possible_moves = []
        if self.side == 'white':
            if self.inverted == self.board.inverted:
                if self.inverted:
                    pos = [7 - self.pos[0], 7 - self.pos[1]]
                else:
                    pos = self.pos.copy()
                if pos[0] + 1 < 8:
                    piece = self.board.squares[pos[0] + 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] + 1, pos[1] - 1]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - move[1]])
                        else:
                            self.possible_moves.append([move[0], move[1]])
                if pos[0] - 1 >= 0:
                    piece = self.board.squares[pos[0] - 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] - 1, pos[1] - 1]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - move[1]])
                        else:
                            self.possible_moves.append([move[0], move[1]])
                if self.inverted:
                    move = [7 - self.pos[0], 7 - (self.pos[1] - 1)]
                else:
                    move = [self.pos[0], self.pos[1] - 1]
                if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                    piece = self.board.squares[move[0]][move[1]]
                    if piece is None:
                        self.possible_moves.append([self.pos[0], self.pos[1] - 1])
                        if self.num_moves == 0:
                            if self.inverted:
                                move = [7 - self.pos[0], 7 - (self.pos[1] - 2)]
                            else:
                                move = [self.pos[0], self.pos[1] - 2]
                            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                                piece = self.board.squares[move[0]][move[1]]
                                if piece is None:
                                    self.possible_moves.append([self.pos[0], self.pos[1] - 2])
                    if self.inverted:
                        move[1] = 7 - (self.pos[1] - 1)
                    else:
                        move[1] = self.pos[1] - 1
                    move = [move[0] - 1, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] - 1])
                            else:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] - 1])
                    move = [move[0] + 2, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] - 1])
                            else:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] - 1])
            else:
                if self.inverted:
                    pos = [7 - self.pos[0], 7 - self.pos[1]]
                else:
                    pos = self.pos.copy()
                if pos[0] + 1 < 8:
                    piece = self.board.squares[pos[0] + 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] + 1, pos[1] + 1]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - move[1]])
                        else:
                            self.possible_moves.append([move[0], move[1]])
                if pos[0] - 1 >= 0:
                    piece = self.board.squares[pos[0] - 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] - 1, pos[1] + 1]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - move[1]])
                        else:
                            self.possible_moves.append([move[0], move[1]])
                if self.inverted:
                    move = [7 - self.pos[0], 7 - (self.pos[1] + 1)]
                else:
                    move = [self.pos[0], self.pos[1] + 1]
                if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                    piece = self.board.squares[move[0]][move[1]]
                    if piece is None:
                        self.possible_moves.append([self.pos[0], self.pos[1] + 1])
                        if self.num_moves == 0:
                            if self.inverted:
                                move = [7 - self.pos[0], 7 - (self.pos[1] + 2)]
                            else:
                                move = [self.pos[0], self.pos[1] + 2]
                            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                                piece = self.board.squares[move[0]][move[1]]
                                if piece is None:
                                    self.possible_moves.append([self.pos[0], self.pos[1] + 2])
                    if self.inverted:
                        move[1] = 7 - (self.pos[1] + 1)
                    else:
                        move[1] = self.pos[1] + 1
                    move = [move[0] - 1, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] + 1])
                            else:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] + 1])
                    move = [move[0] + 2, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] + 1])
                            else:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] + 1])
        else:
            if self.inverted:
                pos = [7 - self.pos[0], 7 - self.pos[1]]
            else:
                pos = self.pos.copy()
            if pos[0] + 1 < 8:
                piece = self.board.squares[pos[0] + 1][pos[1]]
                if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                    move = [pos[0] + 1, pos[1] + 1]
                    if self.inverted:
                        self.possible_moves.append([7 - move[0], 7 - move[1]])
                    else:
                        self.possible_moves.append([move[0], move[1]])
            if pos[0] - 1 >= 0:
                piece = self.board.squares[pos[0] - 1][pos[1]]
                if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                    move = [pos[0] - 1, pos[1]]
                    if self.inverted:
                        self.possible_moves.append([7 - move[0], 7 - move[1]])
                    else:
                        self.possible_moves.append([move[0], move[1]])
            if self.inverted == self.board.inverted:
                if self.inverted:
                    move = [7 - self.pos[0], 7 - (self.pos[1] + 1)]
                else:
                    move = [self.pos[0], self.pos[1] + 1]
                if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                    piece = self.board.squares[move[0]][move[1]]
                    if piece is None:
                        self.possible_moves.append([self.pos[0], self.pos[1] + 1])
                        if self.num_moves == 0:
                            if self.inverted:
                                move = [7 - self.pos[0], 7 - (self.pos[1] + 2)]
                            else:
                                move = [self.pos[0], self.pos[1] + 2]
                            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                                piece = self.board.squares[move[0]][move[1]]
                                if piece is None:
                                    self.possible_moves.append([self.pos[0], self.pos[1] + 2])
                    if self.inverted:
                        move[1] = 7 - (self.pos[1] + 1)
                    else:
                        move[1] = self.pos[1] + 1
                    move = [move[0] - 1, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] + 1])
                            else:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] + 1])
                    move = [move[0] + 2, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] + 1])
                            else:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] + 1])
            else:
                if self.inverted:
                    pos = [7 - self.pos[0], 7 - self.pos[1]]
                else:
                    pos = self.pos.copy()
                if pos[0] + 1 < 8:
                    piece = self.board.squares[pos[0] + 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] + 1, pos[1] - 1]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - move[1]])
                        else:
                            self.possible_moves.append([move[0], move[1]])
                if pos[0] - 1 >= 0:
                    piece = self.board.squares[pos[0] - 1][pos[1]]
                    if piece is not None and piece.side != self.side and isinstance(piece, Pawn) and piece.en_passant:
                        move = [pos[0] - 1, pos[1]]
                        if self.inverted:
                            self.possible_moves.append([7 - move[0], 7 - (move[1] - 1)])
                        else:
                            self.possible_moves.append([move[0], move[1] - 1])
                if self.inverted:
                    move = [7 - self.pos[0], 7 - (self.pos[1] - 1)]
                else:
                    move = [self.pos[0], self.pos[1] - 1]
                if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                    piece = self.board.squares[move[0]][move[1]]
                    if piece is None:
                        self.possible_moves.append([self.pos[0], self.pos[1] - 1])
                        if self.num_moves == 0:
                            if self.inverted:
                                move = [7 - self.pos[0], 7 - (self.pos[1] - 2)]
                            else:
                                move = [self.pos[0], self.pos[1] - 2]
                            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                                piece = self.board.squares[move[0]][move[1]]
                                if piece is None:
                                    self.possible_moves.append([self.pos[0], self.pos[1] - 2])
                    if self.inverted:
                        move[1] = 7 - (self.pos[1] - 1)
                    else:
                        move[1] = self.pos[1] - 1
                    move = [move[0] - 1, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] - 1])
                            else:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] - 1])
                    move = [move[0] + 2, move[1]]
                    if 0 <= move[0] < 8:
                        piece = self.board.squares[move[0]][move[1]]
                        if piece is not None and piece.side != self.side:
                            if self.inverted:
                                self.possible_moves.append([self.pos[0] - 1, self.pos[1] - 1])
                            else:
                                self.possible_moves.append([self.pos[0] + 1, self.pos[1] - 1])
        self.possible_moves = [move for move in self.possible_moves if 0 <= move[0] < 8 and 0 <= move[1] < 8]

    def set_target(self, x, y):
        if abs(y - self.pos[1]) == 2:
            self.en_passant = True
        else:
            self.en_passant = False
        print(self.en_passant)
        super().set_target(x, y)


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
        self.possible_moves = self.calc_trajectory('dg').copy()


class Rook(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'rook', side, 5, board)

    def calc_move(self):
        self.possible_moves = self.calc_trajectory('vt').copy() + self.calc_trajectory('hz').copy()


class Queen(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'queen', side, 9, board)

    def calc_move(self):
        self.possible_moves = self.calc_trajectory('vt').copy() + self.calc_trajectory('hz').copy() + self.calc_trajectory('dg').copy()


class King(Piece):

    def __init__(self, pygame, x, y, side, board):
        super().__init__(pygame, x, y, 'king', side, 10000, board)

    def calc_move(self):
        self.possible_moves = []
        moves = []
        x, y = self.pos
        xs, ys = [x - 1, x, x + 1], [y - 1, y, y + 1]
        xs, ys = [n for n in xs if 0 <= n < 8], [n for n in ys if 0 <= n < 8]
        for i in xs:
            for j in ys:
                if not (i == x and j == y):
                    moves.append([i, j])
        for i in range(len(moves)):
            move = [moves[i][0], moves[i][1]]
            if self.inverted:
                move = [7 - move[0], 7 - move[1]]
            piece = self.board.squares[move[0]][move[1]]
            if piece is None or piece.side != self.side:
                self.possible_moves.append(moves[i])
