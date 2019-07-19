import tcod

from .components.fighter import Fighter
from .components.inventory import Inventory
from .death_functions import kill_monster, kill_player
from .entity import Entity, get_blocking_entities_at_location
from .fov_functions import initialize_fov, recompute_fov
from .game_messages import Message, MessageLog
from .game_states import GameState
from .input_handlers import handle_keys
from .map_objects.game_map import GameMap
from .render_functions import RenderOrder, clear_all, render_all

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MESSAGE_X = BAR_WIDTH + 2
MESSAGE_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MESSAGE_HEIGHT = PANEL_HEIGHT - 1

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

MAX_MONSTERS_PER_ROOM = 3
MAX_ITEMS_PER_ROOM = 2

FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 10

COLORS = {
    "dark_wall": tcod.Color(0, 0, 100),
    "dark_ground": tcod.Color(50, 50, 150),
    "light_wall": tcod.Color(130, 110, 50),
    "light_ground": tcod.Color(200, 180, 50),
}


def main():
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

    tcod.console_set_custom_font("assets/fonts/arial10x10.png", tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Roguelike Tutorial", False)

    con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    panel = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
    game_map.make_map(
        MAX_ROOMS,
        ROOM_MIN_SIZE,
        ROOM_MAX_SIZE,
        MAP_WIDTH,
        MAP_HEIGHT,
        player,
        entities,
        MAX_MONSTERS_PER_ROOM,
        MAX_ITEMS_PER_ROOM,
    )

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(MESSAGE_X, MESSAGE_WIDTH, MESSAGE_HEIGHT)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameState.PLAYER_TURN
    previous_game_state = game_state

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, FOV_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM)

        render_all(
            con,
            panel,
            entities,
            player,
            game_map,
            fov_map,
            fov_recompute,
            message_log,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            BAR_WIDTH,
            PANEL_HEIGHT,
            PANEL_Y,
            mouse,
            COLORS,
            game_state,
        )

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)

        move = action.get("move")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        player_turn_results = []

        if move and game_state == GameState.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameState.ENEMY_TURN
        elif pickup and game_state == GameState.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message("There is nothing here to pick up.", tcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameState.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameState.DROP_INVENTORY

        if (
            inventory_index is not None
            and previous_game_state != GameState.PLAYER_DEAD
            and inventory_index < len(player.inventory.items)
        ):
            item = player.inventory.items[inventory_index]
            if game_state == GameState.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item))
            elif game_state == GameState.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if exit:
            if game_state in (GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY):
                game_state = previous_game_state
            else:
                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for result in player_turn_results:
            message = result.get("message")
            dead_entity = result.get("dead")
            item_added = result.get("item_added")
            item_consumed = result.get("consumed")
            item_dropped = result.get("item_dropped")

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameState.ENEMY_TURN

            if item_consumed:
                game_state = GameState.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameState.ENEMY_TURN

        if game_state == GameState.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for result in enemy_turn_results:
                        message = result.get("message")
                        dead_entity = result.get("dead")

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameState.PLAYER_DEAD:
                                break
                    if game_state == GameState.PLAYER_DEAD:
                        break
            else:
                game_state = GameState.PLAYER_TURN
