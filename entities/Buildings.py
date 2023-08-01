from entities.Units import *


class Barrack:
    def __init__(self, player):
        self.player = player
        self.img = pygame.image.load(
            "sprites/player1/building/barracks.png" if player.red_player else "sprites/player2/building/barracks.png")
        self.x = BARRACK_X if player.red_player else SCREEN_W - BARRACK_X
        self.rect = self.img.get_rect(midbottom=(self.x, SCREEN_H - GROUND))
        self.training_timer = 0
        self.unleashing_timer = 0
        self.unleashing_time_per_unit = 300
        self.is_training = False
        self.is_unleashing = False
        self.is_unleashing_unit = False
        self.training_queue = []
        self.unleashing_units = []

        # Initialize the barracks with one of each unit
        self.ready_units = [
            Worker(self.player),
            Archer(self.player),
            SwordsMan(self.player)
        ]

    def check_training_queue(self):
        if self.training_queue:
            if not self.is_training:
                self.is_training = True
                self.training_timer = pygame.time.get_ticks()
            elif self.is_training:
                if pygame.time.get_ticks() - self.training_timer >= self.training_queue[0].training_time * 100:
                    self.is_training = False
                    unit = self.training_queue.pop(0)
                    self.ready_units.append(unit)

    def train_military(self, unit_type):
        new_unit = unit_type(self.player)
        self.training_queue.append(new_unit)

    def train_worker(self, player):
        worker = Worker(player)
        self.training_queue.append(worker)

    def deploy_worker(self, to_mine):
        for i, unit in enumerate(self.ready_units):
            if isinstance(unit, Worker):
                worker = self.ready_units.pop(i)
                if to_mine:
                    worker.to_mine()
                    self.player.mine_workers.append(worker)
                else:
                    worker.to_wall()
                    self.player.wall_workers.append(worker)
                break

    def deploy_swordsman(self):
        if any(isinstance(unit, SwordsMan) for unit in self.ready_units):
            for i, unit in enumerate(self.ready_units):
                if isinstance(unit, SwordsMan):
                    swordsman = self.ready_units.pop(i)
                    self.player.military_units.append(swordsman)
                    break

    def deploy_archer(self):
        if any(isinstance(unit, Archer) for unit in self.ready_units):
            print(self.ready_units)
            for i, unit in enumerate(self.ready_units):
                if isinstance(unit, Archer):
                    archer = self.ready_units.pop(i)
                    self.player.military_units.append(archer)
                    break

    def deploy_all(self):
        self.unleashing_units.extend(self.ready_units)
        self.ready_units.clear()

        if not self.is_unleashing:
            self.is_unleashing = True

    def deploy(self):
        if self.is_unleashing:
            if self.unleashing_units and not self.is_unleashing_unit:
                self.is_unleashing_unit = True
                self.unleashing_timer = pygame.time.get_ticks()
            elif self.unleashing_units and self.is_unleashing_unit:
                if pygame.time.get_ticks() - self.unleashing_timer >= self.unleashing_time_per_unit:
                    unit = self.unleashing_units.pop(0)
                    if isinstance(unit, (Archer, SwordsMan)):
                        self.player.military_units.append(unit)
                    else:
                        self.player.mine_workers.append(unit)
                    self.is_unleashing_unit = False
            else:
                self.is_unleashing = False

    def update(self):
        self.check_training_queue()
        self.deploy()

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Wall:
    MAX_HEALTH = WALL_HEALTH

    def __init__(self, redPlayer):
        self.img = pygame.image.load(
            "sprites/player1/building/wall.png" if redPlayer else "sprites/player2/building/wall.png")
        self.x = WALL_X if redPlayer else SCREEN_W - WALL_X

        self.rect = self.img.get_rect(midbottom=(self.x, SCREEN_H - GROUND))

        self.health = WALL_HEALTH
        self.hb_width = 50

    def draw_health_bar(self, screen):
        red_hb_rect = pygame.Rect(0, 0, self.hb_width, 6)
        red_hb_rect.center = (self.rect.centerx, (self.rect.top // 2) - 15)
        pygame.draw.rect(screen, (255, 0, 0), red_hb_rect)

        green_hb_rect = pygame.Rect(0, 0, self.hb_width * (self.health / self.MAX_HEALTH), 6)
        green_hb_rect.topleft = red_hb_rect.topleft
        pygame.draw.rect(screen, (0, 255, 0), green_hb_rect)

    def draw(self, screen):
        screen.blit(self.img, self.rect)
        if self.health < self.MAX_HEALTH:
            self.draw_health_bar(screen)


class Mine:
    def __init__(self, redPlayer):
        self.img = pygame.image.load(
            "sprites/player1/building/mine.png" if redPlayer else "sprites/player2/building/mine.png")
        self.x = MINE_X if redPlayer else SCREEN_W - MINE_X

        self.rect = self.img.get_rect(midbottom=(self.x, SCREEN_H - GROUND))

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Tower:
    range = 200
    damage = 10
    canon_damage = 10
    rest_time = 1000
    cannon_rest_time = 100

    def __init__(self, isRedPlayer):
        self.isRedPlayer = isRedPlayer
        self.img = pygame.image.load(
            "sprites/player1/building/tower.png" if isRedPlayer else "sprites/player2/building/tower.png")
        self.x = WALL_X if isRedPlayer else SCREEN_W - WALL_X
        self.rect = self.img.get_rect(midbottom=(self.x, SCREEN_H - GROUND))
        self.arrows = []
        self.cannon_balls = []
        self.attack_timer = 0
        self.cannon_attack_timer = 0
        self.resting = True
        self.cannon_rest = False
        self.attacking = False
        self.cannon_ball = None
        self.cannon_attack = False

    def rest(self):
        pass

    def attack(self, target):
        x = abs(self.rect.centerx - target.rect.centerx)
        y = target.rect.centery - self.rect.top
        arrow_angle = math.atan(y / x)

        self.arrows.append(Arrow(self.rect.centerx, self.rect.top, arrow_angle, self.isRedPlayer))
        self.attack_timer = pygame.time.get_ticks()

    def update_arrows(self, enemy_units):
        for i, arrow in enumerate(self.arrows):
            arrow.update()

            if arrow.rect.bottom >= SCREEN_H - GROUND:
                del self.arrows[i]

            for unit in enemy_units:
                if unit.alive and arrow.rect.colliderect(unit.rect) and self.arrows:
                    unit.health -= self.damage
                    del self.arrows[i]

    def update_cannon_balls(self, enemy_units, player_units):
        self.cannon_ball.update()

        if self.cannon_ball.rect.bottom >= SCREEN_H - GROUND:
            for unit in enemy_units:
                if unit.alive and self.cannon_ball.rangeBox.colliderect(unit.rect):
                    unit.health -= self.canon_damage
                    print(f"enemy unit health: {unit.health}" )
            for unit in player_units:
                if unit.alive and self.cannon_ball.rangeBox.colliderect(unit.rect):
                    unit.health -= self.canon_damage
            self.cannon_ball = None
            self.cannon_attack = False




    def update(self, target, enemy_units, player_units):

        if pygame.time.get_ticks() - self.attack_timer >= self.rest_time and abs(
                self.rect.centerx - target.rect.centerx) <= Tower.range:
            self.attacking = True
            self.resting = False
        else:
            self.attacking = False
            self.resting = True
        if pygame.time.get_ticks() - self.cannon_attack_timer >=self.cannon_rest_time:
            self.cannon_rest = False
        else:
            self.cannon_rest = True
        if self.resting:
            self.rest()
        elif self.attacking:
            self.attack(target)
        self.update_arrows(enemy_units)
        if self.cannon_attack:
            print(f"New CannonBall speed: {self.cannon_ball.rangeBox}")
            self.update_cannon_balls(enemy_units, player_units)




    def draw(self, screen):
        for arrow in self.arrows:
            arrow.draw(screen)
        if self.cannon_ball:
            self.cannon_ball.draw(screen)

        screen.blit(self.img, self.rect)
    """def shoot_cannonBall(self):

        if not self.cannon_rest:
            self.cannon_balls.append(CannonBall(self.isRedPlayer, self.rect.centerx, self.rect.top))
            self.cannon_attack_timer = pygame.time.get_ticks()"""

    def shoot_cannonBall(self):
        self.cannon_attack = True
        if not self.cannon_rest:
            self.cannon_ball =  CannonBall(self.isRedPlayer, self.rect.centerx, self.rect.top)

            self.cannon_attack_timer = pygame.time.get_ticks()


import math

"""class CannonTower(Tower):
    range = 300
    damage = 20
    rest_time = 200
    cool_down_time = 400

    def __init__(self, isRedPlayer):
        self.img = pygame.image.load(
            "sprites/player1/building/bullet.png" if isRedPlayer else "sprites/player2/building/bullet.png")
        self.attack_timer = 0
        self.cool_down_timer = 0
        self.initial_speed = 100
        self.angle = math.radians(45)
        self.gravity = 9.8
        self.cool_down_time = 4000
        self.cannon_balls = []
        self.cooling_down = False

    def shoot(self, target,enemy_units):
        ball_speed = self.initial_speed
        ball_x = self.rect.centerx
        ball_y = self.rect.top

        # Projectile motion equations
        for t in range(100):
            ball_x += ball_speed * t * math.cos(self.angle)
            ball_y += ball_speed * t * math.sin(self.angle) - 0.5 * self.gravity * t ** 2

            if ball_y <= 0:
                break
        for unit in enemy_units:
            if unit.rect.collidepoint(ball_x, ball_y):
                unit.health -= self.damage
                break


    def update(self, target, enemy_units):
        if pygame.time.get_ticks() - self.attack_timer >= self.rest_time and not self.cooling_down:
            self.shoot(target,enemy_units)
            self.attack_timer = pygame.time.get_ticks()
            self.cool_down_timer = pygame.time.get_ticks()
            self.cooling_down = True  # Start the cooldown
        elif self.cooling_down and pygame.time.get_ticks() - self.cool_down_timer >= self.cool_down_time:
            self.cooling_down = False  # Reset the cooldown when it's over

        super().update(target, enemy_units)"""
