import tcod

from input_handlers import handle_keys


SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50


def main():
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2

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

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        tcod.console_set_default_foreground(con, tcod.white)
        tcod.console_put_char(con, player_x, player_y, "@", tcod.BKGND_NONE)
        tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        tcod.console_flush()

        tcod.console_put_char(con, player_x, player_y, " ", tcod.BKGND_NONE)

        action = handle_keys(key)

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        if move:
            dx, dy = move
            player_x += dx
            player_y += dy

        if exit:
            return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


if __name__ == '__main__':

    main()
