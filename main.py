import sys
import pygame
from entities.Player import Player
from utils import Methods
from utils.Constants import SCREEN_H, SCREEN_W, GROUND

pygame.init()

SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
pygame.display.set_caption("Castles War")



def main():
    run = True
    pause = True
    loaded = False
    restart = False
    game_over = False
    if not loaded:
        player1, player2 = Player(True), Player(False)
        player1.enemy = player2
        player2.enemy = player1
        game_over = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:

                if game_over:
                    player1, player2 = Player(True), Player(False)
                    player1.enemy = player2
                    player2.enemy = player1

                    game_over = False

                elif loaded:
                    player1, player2 = Player(True), Player(False)
                    player1, player2 = Methods.load(player1, player2)
                    player1.enemy = player2
                    player2.enemy = player1
                    loaded = False

                if not pause:
                    player1.read_command(event.key)
                    player2.read_command(event.key)
                if event.key == pygame.K_SPACE:
                    pause = not pause
                    restart = False
                if event.key == pygame.K_BACKSLASH and pause:
                    Methods.save(player1, player2)
                if event.key == pygame.K_l and pause:
                    loaded = True
                if event.key == pygame.K_r and pause:
                    restart = True


            if event.type == pygame.QUIT:
                run = False
                sys.exit()

        SCREEN.fill((100, 255, 255))
        pygame.draw.rect(SCREEN, (0, 255, 0),
                         pygame.Rect(0, SCREEN_H - GROUND, SCREEN_W, GROUND))

        if not game_over and not pause:
            player1.update()
            player2.update()
            player1.draw(SCREEN)
            player2.draw(SCREEN)
            Methods.draw_labels(player1, SCREEN)
            Methods.draw_labels(player2, SCREEN)
        elif pause:
            player1.draw(SCREEN)
            player2.draw(SCREEN)
            Methods.draw_labels(player1, SCREEN)
            Methods.draw_labels(player2, SCREEN)
            Methods.draw_pause_label(SCREEN)

        if restart:
            player1, player2 = Player(True), Player(False)
            player1.enemy = player2
            player2.enemy = player1
            restart = False

        if player1.wall.health <= 0:
            Methods.game_over("Blue", SCREEN)
            game_over = True
        elif player2.wall.health <= 0:
            Methods.game_over("Red", SCREEN)
            game_over = True

        clock.tick(60)
        pygame.display.update()


if __name__ == '__main__':
    main()
