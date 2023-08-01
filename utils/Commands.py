import pygame as pg


class Commands:
    RED_KEY_COMMANDS = {
        "train_swordsman": "w",
        "train_archer": "e",
        "train_worker": "q",
        "sword_attack": "d",
        "archer_attack": "f",
        "to_mine": "a",
        "to_wall": "s",
        "unleash": "z",
        "save": "b",
        "cannon_attack": "c"
    }

    BLUE_KEY_COMMANDS = {
        "train_swordsman": "o",
        "train_archer": "i",
        "sword_attack": "j",
        "archer_attack": "h",
        "train_worker": "p",
        "to_mine": "l",
        "to_wall": "k",
        "unleash": "m",
        "save": "b",
        "cannon_attack": "n"
    }

    def __init__(self, player):
        self.deploy_all = None
        self.archer_attack = None
        self.swordsman_attack = None
        self.to_wall = None
        self.to_mine = None
        self.train_archer = None
        self.train_swordsman = None
        self.train_worker = None
        self.cannon_attack = None
        self.key_mapper(Commands.RED_KEY_COMMANDS if player else Commands.BLUE_KEY_COMMANDS)

    def key_mapper(self, commands):
        self.train_worker = pg.key.key_code(commands['train_worker'])
        self.train_swordsman = pg.key.key_code(commands['train_swordsman'])
        self.train_archer = pg.key.key_code(commands['train_archer'])
        self.to_mine = pg.key.key_code(commands['to_mine'])
        self.to_wall = pg.key.key_code(commands['to_wall'])
        self.swordsman_attack = pg.key.key_code(commands['sword_attack'])
        self.archer_attack = pg.key.key_code(commands['archer_attack'])
        self.deploy_all = pg.key.key_code(commands['unleash'])
        self.cannon_attack = pg.key.key_code(commands['cannon_attack'])

