import colors
from model.config import config
import model.weapons
from death_functions import player_death
from main_interface import Game, message
from model.components.fighter import Fighter
from model.entities.game_object import GameObject
from model.systems.fighter_system import FighterSystem


class Player(GameObject):
    def __init__(self):
        data = config.data.player
        super().__init__(0, 0, '@', 'player', colors.white, blocks=True)

        # Turn a name like "Sword" into the actual class instance
        weapon_name = data.startingWeapon
        weapon_init = getattr(model.weapons, weapon_name)

        FighterSystem.set_fighter(
            self, Fighter(
                owner=self,
                hp=data.startingHealth,
                defense=data.startingDefense,
                power=data.startingPower,
                xp=0,
                weapon=weapon_init(self),
                death_function=player_death
            )
        )

        Game.draw_bowsight = False

        self.level = 1
        self.stats_points = 0
        self.arrows = config.data.player.startingArrows

        self.mounted = False
        self.moves_while_mounted = 0
        self.turns_to_rest = 0

        print("You hold your wicked-looking {} at the ready!".format(weapon_name))

    def mount(self, horse):
        if config.data.features.horseIsMountable:
            self.x, self.y = horse.x, horse.y
            self.mounted = True
            horse.is_mounted = True

    def unmount(self, horse):
        if config.data.features.horseIsMountable:
            self.mounted = False
            horse.is_mounted = False

    def _get_health_for_resting(self, max_hp):
        return int(config.data.skills.resting.percent/100 * max_hp)

    def rest(self):
        fighter = FighterSystem.get_fighter(self)
        hp_gained = self._get_health_for_resting(fighter.max_hp)
        fighter.heal(hp_gained)
        return 'rested'

    def calculate_turns_to_rest(self):
        fighter = FighterSystem.get_fighter(self)
        self.turns_to_rest = int((fighter.max_hp - fighter.hp) / self._get_health_for_resting(fighter.max_hp))

        message(f'You rest for {self.turns_to_rest} turns.')

    def move_or_attack(self, dx, dy):
        # TODO: Should this be part of the Fighter component?
        # the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        # try to find an attackable object there
        for obj in Game.area_map.get_entities_on(x, y):
            if FighterSystem.has_fighter(obj):
                target = obj
                break
        else:
            self.move(dx, dy)
            if self.mounted:
                if self.moves_while_mounted >= 1:
                    self.moves_while_mounted = 0
                else:
                    Game.current_turn = self
                    self.moves_while_mounted += 1
                Game.stallion.x, Game.stallion.y = self.x, self.y
            Game.renderer.recompute_fov = True
            return

        FighterSystem.get_fighter(self).attack(target)

    def _xp_next_level(self):
        return 2 ** (self.level + 1) * config.data.player.expRequiredBase

    def gain_xp(self, amount):
        # TODO: make this a component and eventually remove this class?
        fighter = FighterSystem.get_fighter(self)

        fighter.xp += amount
        # XP doubles every level. 40, 80, 160, ...
        # First level = after four orcs. Yeah, low standards.
        # DRY ya'ne
        while fighter.xp >= self._xp_next_level():
            self.level += 1
            self.stats_points += config.data.player.statsPointsOnLevelUp
            message("You are now level {}!".format(self.level))
            fighter.heal(fighter.max_hp)
