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
white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'), [400, 400])
black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'), [400, 400])
white_play = True


while True:
    screen.blit(board.surface, [0, 0])
    screen.blit(white_tile, [800, 0])
    screen.blit(black_tile, [800, 400])
    pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 4)

    for piece in board.pieces:
        piece.calc_move()
        if piece.clicked:
            for move in piece.possible_moves:
                board.draw_move(pygame, move)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            for piece in board.pieces:
                if piece.figure.collidepoint(event.pos):
                    piece.clicked = True
                else:
                    piece.clicked = False
    pygame.display.update()
