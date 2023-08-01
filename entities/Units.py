import math
import random

import pygame

from utils.Constants import *


class Arrow:
    images = {
        "player1": {
            "diag": [pygame.image.load(f"./sprites/player1/bow/arrowdiag-{i}.png") for i in range(2)],
            "hor": [pygame.image.load(f"./sprites/player1/bow/arrowhor-{i}.png") for i in range(2)],
            "vert": [pygame.image.load(f"./sprites/player1/bow/arrowvert-{i}.png") for i in range(2)]
        },
        "player2": {
            "diag": [pygame.image.load(f"./sprites/player2/bow/arrowdiag-{i}.png") for i in range(2)],
            "hor": [pygame.image.load(f"./sprites/player2/bow/arrowhor-{i}.png") for i in range(2)],
            "vert": [pygame.image.load(f"./sprites/player2/bow/arrowvert-{i}.png") for i in range(2)]
        }

    }

    def __init__(self, x, y, angle, redPlayer):
        self.angle = angle
        self.speed = ARROW_SPEED
        self.x = x
        self.y = y
        self.speedX = ARROW_SPEED * math.cos(angle) if redPlayer else -ARROW_SPEED * math.cos(angle)
        self.speedY = ARROW_SPEED * math.sin(angle)

        self.animations = Arrow.images['player1'] if redPlayer else Arrow.images['player2']
        self.image_index = 0
        if angle == 0:
            self.arrow_orientation = "hor"
        elif 0 < angle <= ((math.pi / 2) - (math.pi / 6)):
            self.arrow_orientation = "diag"
        else:
            self.arrow_orientation = "vert"

        self.image = self.animations[self.arrow_orientation][0]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self):
        self.image_index += 0.2
        if self.image_index > len(self.animations[self.arrow_orientation]):
            self.image_index = 0

        self.x += self.speedX
        self.y += self.speedY
        self.image = self.animations[self.arrow_orientation][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class CannonBall:
    damage_range = 100
    gravity = 30

    def __init__(self, redPlayer, x, y):
        self.angle = random.randint(20, 40)
        self.speed = random.randint(7,9) if redPlayer else -random.randint(7, 9)
        self.start_time = pygame.time.get_ticks() * 0.001
        self.time = 0
        self.angle = self.angle if redPlayer else -self.angle
        self.angle_radians = math.radians(self.angle)
        self.x = x
        self.speedX = self.speed * math.cos(self.angle_radians)
        self.y = y
        self.image = pygame.image.load(
            "sprites/player1/building/bullet.png" if redPlayer else "sprites/player2/building/bullet.png")
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        self.rangeBox = pygame.Rect(0, 0, self.rect.w + (self.damage_range * 2), self.rect.h)
        self.rangeBox.midbottom = self.rect.midbottom

    def update(self):
        current_time = pygame.time.get_ticks() * 0.001  # Convert to seconds
        self.time = current_time - self.start_time


          # Convert the angle to radians

        self.x += self.speedX
        self.y -= self.speed * self.time * math.sin(self.angle_radians) -  self.gravity * self.time ** 2
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        self.rangeBox.midbottom = self.rect.midbottom



    def draw(self, screen):
        screen.blit(self.image, self.rect)



class Archer:
    SPEED = ARCHER_SPEED
    DAMAGE = 5
    COST = 5
    images = {"player1":
        {
            "run": [pygame.image.load(f"./sprites/player1/bow/run-{i}.png") for i in range(12)],
            "shoot": [pygame.image.load(f"./sprites/player1/bow/shoot-{i}.png") for i in range(2)],
            "fallen": [pygame.image.load(f"./sprites/player1/bow/fallen-{i}.png") for i in range(6)],
            "ready": pygame.image.load("./sprites/player1/bow/ready.png")
        },
        "player2": {
            "run": [pygame.image.load(f"./sprites/player2/bow/run-{i}.png") for i in range(12)],
            "shoot": [pygame.image.load(f"./sprites/player2/bow/shoot-{i}.png") for i in range(2)],
            "fallen": [pygame.image.load(f"./sprites/player2/bow/fallen-{i}.png") for i in range(6)],
            "ready": pygame.image.load("./sprites/player2/bow/ready.png")
        }
    }

    def __init__(self, player):
        self.player = player
        self.arrows = []
        self.rest = False
        self.fall = False
        self.attack = False
        self.run = True
        self.image_index = 0
        self.x = BARRACK_X if player.red_player else SCREEN_W - BARRACK_X
        self.y = SCREEN_H - GROUND
        self.health = 20
        self.damage = Archer.DAMAGE
        self.training_time = 30
        self.rest_time = 1000
        self.range = 100
        self.speed = Archer.SPEED if player.red_player else -Archer.SPEED
        self.red_player = player.red_player
        self.animations = self.images['player1'] if player.red_player else self.images['player2']
        self.image = self.animations['ready']
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        self.attack_timer = 0
        self.alive = True
        self.rangeBox = pygame.Rect(0, 0, self.rect.w + (self.range * 2), self.rect.h)
        self.rangeBox.midbottom = self.rect.midbottom

    def draw(self, screen):
        for arrow in self.arrows:
            arrow.draw(screen)
        screen.blit(self.image, self.rect)

    def update(self, target, enemy_units):

        self.rangeBox.midbottom = self.rect.midbottom

        for i, arrow in enumerate(self.arrows):
            arrow.update()

            if arrow.rect.colliderect(target.rect):
                target.health -= self.damage
                del self.arrows[i]

            for unit in enemy_units:
                if arrow.rect.colliderect(unit.rect) and self.arrows and unit.alive:
                    unit.health -= self.damage
                    del self.arrows[i]

        self.check_actions(target)

    def running(self):
        self.image_index += 0.2
        if self.image_index > len(self.animations['run']):
            self.image_index = 0

        self.x += self.speed
        self.image = self.animations['run'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def resting(self):
        self.image = self.animations['ready']
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def falling(self):
        if self.image_index + 0.2 < len(self.animations['fallen']):
            self.image_index += 0.2

        self.image = self.animations['fallen'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def check_actions(self, target):
        if self.run:
            self.running()
        elif self.attack:
            self.shooting()
        elif self.fall:
            self.falling()
        elif self.rest:
            self.resting()

        if self.health <= 0:
            if self.alive:
                self.image_index = 0
                self.alive = False

            self.run = False
            self.attack = False
            self.fall = True
            self.rest = False
        else:
            if target and self.rangeBox.colliderect(target.rect) and WALL_X <= self.x <= SCREEN_W - WALL_X:
                if pygame.time.get_ticks() - self.attack_timer >= self.rest_time:
                    self.run = False
                    self.attack = True
                    self.fall = False
                    self.rest = False
                else:
                    self.run = False
                    self.attack = False
                    self.fall = False
                    self.rest = True
            else:
                self.run = True
                self.attack = False
                self.fall = False
                self.rest = False

    def shooting(self):
        self.image_index += 0.2
        if self.image_index > len(self.animations['shoot']):
            self.image_index = 0

            self.arrows.append(Arrow(self.rect.right, self.rect.centery, 0, self.player.red_player))
            self.attack_timer = pygame.time.get_ticks()
            self.run = False
            self.attack = False
            self.fall = False
            self.rest = True

        self.image = self.animations['shoot'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))


class SwordsMan:
    training_time = 20
    damage = 3
    rest_time = 1000
    images = {
        "player1": {
            "run": [pygame.image.load(f"./sprites/player1/sword/run-{i}.png") for i in range(10)],
            "attack": [pygame.image.load(f"./sprites/player1/sword/attack-{i}.png") for i in range(8)],
            "fallen": [pygame.image.load(f"./sprites/player1/sword/fallen-{i}.png") for i in range(6)],
            "ready": pygame.image.load("./sprites/player1/sword/ready.png")
        },
        "player2":
            {
                "run": [pygame.image.load(f"./sprites/player2/sword/run-{i}.png") for i in range(10)],
                "attack": [pygame.image.load(f"./sprites/player2/sword/attack-{i}.png") for i in range(8)],
                "fallen": [pygame.image.load(f"./sprites/player2/sword/fallen-{i}.png") for i in range(6)],
                "ready": pygame.image.load("./sprites/player2/sword/ready.png")
            }
    }

    def __init__(self, player):
        self.player = player
        self.run = True
        self.attack = False
        self.rest = False
        self.fall = False
        self.red_player = player.red_player
        self.x = BARRACK_X if player.red_player else SCREEN_W - BARRACK_X
        self.y = SCREEN_H - GROUND
        self.speed = SWORDSMAN_SPEED if player.red_player else -SWORDSMAN_SPEED
        self.animations = self.images['player1'] if player.red_player else self.images['player2']
        self.image = self.animations['ready']
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        self.image_index = 0
        self.health = 25
        self.attack_timer = 0
        self.range = 10
        self.alive = True
        self.rangeBox = pygame.Rect(0, 0, self.rect.w + (self.range * 2), self.rect.h)
        self.rangeBox.midbottom = self.rect.midbottom

    def running(self):
        self.image_index += 0.2
        if self.image_index > len(self.animations['run']):
            self.image_index = 0

        self.x += self.speed
        self.image = self.animations['run'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def attacking(self, target):
        self.image_index += 0.2
        if self.image_index > len(self.animations['attack']):
            self.image_index = 0

            target.health -= self.damage
            self.attack_timer = pygame.time.get_ticks()
            self.run = False
            self.rest = True
            self.fall = False
            self.attack = False

        self.image = self.animations['attack'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def resting(self):
        self.image = self.animations['ready']
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def falling(self):
        if self.image_index + 0.2 < len(self.animations['fallen']):
            self.image_index += 0.2

        self.image = self.animations['fallen'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self, target, enemy_units):
        self.rangeBox.midbottom = self.rect.midbottom

        if self.run:
            self.running()
        elif self.rest:
            self.resting()
        elif self.attack:
            self.attacking(target)
        elif self.fall:
            self.falling()

        if self.health <= 0:
            if self.alive:
                self.image_index = 0
                self.alive = False

            self.run = False
            self.fall = True
            self.attack = False
            self.rest = False
        else:
            if target and self.rangeBox.colliderect(target.rect) and WALL_X <= self.x <= SCREEN_W - WALL_X:
                if pygame.time.get_ticks() - self.attack_timer >= self.rest_time:
                    self.run = False
                    self.fall = False
                    self.rest = False
                    self.attack = True
                else:
                    self.attack = False
                    self.fall = False
                    self.rest = True
                    self.run = False
            else:
                self.run = True
                self.fall = False
                self.rest = False
                self.attack = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Worker:
    production_amount = 3
    repair_rate = 2
    training_time = 10

    images = {"player1": {
        "dig": [pygame.image.load(f"./sprites/player1/worker/dig-{i}.png") for i in range(9)],
        "repair": [pygame.image.load(f"./sprites/player1/worker/repair-{i}.png") for i in range(4)],
        "run_right": [pygame.image.load(f"./sprites/player1/worker/run-{i}.png") for i in range(6)],
        "run_left": [pygame.transform.flip(pygame.image.load(f"./sprites/player1/worker/run-{i}.png"), True, False) for
                     i in range(6)],
        "ready": pygame.image.load("./sprites/player2/worker/ready.png")
    }, "player2": {
        "dig": [pygame.image.load(f"./sprites/player2/worker/dig-{i}.png") for i in range(9)],
        "repair": [pygame.image.load(f"./sprites/player2/worker/repair-{i}.png") for i in range(4)],
        "run_left": [pygame.image.load(f"./sprites/player2/worker/run-{i}.png") for i in range(6)],
        "run_right": [pygame.transform.flip(pygame.image.load(f"./sprites/player2/worker/run-{i}.png"), True, False) for
                      i in range(6)],
        "ready": pygame.image.load("./sprites/player2/worker/ready.png")
    }
    }

    def __init__(self, player):
        self.red_player = player.red_player
        self.player = player
        self.x = BARRACK_X if self.red_player else SCREEN_W - BARRACK_X
        self.y = SCREEN_H - GROUND
        self.speed = WORKER_SPEED
        self.animations = self.images['player1'] if self.red_player else self.images['player2']
        self.image = self.animations['ready']
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))
        self.image_index = 0
        self.running_to_mine = True
        self.running_to_wall = False
        self.digging = False
        self.repairing = False

    def to_wall(self):
        self.running_to_mine = False
        self.running_to_wall = True
        self.digging = False
        self.repairing = False

    def to_mine(self):
        self.running_to_mine = True
        self.running_to_wall = False
        self.digging = False
        self.repairing = False

    def run_to_mine(self, mine):
        self.image_index += 0.2
        if self.image_index > len(self.animations['run_left']):
            self.image_index = 0

        if mine.rect.centerx < self.rect.centerx:
            self.x -= self.speed
            self.image = self.animations['run_left'][int(self.image_index)]
        elif mine.rect.centerx > self.rect.centerx:
            self.x += self.speed
            self.image = self.animations['run_right'][int(self.image_index)]
        else:
            self.running_to_mine = False
            self.running_to_wall = False
            self.digging = True
            self.repairing = False

        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def run_to_wall(self, wall):
        self.image_index += 0.2
        if self.image_index > len(self.animations['run_left']):
            self.image_index = 0

        if wall.rect.right < self.rect.centerx:
            self.x -= self.speed
            self.image = self.animations['run_left'][int(self.image_index)]
        elif wall.rect.left > self.rect.centerx:
            self.x += self.speed
            self.image = self.animations['run_right'][int(self.image_index)]
        else:
            self.running_to_mine = False
            self.running_to_wall = False
            self.digging = False
            self.repairing = True

        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def dig(self):
        self.image_index += 0.2
        if self.image_index >= len(self.animations['dig']):
            self.image_index = 0
            self.player.resources += self.production_amount

        self.image = self.animations['dig'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def repair(self, wall):

        self.image_index += 0.1
        if self.image_index > len(self.animations['repair']):
            self.image_index = 0
            wall.health += self.repair_rate

        if wall.health >= WALL_HEALTH:
            wall.health = WALL_HEALTH
        self.image = self.animations['repair'][int(self.image_index)]
        self.rect = self.image.get_rect(midbottom=(self.x, self.y))

    def update(self, wall, mine):
        # print(f"{len(self.animations['repair'])} + {self.image_index}")
        if self.running_to_mine:
            self.run_to_mine(mine)
        elif self.digging:
            self.dig()
        elif self.repairing:
            self.repair(wall)
        elif self.running_to_wall:
            self.run_to_wall(wall)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
