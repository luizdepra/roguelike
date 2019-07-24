import os
import shelve

SAVE_FILE_NAME = "game_save.dat"


def save_game(player, entities, game_map, message_log, game_state):
    with shelve.open(SAVE_FILE_NAME, "n") as data_file:
        data_file["player_index"] = entities.index(player)
        data_file["entities"] = entities
        data_file["game_map"] = game_map
        data_file["message_log"] = message_log
        data_file["game_state"] = game_state


def load_game():
    if not os.path.isfile(SAVE_FILE_NAME):
        raise FileNotFoundError

    with shelve.open(SAVE_FILE_NAME, "r") as data_file:
        player_index = data_file["player_index"]
        entities = data_file["entities"]
        game_map = data_file["game_map"]
        message_log = data_file["message_log"]
        game_state = data_file["game_state"]

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state
