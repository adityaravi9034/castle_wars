import pygame

import entities.Player
from entities.Units import SwordsMan, Worker, Archer, Arrow
from utils.Constants import SCREEN_W, SCREEN_H


pygame.init()


def units_update(player):
    for unit in player.military_units:
        unit.update(player.targeted_unit, player.enemy.military_units)

    for worker in player.wall_workers:
        worker.update(player.wall, player.mine)

    for worker in player.mine_workers:
        worker.update(player.wall, player.mine)


def building_update(player):
    player.barrack.update()
    player.tower.update(player.targeted_unit, player.enemy.military_units, player.military_units)


def draw_building(player, screen):
    player.barrack.draw(screen)
    player.tower.draw(screen)
    player.mine.draw(screen)
    player.wall.draw(screen)



def draw_units(player, screen):
    for unit in player.military_units:
        unit.draw(screen)
    for worker in player.mine_workers:
        worker.draw(screen)
    for worker in player.wall_workers:
        worker.draw(screen)


resource_font = pygame.font.Font("freesansbold.ttf", 30)
default = pygame.font.SysFont("comicsans", 12)


def draw_labels(player, screen):
    text = resource_font.render(f"Resources: {int(player.resources)}$", True,
                                (255, 0, 0) if player.red_player else (0, 0, 255))
    screen.blit(text, (10, 30) if player.red_player else (SCREEN_W - text.get_width() -10, 30 ))

def draw_pause_label(screen):
    text = default.render(f"The game has been paused, press SPACE to continue or BackSlash to SAVE or press L to load a game, R to restart", True, (255, 0, 0))
    screen.blit(text, (SCREEN_W // 4 , SCREEN_H // 2))

def game_over(winner, screen):
    end_text = f"{winner} player Wins!"
    text = default.render(end_text, True, (0, 0, 0))
    textRect = text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 3))
    screen.blit(text, textRect)

    press_any_key = default.render("Press any key to start over", True, (0, 0, 0))
    press_any_keyRect = press_any_key.get_rect(center=(SCREEN_W // 2, (SCREEN_H // 3) * 2))
    screen.blit(press_any_key, press_any_keyRect)

def save(p1, p2):
    with open("saved_game.txt", "w") as file:
        file.write("START Game\n")
        file.write(f"TURN {pygame.time.get_ticks()}\n")
        file.write("END Game\n\n")

        for i, player in enumerate([p1, p2]):

            file.write(f"START Player{i + 1}\n")
            file.write(f"RESOURCES {int(player.resources)}\n")
            file.write(f"WALL {int(player.wall.health)}\n")

            # Saves every unit in the barracks
            for unit in player.barrack.ready_units:
                if isinstance(unit, SwordsMan):
                    file.write(f"BARRACKS SWORDSMAN\n")
                elif isinstance(unit, Archer):
                    file.write(f"BARRACKS ARCHER\n")
                elif isinstance(unit, Worker):
                    file.write(f"BARRACKS WORKER\n")

            # Saves every archer on the battlefield
            for unit in player.military_units:
                if isinstance(unit, SwordsMan):
                    file.write(f"SWORDSMAN {unit.rect.x} {unit.health}\n")
                elif isinstance(unit, Archer):
                    file.write(f"ARCHER {unit.rect.x} {unit.health}\n")

                    # Saves every arrow from that archer
                    for arrow in unit.arrows:
                        file.write(f"ARCHER_ARROW {arrow.rect.x}\n")

            # Saves every tower arrow
            for arrow in player.tower.arrows:
                file.write(f"TOWER_ARROW {int(arrow.x)} {int(arrow.y)} {arrow.angle}\n")

            # Saves every mine worker
            for worker in player.mine_workers:
                file.write(f"WORKER MINE {worker.rect.x}\n")

            # Saves every wall worker
            for worker in player.wall_workers:
                file.write(f"WORKER WALL {worker.rect.x}\n")

            file.write(f"END Player{i + 1}\n\n")

def load(p1, p2):
    players = []

    with open("saved_game.txt") as file:
        game, player1, player2, _ = [e.split("\n")[1:len(e.split("\n")) - 1] for e in file.read().split("\n\n")]

        # Declares the game turn
        turn = game[0].split()
        print(f"Turn: {turn[1]}")

        for i, player in enumerate([player1, player2]):
            isLeftPlayer = True if i == 0 else False
            p = p1 if isLeftPlayer else p2

            p.barrack.ready_units.clear()

            for line in player:
                components = line.split()
                property_name = components[0]

                if property_name == 'RESOURCES':
                    p.resources = int(components[1])

                elif property_name == 'WALL':
                    p.wall.health = int(components[1])

                elif property_name == 'ARCHER':
                    archer = Archer(p)
                    archer.x = int(components[1])
                    archer.health = int(components[2])
                    p.military_units.append(archer)

                elif property_name == 'SWORDSMAN':
                    swordsman = SwordsMan(p)
                    swordsman.x = int(components[1])
                    swordsman.health = int(components[2])
                    p.military_units.append(swordsman)

                elif property_name == 'WORKER':
                    worker = Worker(p)
                    if components[1] == 'MINE':
                        print("mine worker")
                        worker.x = p.mine.rect.centerx
                        p.mine_workers.append(worker)
                    elif components[1] == 'WALL':
                        worker.x = p.wall.rect.centerx
                        worker.running_to_mine = False
                        worker.running_to_wall = True
                        p.mine_workers.append(worker)

                elif property_name == 'BARRACKS':
                    if components[1] == 'SWORDSMAN':
                        p.barrack.ready_units.append(SwordsMan(p))
                    elif components[1] == 'ARCHER':
                        p.barrack.ready_units.append(Archer(p))
                    elif components[1] == 'WORKER':
                        p.barrack.ready_units.append(Worker(p))

                elif property_name == 'TOWER_ARROW':
                    arrow = Arrow(int(components[1]), int(components[2]), float(components[3]), isLeftPlayer)
                    p.tower.attack_timer = pygame.time.get_ticks()
                    p.tower.arrows.append(arrow)

                elif property_name == 'ARCHER_ARROW':
                    archer = next((unit for unit in p.military_units if isinstance(unit, Archer)), None)
                    if archer:
                        arrow = Arrow(int(components[1]), archer.rect.centery, 0, isLeftPlayer)
                        archer.attack_timer = pygame.time.get_ticks()
                        archer.arrows.append(arrow)

            players.append(p)

    return players[0], players[1]


