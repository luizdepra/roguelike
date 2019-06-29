import tcod

from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all


SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 10

COLORS = {
    'dark_wall': tcod.Color(0, 0, 100),
    'dark_ground': tcod.Color(50, 50, 150),
    'light_wall': tcod.Color(130, 110, 50),
    'light_ground': tcod.Color(200, 180, 50),
}


def main():
    player = Entity(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', tcod.white)
    npc = Entity(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2, '@', tcod.yellow)
    entities = [npc, player]

    tcod.console_set_custom_font(
        "assets/fonts/arial10x10.png",
        tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD,
    )

    tcod.console_init_root(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        "Roguelike Tutorial",
        False,
    )

    con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)
    game_map.make_map(
        MAX_ROOMS,
        ROOM_MIN_SIZE,
        ROOM_MAX_SIZE,
        MAP_WIDTH,
        MAP_HEIGHT,
        player
    )

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(
                fov_map,
                player.x,
                player.y,
                FOV_RADIUS,
                FOV_LIGHT_WALLS,
                FOV_ALGORITHM
            )

        render_all(
            con,
            entities,
            game_map,
            fov_map,
            fov_recompute,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            COLORS
        )

        fov_recompute = False

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)
                fov_recompute = True

        if exit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


if __name__ == '__main__':

    main()
