import math

import tcod

from .components.item import Item
from .render_functions import RenderOrder


class Entity:
    def __init__(
        self,
        x,
        y,
        char,
        color,
        name,
        blocks=False,
        render_order=RenderOrder.CORPSE,
        fighter=None,
        ai=None,
        item=None,
        inventory=None,
        stairs=None,
        level=None,
        equipment=None,
        equippable=None,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (
            game_map.is_blocked(self.x + dx, self.y + dy)
            or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)
        ):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):
        fov = tcod.map_new(game_map.width, game_map.height)

        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tcod.map_set_properties(
                    fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked
                )

        for entity in entities:
            if entity.blocks and entity not in [self, target]:
                tcod.map_set_properties(fov, entity.x, entity.y, True, False)

        my_path = tcod.path_new_using_map(fov, 1.41)
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                self.x = x
                self.y = y
        else:
            self.move_towards(target.x, target.y, game_map, entities)

        tcod.path_delete(my_path)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


def get_blocking_entities_at_location(entities, destionation_x, destionation_y):
    for entity in entities:
        if entity.blocks and entity.x == destionation_x and entity.y == destionation_y:
            return entity

    return None
