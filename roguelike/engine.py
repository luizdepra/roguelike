import tcod

from .configs import get_configs
from .death_functions import kill_monster, kill_player
from .entity import get_blocking_entities_at_location
from .fov_functions import initialize_fov, recompute_fov
from .game_messages import Message
from .game_states import GameState
from .input_handlers import handle_keys, handle_main_menu, handle_mouse
from .loader_functions.data_loaders import load_game, save_game
from .loader_functions.initialize_new_game import get_game_variables
from .menus import main_menu, message_box
from .render_functions import clear_all, render_all


def play_game(player, entities, game_map, message_log, game_state, con, panel, configs):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    previous_game_state = game_state

    targeting_item = None

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(
                fov_map, player.x, player.y, configs["fov_radius"], configs["fov_light_walls"], configs["fov_algorithm"]
            )

        render_all(
            con,
            panel,
            entities,
            player,
            game_map,
            fov_map,
            fov_recompute,
            message_log,
            configs["screen_width"],
            configs["screen_height"],
            configs["bar_width"],
            configs["panel_height"],
            configs["panel_y"],
            mouse,
            configs["colors"],
            game_state,
        )

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get("move")
        wait = action.get("wait")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        take_stairs = action.get("take_stairs")
        level_up = action.get("level_up")
        show_character_screen = action.get("show_character_screen")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        left_click = mouse_action.get("left_click")
        right_click = mouse_action.get("right_click")

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
        elif wait:
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
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameState.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if take_stairs and game_state == GameState.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, configs)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    tcod.console_clear(con)
                    break
                else:
                    message_log.add_message(Message("There are no stairs here.", tcod.yellow))

        if level_up:
            if level_up == "hp":
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == "str":
                player.fighter.base_power += 1
            elif level_up == "def":
                player.fighter.base_defense += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameState.CHARACTER_SCREEN

        if game_state == GameState.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(
                    targeting_item, entities=entities, fov_map=fov_map, target_x=target_x, target_y=target_y
                )
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({"targeting_cancelled": True})

        if exit:
            if game_state in (GameState.SHOW_INVENTORY, GameState.DROP_INVENTORY, GameState.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameState.TARGETING:
                player_turn_results.append({"targeting_cancelled": True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for result in player_turn_results:
            message = result.get("message")
            dead_entity = result.get("dead")
            item_added = result.get("item_added")
            item_consumed = result.get("consumed")
            item_dropped = result.get("item_dropped")
            equip = result.get("equip")
            targeting = result.get("targeting")
            targeting_cancelled = result.get("targeting_cancelled")
            xp = result.get("xp")

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message("Targeting cancelled"))

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

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_results in equip_results:
                    equipped = equip_results.get("equipped")
                    dequipped = equip_results.get("dequipped")

                    if equipped:
                        message_log.add_message(Message(f"You equipped the {equipped.name}."))

                    if dequipped:
                        message_log.add_message(Message(f"You dequipped the {dequipped.name}."))

                game_state - GameState.ENEMY_TURN

            if targeting:
                previous_game_state = GameState.PLAYER_TURN
                game_state = GameState.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message(f"You gain {xp} experience points."))

                if leveled_up:
                    message_log.add_message(
                        Message(
                            f"Your battle skills grow strong! You reached level {player.level.current_level}!",
                            tcod.yellow,
                        )
                    )
                    previous_game_state = game_state
                    game_state = GameState.LEVEL_UP

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


def main():
    configs = get_configs()

    tcod.console_set_custom_font("assets/fonts/arial10x10.png", tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(configs["screen_width"], configs["screen_height"], configs["window_title"], False)

    con = tcod.console_new(configs["screen_width"], configs["screen_height"])
    panel = tcod.console_new(configs["screen_width"], configs["screen_height"])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load("assets/images/menu_background.png")

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, configs["screen_width"], configs["screen_height"])

            if show_load_error_message:
                message_box(con, "No save game to load", 50, configs["screen_width"], configs["screen_height"])

            tcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get("new_game")
            load_saved_game = action.get("load_game")
            exit_game = action.get("exit")

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(configs)
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            tcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, configs)

            show_main_menu = True
