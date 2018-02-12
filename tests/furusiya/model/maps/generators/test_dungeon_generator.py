import math
import random

from main_interface import Game
from model.maps.generators.dungeon_generator import DungeonGenerator
from model.maps.area_map import AreaMap
from model.entities.party.player import Player

class TestDungeonGenerator:
    def test_generate_generates_rooms(self):
        Game.area_map = AreaMap(80, 43)
        Game.player = Player()
        dg = DungeonGenerator(Game.area_map)

        assert len(dg._rooms) > 0
        # Basic sanity
        for room in dg._rooms:
            assert room.x1 >= 0
            assert room.y1 >= 0
            assert room.x2 > room.x1
            assert room.y2 > room.y1
            assert room.x2 - room.x1 >= 3 # two walls and a space in between
            assert room.y2 - room.y1 >= 3 # two walls and a space in between
            

    def test_generate_generates_monsters(self):
        Game.area_map = AreaMap(80, 40)
        dg = DungeonGenerator(Game.area_map)

        assert dg._area_map is Game.area_map
        assert len(Game.area_map.entities) >= 1