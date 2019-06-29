import tcod


def render_all(
    con,
    entities,
    game_map,
    fov_map,
    fov_recompute,
    screen_width,
    screen_height,
    colors
):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    color = 'light_wall' if wall else 'light_ground'
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    color = 'dark_wall' if wall else 'dark_ground'
                else:
                    continue

                tcod.console_set_char_background(
                    con,
                    x,
                    y,
                    colors.get(color),
                    tcod.BKGND_SET
                )

    for entity in entities:
        draw_entity(con, entity, fov_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):
    if not tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        return

    tcod.console_set_default_foreground(con, entity.color)
    tcod.console_put_char(
        con,
        entity.x,
        entity.y,
        entity.char,
        tcod.BKGND_NONE
    )


def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
