# todo: special moves (castle, en passant, promotion)
# todo: draw detection, check detection, checkmate detection
# todo: cloud deployment
# todo: ML chess


import pygame
from pygame.locals import *
from abstractions import *

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('chess')

board = Board(pygame)
white = [Pawn(pygame, x, 6, 'white', board) for x in range(8)] + \
        [King(pygame, 4, 7, 'white', board), Queen(pygame, 3, 7, 'white', board), Rook(pygame, 0, 7, 'white', board),
         Rook(pygame, 7, 7, 'white', board), Knight(pygame, 6, 7, 'white', board), Knight(pygame, 1, 7, 'white', board),
         Bishop(pygame, 2, 7, 'white', board), Bishop(pygame, 5, 7, 'white', board)]
black = [Pawn(pygame, x, 1, 'black', board) for x in range(8)] + \
        [King(pygame, 4, 0, 'black', board), Queen(pygame, 3, 0, 'black', board), Rook(pygame, 0, 0, 'black', board),
         Rook(pygame, 7, 0, 'black', board), Knight(pygame, 6, 0, 'black', board), Knight(pygame, 1, 0, 'black', board),
         Bishop(pygame, 2, 0, 'black', board), Bishop(pygame, 5, 0, 'black', board)]
# white[0].debug = True
white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'), [400, 400])
black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'), [400, 400])
white_play = True


while True:
    screen.blit(board.surface, [0, 0])
    screen.blit(board.dead_surf, [800, 0])
    board.draw_mini()
    screen.blit(board.mini_surf, [800, 400])
    pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 4)
    pygame.draw.line(screen, (0, 0, 0), (800, 400), (1200, 400), 4)

    for piece in board.pieces:
        if piece.dead:
            piece.draw_dead()
        else:
            piece.calc_move()
            if piece.clicked and ((white_play and piece.side == 'white') or (not white_play and piece.side == 'black')):
                pygame.draw.rect(screen, (200, 200, 200), (piece.pos[0] * board.size, piece.pos[1] * board.size, board.size, board.size), 5)
                for move in piece.possible_moves:
                    board.draw_move(pygame, move)
            else:
                piece.clicked = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            for piece in board.pieces:
                if piece.clicked and [event.pos[0] // board.size, event.pos[1] // board.size] in piece.possible_moves:
                    piece.set_target(event.pos[0] // board.size, event.pos[1] // board.size)
                    if white_play:
                        for piece in black:
                            if isinstance(piece, Pawn) and piece.en_passant:
                                piece.en_passant = False
                    else:
                        for piece in white:
                            if isinstance(piece, Pawn) and piece.en_passant:
                                piece.en_passant = False
                    white_play = not white_play
                    piece.clicked = False
                    board.invert_board()
                if piece.figure.collidepoint(event.pos):
                    if ((white_play and piece.side == 'white') or (not white_play and piece.side == 'black')) and not piece.dead:
                        piece.clicked = True
                else:
                    if piece.clicked:
                        board.redraw()
                        piece.clicked = False
    pygame.display.update()
