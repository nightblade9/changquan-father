import colors
from main_interface import Game, message
from model.components.base import Component


class Item(Component):
    """
    an item that can be picked up and used.
    """
    component_type = 'Item'

    def __init__(self, owner, use_function=None):
        super().__init__(owner)
        self.use_function = use_function

    def pick_up(self):
        """
        add to the player's inventory and remove from the map
        """
        if len(Game.inventory) >= 26:
            message('Your inventory is full, cannot pick up ' +
                    self.owner.name + '.', colors.red)
        elif "arrows" in self.owner.name:
            global player
            # eg. 13 arrows
            num_arrows = int(self.owner.name[0:self.owner.name.index(' ')])
            Game.player.arrows += num_arrows
            message("Picked up {} arrows. Total={}".format(num_arrows, Game.player.arrows))
            Game.entities.remove(self.owner)
        else:
            Game.inventory.append(self.owner)
            Game.entities.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)

    def drop(self):
        """
        add to the map and remove from the player's inventory. also, place it at the player's coordinates
        """
        Game.entities.append(self.owner)
        Game.inventory.remove(self.owner)
        self.owner.x = Game.player.x
        self.owner.y = Game.player.y
        message('You dropped a ' + self.owner.name + '.', colors.yellow)

    def use(self):
        # just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                Game.inventory.remove(self.owner)  # destroy after use, unless it was
                # cancelled for some reason


