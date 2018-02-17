import math

from attrdict import AttrDict

from game import Game
from model.components.walkers.random_walker import RandomWalker
from model.maps.generators import map_generator


class ForestGenerator:
    """
    Generates a scary forest map in entirety, by mutating map tiles.
    Includes population of monsters, map items, etc.
    """
    
    TREE_PERCENTAGE = 1 / 4  # This percent of the map area should be trees
    TREE_COPSE_SIZE = 5  # Create copses of N trees at a time
    TREE_COLOURS = (
        (64, 128, 0), # Brownish
        (0, 64, 0)) # Greenish
    NUM_ITEMS = (10, 20)
    NUM_MONSTERS = (30, 40)

    def __init__(self, area_map):
        self._area_map = area_map
        self._generate_trees()
        
        map_generator.generate_monsters(self._area_map,
                                        Game.random.randint(ForestGenerator.NUM_MONSTERS[0], ForestGenerator.NUM_MONSTERS[1]))

        map_generator.generate_items(self._area_map,
                                     Game.random.randint(ForestGenerator.NUM_ITEMS[0], ForestGenerator.NUM_ITEMS[1]))


    def _generate_trees(self):
        for x in range(0, self._area_map.width):
            for y in range(0, self._area_map.height):
                self._area_map.tiles[x][y].convert_to_ground()

        total = math.floor(self._area_map.width * self._area_map.height * ForestGenerator.TREE_PERCENTAGE)

        # Creates little clusters of N trees
        while total > 0:
            to_create = min(ForestGenerator.TREE_COPSE_SIZE, total)
            self._random_walk(to_create)
            total -= to_create

        # It's too bad those little clusters sometimes create "holes" that are
        # unreachable on all sides. It would be a pity if the stairs ended up
        # spawning there.
        #
        # Since mining is not part of the core experience, let's flood-fill the
        # ground, and any non-flood-filled ground tiles can turn into trees.
        self._fill_ground_holes()

    def _breadth_first_search(self, start_position):
        """
        Breadth-first search. Assuming "position" is reachable,
        mark any other ground tiles that we can reach, as reachable.
        """
        explored = []
        queue = [start_position]

        while queue:
            position = queue.pop()
            (x, y) = position
            if self._area_map.tiles[x][y].is_walkable:  # ground tile
                explored.append(position)

                # Check each adjacent tile. If it's on-map, walkable, and not queued/explored,
                # then it's a candidate for an unwalkable tile.
                def append_if_eligible(to_append):
                    tile = self._area_map.tiles[to_append[0]][to_append[1]]
                    if tile.is_walkable and to_append not in queue + explored:
                        queue.append(to_append)

                if x > 0:
                    append_if_eligible((x - 1, y))
                if x < self._area_map.width - 1:
                    append_if_eligible((x + 1, y))
                if y > 0:
                    append_if_eligible((x, y - 1))
                if y < self._area_map.height - 1:
                    append_if_eligible((x, y + 1))

        return explored

    def _fill_ground_holes(self):
        start_position = self._find_empty_ground()

        all_ground_tiles = [
            (x, y)
            for y in range(0, self._area_map.height)
            for x in range(0, self._area_map.width)
            if self._area_map.tiles[x][y].is_walkable
        ]

        reachable = self._breadth_first_search(start_position)

        unreachable = [(x, y) for (x, y) in all_ground_tiles if (x, y) not in reachable]

        for (x, y) in unreachable:
            self._area_map.tiles[x][y].convert_to_wall(colour=Game.random.choice(ForestGenerator.TREE_COLOURS))

    def _find_empty_ground(self):
        """
        Look for a 3x3 patch of ground. It's unlikely that this is contained
        within a copse of trees as an enclosed area. If we're wrong ... well.
        I suppose you can always exit and re-enter the dungeon if that happens.
        """
        def is_empty_3x3(x, y):
            cond = True
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    cond = cond and self._area_map.tiles[i][j].is_walkable
            return cond

        for x in range(1, self._area_map.width - 1):
            for y in range(1, self._area_map.height - 1):
                if is_empty_3x3(x, y):
                    return x, y

        raise Exception("Can't find any empty ground with empty adjacent tiles!")

    def _random_walk(self, num_tiles):
        """
        Pick a random point, walk to a random adjacent point.
        If it's a floor tile, make it a wall tile, and decrement
        the number of tiles we have to walk.
        Repeat until num_tiles is 0
        """
        e = AttrDict({'x': (Game.random.randint(0, self._area_map.width - 1)), 'y': (Game.random.randint(0, self._area_map.height - 1))})
        walker = RandomWalker(self._area_map, e)

        while num_tiles > 0:
            try:
                walker.walk()
                self._area_map.tiles[e.x][e.y].convert_to_wall(colour=Game.random.choice(ForestGenerator.TREE_COLOURS))
                num_tiles -= 1
            except ValueError as no_walkable_adjacents_error:
                # While loop will not terminate, we'll try elsewhere
                # Randomly move, even if there's a tree there.
                dx = Game.random.randint(-1, 1)
                dy = Game.random.randint(-1, 1) if dx == 0 else 0

                e.x += dx
                e.y += dy
