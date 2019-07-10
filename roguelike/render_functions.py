from enum import Enum

import tcod


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [
        entity.name
        for entity in entities
        if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)
    ]
    names = ", ".join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(
        panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER, f"{name}: {value}/{maximum}"
    )


def render_all(
    con,
    panel,
    entities,
    player,
    game_map,
    fov_map,
    fov_recompute,
    message_log,
    screen_width,
    screen_height,
    bar_width,
    panel_height,
    panel_y,
    mouse,
    colors,
):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    color = "light_wall" if wall else "light_ground"
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    color = "dark_wall" if wall else "dark_ground"
                else:
                    continue

                tcod.console_set_char_background(con, x, y, colors.get(color), tcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)

    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, get_names_under_mouse(mouse, entities, fov_map))

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    if not tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        return

    tcod.console_set_default_foreground(con, entity.color)
    tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, " ", tcod.BKGND_NONE)
