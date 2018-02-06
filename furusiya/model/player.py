import colors
import config
from main_interface import Game, message, player_death
from model.gameobject import GameObject
from model.component import Fighter
from model.weapon import Sword, Bow, Hammer


class Player(GameObject):
    def __init__(self):
        data = config.data.player
        super(Player, self).__init__(0, 0, '@', 'player', colors.white,
                                     blocks=True,
                                     fighter=Fighter(hp=data.startingHealth,
                                                     defense=data.startingDefense, power=data.startingPower, xp=0,
                                                     weapon=None, death_function=player_death))

        Game.draw_bowsight = False

        # Eval is evil if misused. Here, the config tells me the constructor
        # method to call to create my weapon. Don't try this in prod, folks.
        weapon_name = data.startingWeapon
        initializer = eval(weapon_name)
        self.fighter.weapon = initializer(self)  # __init__(owner)

        self.level = 1
        self.stats_points = 0
        self.arrows = config.data.player.startingArrows

        print("You hold your wicked-looking {} at the ready!".format(weapon_name))

    def gain_xp(self, amount):
        self.fighter.xp += amount
        # XP doubles every level. 40, 80, 160, ...
        # First level = after four orcs. Yeah, low standards.
        xp_next_level = 2 ** (self.level + 1) * 10
        # DRY ya'ne
        while self.fighter.xp >= xp_next_level:
            self.level += 1
            self.stats_points += config.data.player.statsPointsOnLevelUp
            xp_next_level = 2 ** (self.level + 1) * config.data.player.expRequiredBase
            message("You are now level {}!".format(self.level))
            self.fighter.heal(self.fighter.max_hp)
