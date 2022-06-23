import pygame
from pygame.locals import *
from abc import ABC, abstractmethod


# calculate king threats method - replace None or any other object with current object. use calc_moves for each
# opposing piece to see if king is in check. todo: modify calc_moves method to incorporate different board for
#  different test scenarios

# if the side playing has the other side's king's position in the possible moves, then its a checkmate
# OR if the side cannot play a legal move, it's a checkmate

# todo: special moves (castle, en passant, promotion)
# todo: graphics and event processing for an inverted board. without changing program logic
# todo: draw detection, check detection, checkmate detection
# todo: cloud deployment with flask server intermediate
# todo: ML chess

# draw rules: trifold repetition, insufficient material

# code plan:
# 1. develop move method and full UI
# 2. enhance special moves
# 3. implement draw, check, checkmate detection
# 4. board inversion


def show_text(window, text, x, y, size=32, color=(255, 255, 255)):
    font_obj = pygame.font.SysFont('courier new', size)
    window.blit(font_obj.render(text, False, color), [x, y])


class Button:

    def __init__(self, window, text, x, y, color=(0, 0, 0), width=150, height=45):
        self.text = text
        self.pos = [x, y]
        self.color = color
        self.dims = [width, height]
        self.rect = None
        self.window = window

    def draw(self):
        self.rect = pygame.draw.rect(self.window, self.color, self.pos + self.dims)
        show_text(self.window, self.text, self.pos[0] + 5, self.pos[1] + 5)


class Board:

    def __init__(self, screen, scale=100):
        self.scale = scale
        self.screen = screen
        self.white_pieces = [Pawn(self, x, 6, 'white') for x in range(8)] + [Rook(self, 0, 7, 'white'),
                                                                             Rook(self, 7, 7, 'white'),
                                                                             Knight(self, 1, 7, 'white'),
                                                                             Knight(self, 6, 7, 'white'),
                                                                             Bishop(self, 2, 7, 'white'),
                                                                             Bishop(self, 5, 7, 'white'),
                                                                             Queen(self, 3, 7, 'white'),
                                                                             King(self, 4, 7, 'white')]
        self.black_pieces = [Pawn(self, x, 1, 'black') for x in range(8)] + [Rook(self, 0, 0, 'black'),
                                                                             Rook(self, 7, 0, 'black'),
                                                                             Knight(self, 1, 0, 'black'),
                                                                             Knight(self, 6, 0, 'black'),
                                                                             Bishop(self, 2, 0, 'black'),
                                                                             Bishop(self, 5, 0, 'black'),
                                                                             Queen(self, 3, 0, 'black'),
                                                                             King(self, 4, 0, 'black')]
        self.pieces = self.black_pieces + self.white_pieces
        self.points = {'white': 0, 'black': 0}
        self.white_moves = []
        self.black_moves = []
        self.promote = None
        self.promo_buttons = [
            Button(self.screen, 'Queen', self.scale * 8 // 2 - 75, self.scale * 8 // 2 - 100),
            Button(self.screen, 'Rook', self.scale * 8 // 2 - 75, self.scale * 8 // 2 - 50),
            Button(self.screen, 'Bishop', self.scale * 8 // 2 - 75, self.scale * 8 // 2),
            Button(self.screen, 'Knight', self.scale * 8 // 2 - 75, self.scale * 8 // 2 + 50)
        ]
        self.button_order = [Queen, Rook, Bishop, Knight]
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        for piece in self.pieces:
            self.squares[piece.pos[0]][piece.pos[1]] = piece
        self.white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'),
                                                 [self.scale, self.scale])
        self.black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'),
                                                 [self.scale, self.scale])
        self.big_white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'),
                                                     [self.scale * 4, self.scale * 4])
        self.big_black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'),
                                                     [self.scale * 4, self.scale * 4])
        self.surface = pygame.Surface([self.scale * 8, self.scale * 8])
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    self.surface.blit(self.white_tile, [x * self.scale, y * self.scale])
                else:
                    self.surface.blit(self.black_tile, [x * self.scale, y * self.scale])

    def draw(self):
        self.screen.blit(self.surface, [0, 0])
        self.screen.blit(self.big_white_tile, [self.scale * 8, 0])
        self.screen.blit(self.big_black_tile, [self.scale * 8, self.scale * 4])
        pygame.draw.line(self.screen, (0, 0, 0), (self.scale * 8, 0), (self.scale * 8, self.scale * 8), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (self.scale * 8, self.scale * 4), (self.scale * 12, self.scale * 4), 2)
        show_text(self.screen, 'white points: {}'.format(self.points['white']), self.scale * 8.25, self.scale / 3, size=24, color=(0, 0, 0))
        show_text(self.screen, 'black points: {}'.format(self.points['black']), self.scale * 8.25, self.scale * 3, size=24, color=(0, 0, 0))
        for piece in self.pieces:
            if piece.alive and isinstance(piece, Pawn) and not piece.promoted:
                if piece.color == 'white' and piece.pos[1] == 0 or piece.color == 'black' and piece.pos[1] == 7:
                    self.promote = piece
            piece.draw()
        if self.promote is not None:
            for button in self.promo_buttons:
                button.draw()

    def calc_moves(self):
        self.white_moves = []
        self.black_moves = []
        for piece in self.white_pieces:
            piece.calc_moves()
            self.white_moves += piece.possible_moves
        for piece in self.black_pieces:
            piece.calc_moves()
            self.black_moves += piece.possible_moves

    def promotion(self, index):
        self.promote.promoted = True
        replacement = self.button_order[index](self, self.promote.pos[0], self.promote.pos[1], self.promote.color)
        replacement.original = self.promote
        self.squares[self.promote.pos[0]][self.promote.pos[1]] = replacement
        if self.promote.color == 'white':
            self.white_pieces.append(replacement)
        else:
            self.black_pieces.append(replacement)
        self.pieces.append(replacement)
        self.promote = None


class Piece(ABC):

    def __init__(self, board, x, y, color, piece):
        self.board = board
        self.possible_moves = []
        self.pos = [x, y]
        self.color = color
        self.piece = piece
        self.image = pygame.transform.scale(pygame.image.load('../sprites/{}/{}.png'.format(self.color, self.piece)),
                                            [self.board.scale,
                                             self.board.scale])  # [int(self.board.scale * 0.8), int(self.board.scale * 0.8)])
        self.dead_image = pygame.transform.scale(
            pygame.image.load('../sprites/{}/{}.png'.format(self.color, self.piece)),
            [self.board.scale // 2, self.board.scale // 2])
        self.dead_pos = [x, y]
        if y == 0:
            self.dead_pos[1] = 3
        elif y == 1:
            self.dead_pos[1] = 2
        elif y == 6:
            self.dead_pos[1] = 1
        else:
            self.dead_pos[1] = 0
        self.rect = None
        self.points = 0
        self.alive = True
        self.original = None

    def move(self, target):
        if target in self.possible_moves:
            if self.board.squares[target[0]][target[1]] is not None:
                self.board.squares[target[0]][target[1]].alive = False
                if self.board.squares[target[0]][target[1]].original is not None:
                    self.board.squares[target[0]][target[1]].original.alive = False
                    self.board.points[self.color] += self.board.squares[target[0]][target[1]].original.points
                else:
                    self.board.points[self.color] += self.board.squares[target[0]][target[1]].points
                # self.board.squares[move[0]][move[1]].alive = False
            self.board.squares[target[0]][target[1]] = self
            self.board.squares[self.pos[0]][self.pos[1]] = None
            self.pos = target
            if self.color == 'white':
                for piece in self.board.black_pieces:
                    if isinstance(piece, Pawn):
                        piece.en_passant = False
            else:
                for piece in self.board.white_pieces:
                    if isinstance(piece, Pawn):
                        piece.en_passant = False

    def draw(self):
        if self.alive:
            self.rect = self.board.screen.blit(self.image,
                                               [self.board.scale * self.pos[0], self.board.scale * self.pos[1]])
        else:
            if self.original is None:
                self.board.screen.blit(self.dead_image, [self.dead_pos[0] * self.board.scale / 2 + self.board.scale * 8,
                                                     self.dead_pos[1] * self.board.scale / 2 + self.board.scale / 2])

    @abstractmethod
    def calc_moves(self):
        pass

    def draw_moves(self):
        pygame.draw.rect(self.board.screen, (200, 200, 200), (
        self.pos[0] * self.board.scale, self.pos[1] * self.board.scale, self.board.scale, self.board.scale), 4)
        for move in self.possible_moves:
            pygame.draw.circle(self.board.screen, (255, 255, 255), (
                move[0] * self.board.scale + self.board.scale / 2, move[1] * self.board.scale + self.board.scale / 2),
                               10)
            pygame.draw.circle(self.board.screen, (0, 0, 255), (
                move[0] * self.board.scale + self.board.scale / 2, move[1] * self.board.scale + self.board.scale / 2),
                               10, 2)

    def calc_vertical(self):
        y = self.pos[1] - 1
        while y >= 0:
            tgt = [self.pos[0], y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            y -= 1
        y = self.pos[1] + 1
        while y < 8:
            tgt = [self.pos[0], y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            y += 1

    def calc_horizontal(self):
        x = self.pos[0] - 1
        while x >= 0:
            tgt = [x, self.pos[1]]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x -= 1
        x = self.pos[0] + 1
        while x < 8:
            tgt = [x, self.pos[1]]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x += 1

    def calc_diagonal(self):
        x = self.pos[0] - 1
        y = self.pos[1] - 1
        while x >= 0 and y >= 0:
            tgt = [x, y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x -= 1
            y -= 1
        x = self.pos[0] + 1
        y = self.pos[1] - 1
        while x < 8 and y >= 0:
            tgt = [x, y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x += 1
            y -= 1
        x = self.pos[0] - 1
        y = self.pos[1] + 1
        while x >= 0 and y < 8:
            tgt = [x, y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x -= 1
            y += 1
        x = self.pos[0] + 1
        y = self.pos[1] + 1
        while x < 8 and y < 8:
            tgt = [x, y]
            if self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            elif self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
                break
            else:
                break
            x += 1
            y += 1


class Pawn(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'pawn')
        self.moved = False
        self.en_passant = False
        self.points = 1
        self.promoted = False

    def calc_moves(self):
        self.possible_moves = []
        if self.color == 'white':
            # 1 step forward
            tgt = [self.pos[0], self.pos[1] - 1]
            if 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            # 2 step forward
            if not self.moved and self.board.squares[tgt[0]][tgt[1] - 1] is None:
                self.possible_moves.append([tgt[0], tgt[1] - 1])
            # kill
            tgt = [self.pos[0] - 1, self.pos[1] - 1]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
            tgt = [self.pos[0] + 1, self.pos[1] - 1]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
            # en passant capture
            # todo: currently just moves sideways (to make kills easier to register). add checks for diagonal
            tgt = [self.pos[0] - 1, self.pos[1]]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color and \
                    self.board.squares[tgt[0]][tgt[1]].piece == 'pawn' and self.board.squares[tgt[0]][
                tgt[1]].en_passant and self.board.squares[tgt[0]][tgt[1] - 1] is None:
                # self.possible_moves.append(tgt)
                self.possible_moves.append([tgt[0], tgt[1] - 1])
            tgt = [self.pos[0] + 1, self.pos[1]]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color and \
                    self.board.squares[tgt[0]][tgt[1]].piece == 'pawn' and self.board.squares[tgt[0]][
                tgt[1]].en_passant and self.board.squares[tgt[0]][tgt[1] - 1] is None:
                # self.possible_moves.append(tgt)
                self.possible_moves.append([tgt[0], tgt[1] - 1])
        else:
            # 1 step forward
            tgt = [self.pos[0], self.pos[1] + 1]
            if 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is None:
                self.possible_moves.append(tgt)
            # 2 step forward
            if not self.moved and self.board.squares[tgt[0]][tgt[1] + 1] is None:
                self.possible_moves.append([tgt[0], tgt[1] + 1])
            # kill
            tgt = [self.pos[0] - 1, self.pos[1] + 1]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
            tgt = [self.pos[0] + 1, self.pos[1] + 1]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color:
                self.possible_moves.append(tgt)
            # en passant capture
            # todo: currently just moves sideways (to make kills easier to register). add checks for diagonal
            tgt = [self.pos[0] - 1, self.pos[1]]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color and \
                    self.board.squares[tgt[0]][tgt[1]].piece == 'pawn' and self.board.squares[tgt[0]][
                tgt[1]].en_passant and self.board.squares[tgt[0]][tgt[1] + 1] is None:
                # self.possible_moves.append(tgt)
                self.possible_moves.append([tgt[0], tgt[1] + 1])
            tgt = [self.pos[0] + 1, self.pos[1]]
            if 0 <= tgt[0] < 8 and 0 <= tgt[1] < 8 and self.board.squares[tgt[0]][tgt[1]] is not None and \
                    self.board.squares[tgt[0]][tgt[1]].color != self.color and \
                    self.board.squares[tgt[0]][tgt[1]].piece == 'pawn' and self.board.squares[tgt[0]][
                tgt[1]].en_passant and self.board.squares[tgt[0]][tgt[1] + 1] is None:
                # self.possible_moves.append(tgt)
                self.possible_moves.append([tgt[0], tgt[1] + 1])

    def move(self, target):
        pos = self.pos.copy()
        current = self.board.squares[target[0]][target[1]]
        super().move(target)
        if abs(target[1] - pos[1]) == 2:
            self.en_passant = True
        elif abs(target[0] - pos[0]) == 1 and abs(target[1] - pos[1]) == 1 and current is None:
            if self.color == 'white':
                self.board.squares[target[0]][target[1] + 1].alive = False
                self.board.points['white'] += 1
                self.board.squares[target[0]][target[1] + 1] = None
            else:
                self.board.squares[target[0]][target[1] - 1].alive = False
                self.board.points['black'] += 1
                self.board.squares[target[0]][target[1] - 1] = None
        self.moved = True

    def draw(self):
        if not self.promoted:
            super().draw()


class Knight(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'knight')
        self.points = 3

    def calc_moves(self):
        self.possible_moves = []
        tgt_xs = [self.pos[0] - 2, self.pos[0] - 1, self.pos[0] + 1, self.pos[0] + 2]
        tgt_ys = [self.pos[1] - 2, self.pos[1] - 1, self.pos[1] + 1, self.pos[1] + 2]
        for x in tgt_xs:
            if 0 <= x < 8:
                for y in tgt_ys:
                    if 0 <= y < 8 and abs(abs(self.pos[0] - x) + abs(self.pos[1] - y)) == 3:
                        if self.board.squares[x][y] is None or self.board.squares[x][y].color != self.color:
                            self.possible_moves.append([x, y])


class Bishop(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'bishop')
        self.points = 3

    def calc_moves(self):
        self.possible_moves = []
        self.calc_diagonal()


class Rook(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'rook')
        self.moved = False
        self.points = 5

    def calc_moves(self):
        self.possible_moves = []
        self.calc_vertical()
        self.calc_horizontal()

    def move(self, target, castle=False):
        if castle:
            self.possible_moves.append(target)
        super().move(target)
        self.moved = True


class Queen(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'queen')
        self.points = 9

    def calc_moves(self):
        self.possible_moves = []
        self.calc_vertical()
        self.calc_horizontal()
        self.calc_diagonal()


class King(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, 'king')
        self.moved = False

    def move(self, target):
        if abs(self.pos[0] - target[0]) == 2:
            if self.pos[0] > target[0]:
                self.board.squares[0][self.pos[1]].move([target[0] + 1, target[1]], castle=True)
            else:
                self.board.squares[7][self.pos[1]].move([target[0] - 1, target[1]], castle=True)
        super().move(target)
        self.moved = True

    def calc_moves(self):
        self.possible_moves = []
        tgt_xs = [self.pos[0] - 1, self.pos[0], self.pos[0] + 1]
        tgt_ys = [self.pos[1] - 1, self.pos[1], self.pos[1] + 1]
        for x in tgt_xs:
            if 0 <= x < 8:
                for y in tgt_ys:
                    if 0 <= y < 8 and not (x == self.pos[0] and y == self.pos[1]):
                        if self.board.squares[x][y] is None or self.board.squares[x][y].color != self.color:
                            self.possible_moves.append([x, y])
        # castling
        # todo: ensure that threats on the way are accounted for
        if self.color == 'white':
            for piece in self.board.white_pieces:
                if isinstance(piece, Rook):
                    if not self.moved and not piece.moved:
                        can_castle = True
                        if piece.pos[0] > self.pos[0]:
                            x = piece.pos[0] - 1
                            while x > self.pos[0]:
                                if self.board.squares[x][self.pos[1]] is not None:
                                    can_castle = False
                                    break
                                x -= 1
                            if can_castle:
                                self.possible_moves.append([self.pos[0] + 2, self.pos[1]])
                        else:
                            x = piece.pos[0] + 1
                            while x < self.pos[0]:
                                if self.board.squares[x][self.pos[1]] is not None:
                                    can_castle = False
                                    break
                                x += 1
                            if can_castle:
                                self.possible_moves.append([self.pos[0] - 2, self.pos[1]])
        else:
            for piece in self.board.black_pieces:
                if isinstance(piece, Rook):
                    if not self.moved and not piece.moved:
                        can_castle = True
                        if piece.pos[0] > self.pos[0]:
                            x = piece.pos[0] - 1
                            while x > self.pos[0]:
                                if self.board.squares[x][self.pos[1]] is not None:
                                    can_castle = False
                                    break
                                x -= 1
                            if can_castle:
                                self.possible_moves.append([self.pos[0] + 2, self.pos[1]])
                        else:
                            x = piece.pos[0] + 1
                            while x < self.pos[0]:
                                if self.board.squares[x][self.pos[1]] is not None:
                                    can_castle = False
                                    break
                                x += 1
                            if can_castle:
                                self.possible_moves.append([self.pos[0] - 2, self.pos[1]])
