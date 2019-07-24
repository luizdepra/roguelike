import tcod

from ..components.fighter import Fighter
from ..components.inventory import Inventory
from ..entity import Entity
from ..game_messages import MessageLog
from ..game_states import GameState
from ..map_objects.game_map import GameMap
from ..render_functions import RenderOrder


def get_game_variables(configs):
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(
        0,
        0,
        "@",
        tcod.white,
        "Player",
        blocks=True,
        render_order=RenderOrder.ACTOR,
        fighter=fighter_component,
        inventory=inventory_component,
    )
    entities = [player]

    game_map = GameMap(configs["map_width"], configs["map_height"])
    game_map.make_map(
        configs["max_rooms"],
        configs["room_min_size"],
        configs["room_max_size"],
        configs["map_width"],
        configs["map_height"],
        player,
        entities,
        configs["max_monsters_per_room"],
        configs["max_items_per_room"],
    )

    message_log = MessageLog(configs["message_x"], configs["message_width"], configs["message_height"])

    game_state = GameState.PLAYER_TURN

    return player, entities, game_map, message_log, game_state