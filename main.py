# IMPORT SECTION

import sys
from enum import Enum
from operator import attrgetter, itemgetter
import itertools
import random

# DEFINITIONS
LOW_COST = 4        # 0 - LOW_COST
MID_COST = 7        # (LOW_COST + 1) - MID_COST
HIGH_COST = 12      # (MID_COST + 1) - 12

cards_by_cost = [0, 0, 0]   # LOW, MID, HIGH
max_cards_by_cost = [8, 8, 8]

cards_by_type = [0, 0, 0, 0]
max_cards_by_type = [24, 4, 4, 4]    # CREATURES / ITEMS


BREAKTHROUGH_IMPACT = 1
CHARGE_IMPACT = 2
GUARD_IMPACT = 2
DRAIN_IMPACT = 2
LETHAL_IMPACT = 1
WARD_IMPACT = 1

SILENCE_ITEMS = [142, 148, 149]
REMOVAL = 151

# CLASSES

class Location(Enum):
    IN_HAND = 0
    ON_MY_BOARD = 1
    ON_OPPONENT_BOARD = -1


class CardType(Enum):
    CREATURE = 0
    GREEN_ITEM = 1
    RED_ITEM = 2
    BLUE_ITEM = 3


class Player:
    health = 0
    mana = 0
    deck = 0
    rune = 0


class Card:
    cid = 0
    ID = 0
    location = Location.IN_HAND
    ctype = CardType.CREATURE
    cost = 0
    attack = 0
    health = 0
    abilities = ""
    health_change = 0
    opponent_health_change = 0
    draw = 0

    def has_ability(self, c):
        return c in self.abilities

    def can_use(self):
        return self.cost <= me.mana

    def can_summon(self):
        return self.can_use()


class Creature(Card):

    def __init__(self, card):
        self.cid = card.cid
        self.ID = card.ID
        self.location = card.location
        self.ctype = card.ctype
        self.cost = card.cost
        self.attack = card.attack
        self.health = card.health
        self.abilities = card.abilities
        self.health_change = card.health_change
        self.opponent_health_change = card.opponent_health_change
        self.draw = card.draw

    def strike(self, opponent_creature):
        global result_str

        __self_striked = False
        __opponent_creature_striked = False

        if opponent_creature.has_ability('W'):
            if self.attack > 0:
                opponent_creature.abilities.replace('W', '-')
        else:
            if self.attack > 0:
                opponent_creature.health -= self.attack
                __opponent_creature_striked = True

        if self.has_ability('W'):
            if opponent_creature.attack > 0:
                self.abilities.replace('W', '-')
        else:
            if opponent_creature.attack > 0:
                self.health -= opponent_creature.attack
                __self_striked = True

        if self.has_ability('L') and __opponent_creature_striked:
            opponent.health = 0

        if opponent_creature.has_ability('L') and __self_striked:
            self.health = 0

        if self.has_ability('B') and opponent.health < 0:
            opponent.health += opponent.health

        if self.has_ability('D') and __opponent_creature_striked:
            me.health += self.attack

        result_str += 'ATTACK {} {};'.format(self.cid, opponent_creature.cid)


    def strike_to_face(self):
        global result_str

        opponent.health -= self.attack

        result_str += 'ATTACK {} -1;'.format(self.cid)

    def summon(self):
        global result_str

        me.mana -= self.cost

        result_str += 'SUMMON {};'.format(self.cid)


class GreenItem(Card):

    def __init__(self, card):
        self.cid = card.cid
        self.ID = card.ID
        self.location = card.location
        self.ctype = card.ctype
        self.cost = card.cost
        self.attack = card.attack
        self.health = card.health
        self.abilities = card.abilities
        self.health_change = card.health_change
        self.opponent_health_change = card.opponent_health_change
        self.draw = card.draw

    def use(self, target_creature):
        global result_str

        me.mana -= self.cost

        target_creature.attack += self.attack
        target_creature.health += self.health

        for index, ability in enumerate(self.abilities):
            if ability != '-':
                target_creature.abilities = target_creature.abilities[:index] + ability + target_creature.abilities[index + 1:]

        me.health += self.health_change

        result_str += 'USE {} {};'.format(self.cid, target_creature.cid)


class RedItem(Card):

    def __init__(self, card):
        self.cid = card.cid
        self.ID = card.ID
        self.location = card.location
        self.ctype = card.ctype
        self.cost = card.cost
        self.attack = card.attack
        self.health = card.health
        self.abilities = card.abilities
        self.health_change = card.health_change
        self.opponent_health_change = card.opponent_health_change
        self.draw = card.draw

    def use(self, target_creature):
        global result_str

        me.mana -= self.cost

        target_creature.attack += self.attack
        target_creature.health += self.health

        for _, ability in enumerate(self.abilities):
            if ability != '-':
                target_creature.abilities.replace(ability, '-')

        opponent.health += self.opponent_health_change

        result_str += 'USE {} {};'.format(self.cid, target_creature.cid)


class BlueItem(Card):

    def __init__(self, card):
        self.cid = card.cid
        self.ID = card.ID
        self.location = card.location
        self.ctype = card.ctype
        self.cost = card.cost
        self.attack = card.attack
        self.health = card.health
        self.abilities = card.abilities
        self.health_change = card.health_change
        self.opponent_health_change = card.opponent_health_change
        self.draw = card.draw

    def use_to_creature(self, target_creature):
        global result_str

        me.mana -= self.cost

        target_creature.health += self.health

        me.health += self.health_change
        opponent.health += self.opponent_health_change

        result_str += 'USE {} {};'.format(self.cid, target_creature.cid)

    def use_to_face(self):
        global result_str

        me.mana -= self.cost

        me.health += self.health_change
        opponent.health += self.opponent_health_change

        opponent.health += self.health

        result_str += 'USE {} -1;'.format(self.cid)


locations = {
    0: Location.IN_HAND,
    1: Location.ON_MY_BOARD,
    -1: Location.ON_OPPONENT_BOARD,
}

card_types = {
    0: CardType.CREATURE,
    1: CardType.GREEN_ITEM,
    2: CardType.RED_ITEM,
    3: CardType.BLUE_ITEM,
}


def get_cost_category(card):
    if card.cost <= LOW_COST:
        return 0
    elif card.cost <= MID_COST:
        return 1
    else:
        return 2


def filter_by_cost(cards):
    result = []

    for card in cards:
        if cards_by_cost[get_cost_category(card)] < max_cards_by_cost[get_cost_category(card)]:
            result.append(card)

    return result


def filter_by_type(cards):
    result = []

    for card in cards:
        if cards_by_type[int(card.ctype.value)] < max_cards_by_type[int(card.ctype.value)]:
            result.append(card)

    return result


def get_impact(card):
    if card.ctype == CardType.CREATURE:

        impact = card.attack + card.health
        if card.has_ability('B'):
            impact += BREAKTHROUGH_IMPACT
        if card.has_ability('C'):
            impact += CHARGE_IMPACT
        if card.has_ability('G'):
            impact += GUARD_IMPACT
        if card.has_ability('D'):
            impact += DRAIN_IMPACT
        if card.has_ability('L'):
            impact += LETHAL_IMPACT
        if card.has_ability('W'):
            impact += WARD_IMPACT

        impact += card.health_change / 2
        impact -= card.opponent_health_change / 2

        impact += card.draw

        if card.attack * 3 < card.health:
            impact -= 2

        if card.health * 2 < card.attack:
            impact -= 2

        return impact / (card.cost + 1)

    elif card.ctype == CardType.GREEN_ITEM:
        impact = card.attack + card.health
        if card.has_ability('B'):
            impact += BREAKTHROUGH_IMPACT
        if card.has_ability('C'):
            impact += CHARGE_IMPACT
        if card.has_ability('G'):
            impact += GUARD_IMPACT
        if card.has_ability('D'):
            impact += DRAIN_IMPACT
        if card.has_ability('L'):
            impact += LETHAL_IMPACT
        if card.has_ability('W'):
            impact += WARD_IMPACT

        return impact / (card.cost + 1)

    elif card.ctype == CardType.RED_ITEM:
        impact = (-card.attack) + (-card.health)

        if card.abilities != '------':
            impact += 2

        impact += -card.opponent_health_change

        return impact / (card.cost + 1)

    else:
        impact = -card.health

        impact += card.health_change
        impact += -card.opponent_health_change

        return impact / (card.cost + 1)


def filter_card_by_can_played(cards, current_mana):
    return [card for card in cards if card.cost <= current_mana]


def possible_success_attack(my_card, opponent_card):
    if my_card.has_ability('W'):
        if my_card.attack >= opponent_card.health and not opponent_card.has_ability('W'):
            return True
        elif opponent_card.has_ability('W') and get_impact(my_card) < get_impact(opponent_card):
            return True
        else:
            return False
    else:
        if my_card.attack <= 2 and opponent_card.has_ability('W'):
            return True
        if my_card.attack >= opponent_card.health and my_card.health > opponent_card.attack and \
                not opponent_card.has_ability('W'):

            return True

        if my_card.attack >= opponent_card.health and my_card.health == opponent_card.attack and \
                not opponent_card.has_ability('W') and my_card.attack < opponent_card.attack:

            return True

        if my_card.attack >= opponent_card.health and my_card.health < opponent_card.attack and \
                not opponent_card.has_ability('W'):

            return True

    return False


def get_best_target(creature, opponent_creatures, opponent_guards, my_guards):

    if creature.has_ability('L'):
        if len(opponent_guards) > 0:
            opponent_guards.sort(key=attrgetter('cost'), reverse=True)
            for opponent_guard in opponent_guards:
                if not opponent_guard.has_ability('W'):
                    return opponent_guard

            return None

        opponent_creatures.sort(key=attrgetter('cost'), reverse=True)
        for opponent_creature in opponent_creatures:
            if not opponent_creature.has_ability('W') and creature.cost <= opponent_creature.cost:
                return opponent_creature

        return None

    # ELSE

    if sum([creature.health for creature in my_guards]) > sum([creature.attack for creature in opponent_creatures]) and \
        len(opponent_guards) == 0:

        return -1

    opponent_guards.sort(key=attrgetter('cost'), reverse=True)
    opponent_creatures.sort(key=attrgetter('cost'), reverse=True)

    if creature.health == 1 and creature.attack >= 3:
        if len(opponent_guards) > 0:
            return opponent_guards[0]
        return -1

    for opponent_guard in opponent_guards:
        if possible_success_attack(creature, opponent_guard):
            return opponent_guard

    if len(opponent_guards) == 0:
        for opponent_creature in opponent_creatures:
            if possible_success_attack(creature, opponent_creature):
                return opponent_creature

        return -1

    for opponent_guard in opponent_guards:
        if (creature.health > opponent_guard.attack or creature.has_ability('W')) and not creature.has_ability('G'):
            return opponent_guard

    if len(opponent_guards) == 0:
        for opponent_creature in opponent_creatures:
            if (creature.health > opponent_creature.attack or creature.has_ability('W')) and not creature.has_ability('G'):
                return opponent_creature

        return -1
    return None



# GLOBAL VARIABLES

me = Player()
opponent = Player()


# GAME LOOP

draft_turn = 0

while True:

    opponent_creatures = []
    opponent_guards = []

    my_creatures = []
    my_guards = []

    cards_in_my_hand = []
    creatures_in_hand = []
    green_items_in_hand = []
    red_items_in_hand = []
    blue_items_in_hand = []

    me.health, me.mana, me.deck, me.rune = [int(j) for j in input().split()]
    opponent.health, opponent.mana, opponent.deck, opponent.rune = [int(j) for j in input().split()]

    opponent_hand = int(input())
    card_count = int(input())

    for _ in range(card_count):
        card = Card()
        card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
        card.ID = int(card_number)
        card.cid = int(instance_id)
        card.location = locations[int(location)]
        card.ctype = card_types[int(card_type)]
        card.cost = int(cost)
        card.attack = int(attack)
        card.health = int(defense)
        card.abilities = abilities
        card.health_change = int(my_health_change)
        card.opponent_health_change = int(opponent_health_change)
        card.draw = int(card_draw)

        if card.location == Location.ON_OPPONENT_BOARD:
            creature = Creature(card)
            opponent_creatures.append(creature)

            if creature.has_ability('G'):
                opponent_guards.append(creature)

        if card.location == Location.ON_MY_BOARD:
            creature = Creature(card)
            my_creatures.append(creature)

            if creature.has_ability('G'):
                my_guards.append(creature)

        if card.location == Location.IN_HAND:
            cards_in_my_hand.append(card)

            if card.ctype == CardType.CREATURE:
                creatures_in_hand.append(Creature(card))
            elif card.ctype == CardType.GREEN_ITEM:
                green_items_in_hand.append(GreenItem(card))
            elif card.ctype == CardType.RED_ITEM:
                red_items_in_hand.append(RedItem(card))
            elif card.ctype == CardType.BLUE_ITEM:
                blue_items_in_hand.append(BlueItem(card))


    if draft_turn < 30:

        filtered_cards = cards_in_my_hand[:]
        filtered_cards.sort(key=lambda card: get_impact(card), reverse=True)
        print([get_impact(card) for card in filtered_cards], file=sys.stderr)

        cards_by_type[int(filtered_cards[0].ctype.value)] += 1
        cards_by_cost[get_cost_category(filtered_cards[0])] += 1

        print('PICK {}'.format(cards_in_my_hand.index(filtered_cards[0])))
        print('CREATURES = {}, GREEN = {}, RED = {}, BLUE = {}'.format(cards_by_type[0], cards_by_type[1],
                                                                       cards_by_type[2],cards_by_type[3]),
              file=sys.stderr)
        print('LOW = {}, MID = {}, HIGH = {}'.format(cards_by_cost[0], cards_by_cost[1], cards_by_cost[2]),
              file=sys.stderr)

        draft_turn += 1
        continue


    result_str = ""

    # USE RED ITEMS ON OPPONENT GUARDS

    if len(opponent_guards) > 0 and len(red_items_in_hand) > 0:

        silence_items = [item for item in red_items_in_hand if item.ID in SILENCE_ITEMS]
        if len(silence_items) > 0:
            if silence_items[0].can_use():
                opponent_guards.sort(key=get_impact, reverse=True)
                silence_items[0].use(opponent_guards[0])
                if opponent_guards[0].health <= 0:
                    opponent_creatures.remove(opponent_guards[0])
                opponent_guards.remove(opponent_guards[0])
                red_items_in_hand.remove(silence_items[0])

        removal_items = [item for item in red_items_in_hand if item.ID == REMOVAL]
        if len(removal_items) > 0:
            opponent_guards.sort(key=get_impact, reverse=True)
            if removal_items[0].can_use() and opponent_guards[0].cost > 6:
                removal_items[0].use(opponent_guards[0])

                opponent_creatures.remove(opponent_guards[0])
                opponent_guards.remove(opponent_guards[0])

                red_items_in_hand.remove(removal_items[0])


    # USE GREEN ITEMS ON MY CREATURES

    if len(green_items_in_hand) > 0:
        green_items_in_hand.sort(key=attrgetter('cost'))
        my_guards.sort(key=attrgetter('cost'), reverse=True)

        my_drain_creatures = [creature for creature in my_creatures if creature.has_ability('D')]

        if len(my_guards) > 0:
            if green_items_in_hand[0].can_use():
                green_items_in_hand[0].use(my_guards[0])
                green_items_in_hand.remove(green_items_in_hand[0])

        elif len(my_drain_creatures) > 0:
            if green_items_in_hand[0].can_use():
                green_items_in_hand[0].use(my_drain_creatures[0])
                green_items_in_hand.remove(green_items_in_hand[0])


    # TRY SUMMON

    quad_cost = -1
    cards_to_summon = []

    creatures_in_hand.sort(key=attrgetter('cost'), reverse=True)
    for i in range(len(creatures_in_hand)):
        for cards in itertools.combinations(creatures_in_hand, i):
            if sum([card.cost for card in cards]) > me.mana:
                continue

            current_quad_cost = sum([card.cost ** 2 for card in cards])
            if current_quad_cost > quad_cost:
                quad_cost = current_quad_cost
                cards_to_summon = cards

    for creature in cards_to_summon:
        if creature.can_summon():
            creature.summon()
            if creature.has_ability('G'):
                my_guards.append(creature)
            if creature.has_ability('C'):
                my_creatures.append(creature)

    # IF WE HAVE MANA > 0

    if me.mana > 0:

        if len(blue_items_in_hand) > 0:
            for item in blue_items_in_hand:
                if item.can_use():
                    item.use_to_face()
                    blue_items_in_hand.remove(item)

        if len(green_items_in_hand) > 0:
            for item in green_items_in_hand:
                if item.can_use() and len(my_creatures) > 0:
                    item.use(random.choice(my_creatures))
                    green_items_in_hand.remove(item)

        if len(red_items_in_hand) > 0:
            for item in red_items_in_hand:
                if item.ID in SILENCE_ITEMS:
                    continue
                if item.can_use() and len(opponent_creatures) > 0:
                    opponent_creature = random.choice(opponent_creatures)
                    item.use(opponent_creature)
                    red_items_in_hand.remove(item)

                    if opponent_creature.health <= 0:
                        opponent_creatures.remove(opponent_creature)

                        if opponent_creature in opponent_guards:
                            opponent_guards.remove(opponent_creature)



    # ATTACK


    for _ in range(6):
        for my_creature in my_creatures:

            if len(opponent_guards) == 0 and sum([creature.attack for creature in my_creatures]) >= opponent.health:
                for creature in my_creatures:
                    creature.strike_to_face()
                break


            target = get_best_target(my_creature, opponent_creatures, opponent_guards, my_guards)

            if target == -1:
                my_creature.strike_to_face()
                my_creatures.remove(my_creature)

            elif target != None:
                my_creature.strike(target)

                my_creatures.remove(my_creature)
                if target.health <= 0:
                    opponent_creatures.remove(target)

                    if target in opponent_guards:
                        opponent_guards.remove(target)

                if my_creature.health <= 0 and my_creature in my_guards:
                    my_guards.remove(my_creature)

            continue

    for my_creature in my_creatures:
        my_creature.strike_to_face()

    if result_str != "":
        print(result_str)
    else:
        print("PASS")







































