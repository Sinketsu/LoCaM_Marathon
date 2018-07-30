import sys
from enum import Enum
from operator import attrgetter, itemgetter


class Location(Enum):
    IN_HAND = 0
    ON_MY_BOARD = 1
    ON_OPPONENT_BOARD = -1


class Player:
    health = 0
    mana = 0
    deck = 0
    rune = 0


class Card:
    cid = 0
    instanse = 0
    location = Location.IN_HAND
    ctype = 0
    cost = 0
    attack = 0
    health = 0
    abilities = ""
    health_change = 0
    opponent_health_change = 0
    draw = 0

    def has_abality(self, c):
        return c in abilities



locations = {
    0: Location.IN_HAND,
    1: Location.ON_MY_BOARD,
    -1: Location.ON_OPPONENT_BOARD,
}


def sort_by_cost(card):
    return card.cost


def sort_by_damage(card):
    return card.attack


def sort_by_hp(card):
    return card.health


def possible_success_attack(my_card, opponent_card):
    if my_card.attack >= opponent_card.health and my_card.health < opponent_card.attack:
        return True
    if my_card.attack >= opponent_card.health and my_card.health > opponent_card.attack:
        return True
    return False


me = Player()
opponent = Player()

draft_turn = 0

while True:

    cards_in_hand = []
    creatures = []
    opponent_creatures = []

    me.health, me.mana, me.deck, me.rune = [int(j) for j in input().split()]
    opponent.health, opponent.mana, opponent.deck, opponent.rune = [int(j) for j in input().split()]

    opponent_hand = int(input())
    card_count = int(input())

    for i in range(card_count):
        card = Card()
        card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
        card.instanse = int(card_number)
        card.cid = int(instance_id)
        card.location = locations[int(location)]
        card.ctype = int(card_type)
        card.cost = int(cost)
        card.attack = int(attack)
        card.health = int(defense)
        card.abilities = abilities
        card.health_change = int(my_health_change)
        card.opponent_health_change = int(opponent_health_change)
        card.draw = int(card_draw)

        if card.location == Location.IN_HAND:
            cards_in_hand.append(card)
        elif card.location == Location.ON_MY_BOARD:
            creatures.append(card)
        else:
            opponent_creatures.append(card)

    if draft_turn < 30:
        impact = 0
        idx = 0

        for index, card in enumerate(cards_in_hand):
            if card.ctype != 0:
                continue
            current_impact = card.attack + card.health
            card.cost += 1
            if 'G' in card.abilities:
                current_impact += 2
            if 'C' in card.abilities:
                current_impact += 1
            current_impact /= card.cost

            if current_impact > impact and card.health <= 2 * card.attack and card.attack <= 3 * card.health and not (
                    card.cost == 1 and 'G' not in card.abilities):
                impact = current_impact
                idx = index

        print("PICK {}".format(idx))

        draft_turn += 1
        continue

    print("MY MANA = ", me.mana, file=sys.stderr)

    result_str = ""

    cards_in_hand.sort(key=sort_by_cost, reverse=True)
    creatures_to_summon = []

    for index, card in enumerate(cards_in_hand):
        if card.cost <= me.mana:
            creatures_to_summon.append(card.cid)
            if 'C' in card.abilities:
                creatures.append(card)
            me.mana -= card.cost

    for cid in creatures_to_summon:
        result_str += "SUMMON {};".format(cid)

    # try defeat guards
    opponent_guards = []
    for card in opponent_creatures:
        if 'G' in card.abilities:
            opponent_guards.append(card)

    if len(opponent_guards) != 0:
        for guard in opponent_guards:
            for card in creatures:
                if possible_success_attack(card, guard):
                    result_str += "ATTACK {} {};".format(card.cid, guard.cid)
                    opponent_guards.remove(guard)
                    creatures.remove(card)
                    break

    print(len(opponent_guards), file=sys.stderr)

    opponent_guards.sort(key=sort_by_hp)
    creatures.sort(key=sort_by_damage)
    if len(opponent_guards) != 0:
        for guard in opponent_guards:
            for card in creatures:
                if card.attack >= guard.health:
                    result_str += "ATTACK {} {};".format(card.cid, guard.cid)
                    opponent_guards.remove(guard)
                    creatures.remove(card)
                    break

    if len(opponent_guards) != 0:
        if len(creatures) != 0:
            result_str += "ATTACK {} {};".format(creatures[0].cid, opponent_guards[0].cid)
            opponent_guards[0].health -= creatures[0].attack
            creatures.remove(creatures[0])
        if len(creatures) != 0:
            result_str += "ATTACK {} {};".format(creatures[0].cid, opponent_guards[0].cid)
            opponent_guards[0].health -= creatures[0].attack
            creatures.remove(creatures[0])
            if opponent_guards[0].health <= 0:
                opponent_guards.remove(opponent_guards[0])

    max_my_dmg = sum([card.attack for card in creatures])
    if max_my_dmg >= opponent.health and len(opponent_guards) == 0:  # if we have a lethal
        for card in creatures:
            result_str += "ATTACK {} -1;".format(card.cid)  # attack all creatures to face

    else:
        defeated_creatures = []
        creatures.sort(key=sort_by_damage)
        for card in creatures:
            for opponent_creature in opponent_creatures:
                if possible_success_attack(card, opponent_creature) and opponent_creature not in defeated_creatures:
                    result_str += "ATTACK {} {};".format(card.cid, opponent_creature.cid)
                    defeated_creatures.append(opponent_creature)
                    break
            else:
                result_str += "ATTACK {} -1;".format(card.cid)

    if result_str != "":
        print(result_str)
    else:
        print("PASS")
