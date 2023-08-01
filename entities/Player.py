from entities.Buildings import *
from utils import Methods
from utils.Commands import Commands
from utils.Constants import *


class Player:

    def __init__(self, red_player):
        self.wall_workers = []
        self.mine_workers = []
        self.targeted_unit = None
        self.military_units = []
        self.red_player = red_player
        self.commands = Commands(red_player)
        self.wall = Wall(self.red_player)
        self.resources = START_RESOURCE
        self.enemy = None
        self.barrack = Barrack(self)
        self.tower = Tower(self.red_player)
        self.mine = Mine(self.red_player)


    def read_command(self, command):
        if command == self.commands.train_archer:
            if self.resources > ARCHER_COST:
                self.barrack.train_military(Archer)
                self.resources -= ARCHER_COST
            else:
                self.resources = 0
        elif command == self.commands.train_swordsman:
            if self.resources > SWORDSMAN_COST:
                self.barrack.train_military(SwordsMan)
                self.resources -= SWORDSMAN_COST
            else:
                self.resources = 0
        elif command == self.commands.archer_attack:
            self.barrack.deploy_archer()

        elif command == self.commands.swordsman_attack:
            self.barrack.deploy_swordsman()

        elif command == self.commands.train_worker:
            if self.resources > WORKER_COST:
                self.barrack.train_worker(self)
                self.resources -= WORKER_COST
            else:
                self.resources = 0
        elif command == self.commands.to_mine:
            self.to_mine()

        elif command == self.commands.to_wall:
            self.to_wall()

        elif command == self.commands.deploy_all:
            self.barrack.deploy_all()

        elif command == self.commands.cannon_attack and not self.tower.cannon_attack:
            self.tower.shoot_cannonBall()
            self.resources -= CANNON_COST

    def to_mine(self):
        if any(isinstance(unit, Worker) for unit in self.barrack.ready_units):
            self.barrack.deploy_worker(True)
        elif self.wall_workers:
            worker = self.wall_workers.pop()
            self.mine_workers.append(worker)
            worker.to_mine()

    def to_wall(self):
        if any(isinstance(unit, Worker) for unit in self.barrack.ready_units):
            self.barrack.deploy_worker(False)
        elif self.mine_workers:
            worker = self.mine_workers.pop()
            self.wall_workers.append(worker)
            worker.to_wall()

    def update(self):
        self.target()
        Methods.units_update(self)
        Methods.building_update(self)

    def draw(self, screen):
        Methods.draw_building(self, screen)
        Methods.draw_units(self, screen)

    def target(self):
        alive_units = [unit for unit in self.enemy.military_units if unit.alive]

        if alive_units:
            selected_target = min(alive_units, key=lambda unit: abs(self.wall.rect.x - unit.x))
            self.targeted_unit = selected_target if WALL_X <= selected_target.rect.centerx <= SCREEN_W - WALL_X else self.enemy.wall
        else:
            self.targeted_unit = self.enemy.wall




