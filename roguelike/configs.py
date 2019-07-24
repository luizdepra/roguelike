import tcod

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


def get_configs():
    return {
        "window_title": "Roguelike Tutorial Revised",
        "screen_width": SCREEN_WIDTH,
        "screen_height": SCREEN_HEIGHT,
        "bar_width": BAR_WIDTH,
        "panel_height": PANEL_HEIGHT,
        "panel_y": PANEL_Y,
        "message_x": MESSAGE_X,
        "message_width": MESSAGE_WIDTH,
        "message_height": MESSAGE_HEIGHT,
        "map_width": MAP_WIDTH,
        "map_height": MAP_HEIGHT,
        "room_max_size": ROOM_MAX_SIZE,
        "room_min_size": ROOM_MIN_SIZE,
        "max_rooms": MAX_ROOMS,
        "fov_algorithm": FOV_ALGORITHM,
        "fov_light_walls": FOV_LIGHT_WALLS,
        "fov_radius": FOV_RADIUS,
        "max_monsters_per_room": MAX_MONSTERS_PER_ROOM,
        "max_items_per_room": MAX_ITEMS_PER_ROOM,
        "colors": COLORS,
    }
