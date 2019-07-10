import tcod

from ..game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):
        self.hp -= amount

        results = []
        if self.hp <= 0:
            results.append({"dead": self.owner})

        return results

    def attack(self, target):
        damage = self.power - target.fighter.defense

        results = []
        if damage > 0:
            message = Message(
                "{} attacks {} for {} hit points.".format(self.owner.name.capitalize(), target.name, damage), tcod.white
            )
            results.append({"message": message})
            results.extend(target.fighter.take_damage(damage))

        else:
            message = Message(
                "{} attacks {} but does no damage.".format(self.owned.name.capitalize(), target.name), tcod.white
            )
            results.append({"message": message})
        return results
