class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


def get_blocking_entities_at_location(entities, destionation_x, destionation_y):
    for entity in entities:
        if entity.blocks and entity.x == destionation_x and entity.y == destionation_y:
            return entity

    return None
