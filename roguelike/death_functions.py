import tcod

from .game_states import GameState
from .render_functions import RenderOrder


def kill_player(player):
    player.char = "%"
    player.color = tcod.dark_red

    return "You died!", GameState.PLAYER_DEAD


def kill_monster(monster):
    name = monster.name.capitalize()
    death_message = f"{name} is dead!"

    monster.char = "%"
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"Remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE

    return death_message
