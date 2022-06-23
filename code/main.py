from abstractions import *

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('Chess')

board = Board(screen)
board.calc_moves()
turn = 'white'
selected = None
white_tile = pygame.transform.scale(pygame.image.load('../sprites/board/white_tile.png'), [400, 400])
black_tile = pygame.transform.scale(pygame.image.load('../sprites/board/black_tile.png'), [400, 400])

while True:
    board.draw()
    if selected is not None:
        selected.draw_moves()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if selected is None:
                for piece in board.pieces:
                    if piece.rect.collidepoint(event.pos) and piece.color == turn and piece.alive and not (type(piece) == Pawn and piece.promoted):
                        selected = piece
                        break
            else:
                pos = [event.pos[0] // board.scale, event.pos[1] // board.scale]
                if pos in selected.possible_moves:
                    # todo: move method to commit to move
                    selected.move(pos)
                    if turn == 'white':
                        turn = 'black'
                    else:
                        turn = 'white'
                    board.calc_moves()
                    selected = None
                else:
                    selected = None
            if board.promote is not None:
                for index, button in enumerate(board.promo_buttons):
                    if button.rect.collidepoint(event.pos):
                        board.promotion(index)
    pygame.display.update()
