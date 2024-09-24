from random import randint, choice
from enum import Enum


class SuperAbility(Enum):
    CRITICAL_DAMAGE = 1
    BOOST = 2
    HEAL = 3
    SAVE_DAMAGE_AND_REVERT = 4


class GameEntity:
    def __init__(self, name, health, damage):
        self.__name = name
        self.__health = health
        self.__damage = damage
    
    @property
    def name(self):
        return self.__name
    
    @property
    def health(self):
        return self.__health
    
    @health.setter
    def health(self, value):
        self.__health = value
    
    @property
    def damage(self):
        return self.__damage
    
    @damage.setter
    def damage(self, value):
        self.__damage = value

    def __str__(self) -> str:
        return f'{self.__name} health: {self.__health} damage: {self.__damage} '
    
class Boss(GameEntity):
    def __init__(self, name, health, damage):
        super().__init__(name, health, damage)
        self.__defence = None
    
    @property
    def defence(self):
        return self.__defence
    
    def choose_defence(self, heroes):
        hero = choice(heroes)
        self.__defence = hero.super_ability


    def hit(self, heroes):
        for hero in heroes:
            if hero.health > 0:
                hero.health -= self.damage

    def __str__(self):
        return f'BOSS ' + super().__str__() + f'defence: {self.__defence}'


class Hero(GameEntity):
    def __init__(self, name, health, damage, super_ability):
        super().__init__(name, health, damage)
        if not isinstance(super_ability, SuperAbility):
            raise ValueError('Ability must be of type SuperAbility')
        else: 
            self.__super_ability = super_ability 

    
    def hit(self, boss):
        if boss.defence != self.super_ability:
            boss.health -= self.damage
    
    @property
    def super_ability(self):
        return self.__super_ability
    

    def apply_super_power(self, boss, heroes):
        pass

class Warrior(Hero):
    def __init__(self, name, health, damage):
        super().__init__(name, health, damage, SuperAbility.CRITICAL_DAMAGE)

    
    def apply_super_power(self, boss, heroes):
        pass


class Magic(Hero):
    def __init__(self, name, health, damage):
        super().__init__(name, health, damage, SuperAbility.BOOST)

    
    def apply_super_power(self, boss, heroes):
        pass


class Medic(Hero):
    def __init__(self, name, health, damage, heal_points):
        super().__init__(name, health, damage, SuperAbility.HEAL)
        self.__heal_points = heal_points
    
    def apply_super_power(self, boss, heroes):
        pass


class Berserk(Hero):
    def __init__(self,  name, health, damage,):
        super().__init__(name, health, damage, SuperAbility.SAVE_DAMAGE_AND_REVERT)
        self.__saved_damage = 0

    def apply_super_power(self, boss, heroes):
        pass

round_counter = 0

def print_statistics(boss, heroes):
    print('Round ' + str(round_counter) + ' -----------------------------------------')
    print(boss)
    for hero in heroes:
        print(hero)

def is_game_finished(boss, heroes):
    if boss.health <= 0:
        print('Boss defeated, good job')
        return True
    all_heroes_dead = True
    for hero in heroes:
        if hero.health > 0:
            all_heroes_dead = False
            break
    if all_heroes_dead:
        print('END GAME! LOOSER')
    return all_heroes_dead


def play_round(boss, heroes):
    global round_counter
    round_counter += 1
    boss.choose_defence(heroes)
    boss.hit(heroes)
    for hero in heroes:
        if hero.health > 0:
            hero.hit(boss)
            hero.apply_super_power(boss, heroes)
    print_statistics(boss, heroes)



def start_game():
    boss = Boss('Rashan', 1000, 100)
    warrior = Warrior('Konor', 280, 10)
    doc = Medic('Hous', 250, 5, 15)
    berserk = Berserk('Hiccup', 260, 15)
    magic = Magic('Invoker', 270, 20)
    assistant = Medic('Morty', 290, 5, 5)
    heroes = [warrior, doc, berserk, magic, assistant]
    print_statistics(boss, heroes)
    
    while not is_game_finished(boss, heroes):
        play_round(boss, heroes)




start_game()
