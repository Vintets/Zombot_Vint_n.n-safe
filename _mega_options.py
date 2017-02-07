#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from ctypes import windll
import sys
import re
from game_state.game_types import GameWoodTree, GameStone

if True:
    from game_actors_and_handlers.gifts import GiftReceiverBot, FreeGifts, SendCollections, SendColl, GiftsToFake
    from game_actors_and_handlers.cakes_receiver import CakesReceiverBot
    from game_actors_and_handlers.plants import HarvesterBot, SeederBot, GameSeedReader, UseEggItemBot,\
        FertilBot, FertilPlantBot, FertilPlantGreenBot, ScrollBot
    from game_actors_and_handlers.roulettes import RouletteRoller, RouletteTavernaDub
    from game_actors_and_handlers.wood_graves import WoodPicker, WoodTargetSelecter
    from game_actors_and_handlers.cook_graves import BrewPicker, CookerBot, RecipeReader, CookSpeed
    from game_actors_and_handlers.digger_graves import BagsPicker
    from game_actors_and_handlers.stone_graves import StonePicker, StoneTargetSelecter
    from game_actors_and_handlers.pickups import Pickuper, BoxPickuper
    from game_actors_and_handlers.location import ChangeLocationBot
    from game_actors_and_handlers.friends import VisitingUsers
    from game_actors_and_handlers.wand import MagicWand
    from game_actors_and_handlers.building_buyer import BuildingBuyer
    from game_actors_and_handlers.building_tent import BuildingTent
    from game_actors_and_handlers.chop import PirateTreeCut, PirateTreeCutBroot, ShipCheck
    from game_actors_and_handlers.buffs import GameBuffFixHarvest, GameBuffDigger, GameBuffFixCook, GameTravelBuff
    from game_actors_and_handlers.burrowing import DigBot
    from game_actors_and_handlers.storage import SellBot, PutStorage
    from game_actors_and_handlers.monster_pit import MonsterPit
    from game_actors_and_handlers.premium_gifts import PremiumGifts
    from game_actors_and_handlers.tree_plant import TreePlant
    from game_actors_and_handlers.trade_graves import TradeBot, TradeSet
    from game_actors_and_handlers.A_work import Work
    from game_actors_and_handlers.buy import BuyCaravel, BuyShovel, BuyGreenFertilizer, BuyAny
    from game_actors_and_handlers.upgrade import Upgrader
    from game_actors_and_handlers.auto_pirat import AutoPirat, KnockTeam
    from game_actors_and_handlers.craft import ExchangeHarvest, ExchangeFlyingShip,\
        ExchangeInstantrert, ExchangeShovelsBamboo, ExchangeShovelsNail,\
        ExchangeEmeraldObserv, ExchangeKleverhell, ExchangeChesnLiliy,\
        ExchangeHeliya, ExchangeTomatoskulls, ExchangeTube, Exchange1in1000,\
        Exchange1000in1, ExchangeEmeraldic, ExchangeBrains, ExchangeBolt,\
        ExchangeBabel, ExchangeRubber, ExchangeTransformator, ExchangeBlueHeart,\
        ExchangeFire, ExchangeFire2, ExchangeBoard, ExchangeKraska, ExchangeDiz,\
        ExchangeTermo, ExchangeLove1, ExchangeLove2, ExchangeSuperglue, ExchangeIronHeart
    from game_actors_and_handlers.airplane_sell import TiketReceiverBot
    from game_actors_and_handlers.bolt_gift import BoltGift
    from game_actors_and_handlers.deleting_objects import DeletingObjects
    from game_actors_and_handlers.active_user import ActiveUser, FinalReportUserMR, FinalReportUserVK
    from game_actors_and_handlers.tent_circus import BowReceiverBot
    #from game_actors_and_handlers.barabashka import Barabashka
    from game_actors_and_handlers.change_palach import ChangePalach
    from game_actors_and_handlers.change_inferno import ChangeInferno
    from game_actors_and_handlers.collections_sell import Collectionsell

stdout_handle = windll.kernel32.GetStdHandle(-11)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute

logger = logging.getLogger(__name__)


class MegaOptions():
    def __init__(self,curuser):
        self.curuser = curuser
        groups = {
                'group_2':['name1', 'name2'],                               # продвинутые фейки
                'group_3':['1_', '2_', '3_', '4_', '5_'],                   # пиратская группа
                }
        self.group = self.get_group(groups)


# Управление модулями ========================================================
    # включение выключение модулей, (бывший game_engine.py)
    def actor_options(self):
        if self.group == 1: return [
                    Work,                  # Опыты и тесты
                    ActiveUser,            # Лог активности юзеров
                    # FinalReportUserMR,     # Полный отчёт о друзьях MR
                    # FinalReportUserVK,     # Полный отчёт о друзьях VK
                    # DeletingObjects,       # Удаление объектов

                    # SendCollections,       # РАЗОВО! Дарить коллекции по списку
                    # BoltGift,              # РАЗОВО! Передача другу Болтов по 1
                    # TiketReceiverBot,      # Собираем билеты, обновляем самолет/пасхальную корзинку
                    # BowReceiverBot,        # Собираем банты из циркового шатра
                    # Barabashka,            # Собираем барабашек из дома приведений
                    # VisitingUsers,         # Посещение друзей

                    # CakesReceiverBot,      # Сбор пряников
                    # GiftReceiverBot,       # Принятие подарков
                    # PremiumGifts,          # Принятие платных выставляемых подарков
                    # FreeGifts,             # Дарить бесплатки
                    # GiftsToFake,           # Дарить фейкам по списку
                    # SendColl,              # Передача коллекций (!)
                    # DigBot,                # Закапывать друзей получая мозги
                    # MonsterPit,            # Работа с Моней
                    # GameBuffFixHarvest,    # Применение суперурожая
                    # GameBuffDigger,        # Активировать супер-поиск
                    # GameBuffFixCook,       # Активировать повара-минутки
                    # GameTravelBuff,        # Применение проездного
                    # SellBot,               # Продажа чего либо
                    # UseEggItemBot,         # Бить ценности
                    # PutStorage,            # Выставлять объекты со склада

                    # ExchangeHarvest,       # Обмен роз/лилий на монеты (в останкино)
                    # ExchangeEmeraldObserv, # Создание изумрудки (в планетарии)
                    # ExchangeShovelsBamboo, # Создание лопат из бамбука (в глаз-алмаз)
                    # ExchangeShovelsNail,   # Создание лопат из досок и гвоздей (в глаз-алмаз)
                    # ExchangeFlyingShip,    # Cоздание всего в летучем корабле. Клеверх.,чесн.лил.,хеллия,черепки
                    # Exchange1in1000,       # Cоздание металлолома ШТУКИ В 1000 (в склепе)
                    # ExchangeEmeraldic,     # Создание в изумрудных постройках
                    # ExchangeBabel,         # Создание зомбаксов (в Вавилоне)
                    # ExchangeInstantrert,   # Создание красных удобрений из черепков в томате (зомбоящик)
                    # ExchangeTube,          # Cоздание труб (в склепе)
                    # ExchangeSuperglue,     # Cоздание супер-клея (в Ёлке)
                    # ExchangeBolt,          # Создание болтов (в Эйфелевой)
                    # ExchangeRubber,        # Создание резины (в Останкино)
                    # ExchangeTransformator, # Создание трансформаторов (в Башне)
                    # ExchangeIronHeart,     # Создание железных сердец (в Вожде)
                    # ExchangeBlueHeart,     # Создание синих сердец (в Вожде)
                    # ExchangeFire,          # Создание огня (в Вожде)
                    # ExchangeFire2,         # Создание огня (в Цветике)
                    # ExchangeBoard,         # Создание досок (в Мельнице)
                    # ExchangeKraska,        # Создание желтой краски (в Пирамиде)
                    # ExchangeDiz,           # Создание дизайнерских яиц (в Семейном гнезде)
                    # ExchangeTermo,         # Создание термо яиц (в Семейном гнезде)
                    # ExchangeLove2,         # Создание любви(сердец) из лилий (в Особняке)
                    # ExchangeLove1,         # Создание любви(сердец) из роз (в Особняке)
                    # ExchangeBrains,        # Создание мозгов (в останкино)
                    # ChangePalach,          # Обмен коллекции палача на дублоны
                    # ChangeInferno,         # Обмен адской коллекции
                    # Collectionsell,        # Обмен любых коллекций

                    # BuildingBuyer,         # Покупать ракету
                    # BuildingTent,          # Удалено
                    # BuyShovel,             # Покупать золотые лопаты
                    # BuyGreenFertilizer,    # Покупать зелёные удобрения
                    # BuyAny,                # Покупка чего либо выставляемого
                    # BuyCaravel,            # Покупать каравеллы
                    # Upgrader,              # Достраивать строения
                    
                    RouletteRoller,        # Кручение рулеток
                    # RouletteTavernaDub,    # Кручение таверны за дублоны
                    # ShipCheck,             # Выкидывание из кораблей неугодных матросов
                    # KnockTeam,             # Работа команды стукачей
                    # AutoPirat,             # Автопиратство
                    WoodPicker,            # Сбор дерева
                    StonePicker,           # Сбор камня
                    WoodTargetSelecter,    # Отправка работать дровосекам
                    StoneTargetSelecter,   # Отправка работать камнетёсов
                    BagsPicker,            # Сбор сумок
                    BrewPicker,            # Сбор сваренного
                    CookerBot,             # Работа с поварами (подъем из могил, установка рецептов)
                    # CookSpeed,             # Cолить рецепты
                    # TradeBot,              # Ставить обмен у торговцев
                    # TradeSet,              # Супер торговец (админы добавили автобан! Аккуратно!)

                    # FertilPlantBot,        # Удобрение растений (красным)
                    # FertilBot,             # Удобрение деревьев
                    HarvesterBot,          # Сбор чего либо + вскапывание грядок
                    SeederBot,             # Посейка
                    # FertilPlantGreenBot,   # Удобрение растений (зелёным)
                    # TreePlant,             # Посадка деревьев 
                    # MagicWand,             # Добыча ресурсов палочками

                    # ScrollBot,             # Бъём свитки
                    # PirateTreeCutBroot,    # Удалено
                    PirateTreeCut,         # Рубка на острове сокровищ
                    BoxPickuper,           # Вскрытие чего либо
                    Pickuper,              # Сбор дропа
                    ChangeLocationBot      # Переход по локациям
                    ]
        elif self.group in [2, 3]: return [
                    Work,                  # Опыты и тесты
                    ActiveUser,            # Лог активности юзеров
                    # FinalReportUserMR,     # Полный отчёт о друзьях MR
                    # FinalReportUserVK,     # Полный отчёт о друзьях VK
                    # DeletingObjects,       # Удаление объектов

                    # SendCollections,       # РАЗОВО! Дарить коллекции по списку
                    # BoltGift,              # РАЗОВО! Передача другу Болтов по 1
                    # TiketReceiverBot,      # Собираем билеты, обновляем самолет/пасхальную корзинку
                    # BowReceiverBot,        # Собираем банты из циркового шатра
                    # Barabashka,            # Собираем барабашек из дома приведений
                    # VisitingUsers,         # Посещение друзей

                    # CakesReceiverBot,      # Сбор пряников
                    # GiftReceiverBot,       # Принятие подарков
                    # PremiumGifts,          # Принятие платных выставляемых подарков
                    # FreeGifts,             # Дарить бесплатки
                    # GiftsToFake,           # Дарить фейкам по списку
                    # SendColl,              # Передача коллекций (!)
                    # DigBot,                # Закапывать друзей получая мозги
                    # MonsterPit,            # Работа с Моней
                    # GameBuffFixHarvest,    # Применение суперурожая
                    # GameBuffDigger,        # Активировать супер-поиск
                    # GameBuffFixCook,       # Активировать повара-минутки
                    # GameTravelBuff,        # Применение проездного
                    # SellBot,               # Продажа чего либо
                    # UseEggItemBot,         # Бить ценности
                    # PutStorage,            # Выставлять объекты со склада

                    # ExchangeHarvest,       # Обмен роз/лилий на монеты (в останкино)
                    # ExchangeEmeraldObserv, # Создание изумрудки (в планетарии)
                    # ExchangeShovelsBamboo, # Создание лопат из бамбука (в глаз-алмаз)
                    # ExchangeShovelsNail,   # Создание лопат из досок и гвоздей (в глаз-алмаз)
                    # ExchangeFlyingShip,    # Cоздание всего в летучем корабле. Клеверх.,чесн.лил.,хеллия,черепки
                    # Exchange1in1000,       # Cоздание металлолома ШТУКИ В 1000 (в склепе)
                    # ExchangeEmeraldic,     # Создание в изумрудных постройках
                    # ExchangeBabel,         # Создание зомбаксов (в Вавилоне)
                    # ExchangeInstantrert,   # Создание красных удобрений из черепков в томате (зомбоящик)
                    # ExchangeTube,          # Cоздание труб (в склепе)
                    # ExchangeSuperglue,     # Cоздание супер-клея (в Ёлке)
                    # ExchangeBolt,          # Создание болтов (в Эйфелевой)
                    # ExchangeRubber,        # Создание резины (в Останкино)
                    # ExchangeTransformator, # Создание трансформаторов (в Башне)
                    # ExchangeIronHeart,     # Создание железных сердец (в Вожде)
                    # ExchangeBlueHeart,     # Создание синих сердец (в Вожде)
                    # ExchangeFire,          # Создание огня (в Вожде)
                    # ExchangeFire2,         # Создание огня (в Цветике)
                    # ExchangeBoard,         # Создание досок (в Мельнице)
                    # ExchangeKraska,        # Создание желтой краски (в Пирамиде)
                    # ExchangeDiz,           # Создание дизайнерских яиц (в Семейном гнезде)
                    # ExchangeTermo,         # Создание термо яиц (в Семейном гнезде)
                    # ExchangeLove2,         # Создание любви(сердец) из лилий (в Особняке)
                    # ExchangeLove1,         # Создание любви(сердец) из роз (в Особняке)
                    # ExchangeBrains,        # Создание мозгов (в останкино)
                    # ChangePalach,          # Обмен коллекции палача на дублоны
                    # ChangeInferno,         # Обмен адской коллекции
                    # Collectionsell,        # Обмен любых коллекций

                    # BuildingBuyer,         # Покупать ракету
                    # BuildingTent,          # Удалено
                    # BuyShovel,             # Покупать золотые лопаты
                    # BuyGreenFertilizer,    # Покупать зелёные удобрения
                    # BuyAny,                # Покупка чего либо выставляемого
                    # BuyCaravel,            # Покупать каравеллы
                    # Upgrader,              # Достраивать строения
                    
                    RouletteRoller,        # Кручение рулеток
                    # RouletteTavernaDub,    # Кручение таверны за дублоны
                    # ShipCheck,             # Выкидывание из кораблей неугодных матросов
                    # KnockTeam,             # Работа команды стукачей
                    # AutoPirat,             # Автопиратство
                    WoodPicker,            # Сбор дерева
                    StonePicker,           # Сбор камня
                    WoodTargetSelecter,    # Отправка работать дровосекам
                    StoneTargetSelecter,   # Отправка работать камнетёсов
                    BagsPicker,            # Сбор сумок
                    BrewPicker,            # Сбор сваренного
                    CookerBot,             # Работа с поварами (подъем из могил, установка рецептов)
                    # CookSpeed,             # Cолить рецепты
                    # TradeBot,              # Ставить обмен у торговцев
                    # TradeSet,              # Супер торговец (админы добавили автобан! Аккуратно!)

                    # FertilPlantBot,        # Удобрение растений (красным)
                    # FertilBot,             # Удобрение деревьев
                    HarvesterBot,          # Сбор чего либо + вскапывание грядок
                    SeederBot,             # Посейка
                    # FertilPlantGreenBot,   # Удобрение растений (зелёным)
                    # TreePlant,             # Посадка деревьев 
                    # MagicWand,             # Добыча ресурсов палочками

                    # ScrollBot,             # Бъём свитки
                    # PirateTreeCutBroot,    # Удалено
                    PirateTreeCut,         # Рубка на острове сокровищ
                    BoxPickuper,           # Вскрытие чего либо
                    Pickuper,              # Сбор дропа
                    ChangeLocationBot      # Переход по локациям
                    ]
        else: return [
                    Work,                  # Опыты и тесты
                    ActiveUser,            # Лог активности юзеров
                    # FinalReportUserMR,     # Полный отчёт о друзьях MR
                    # FinalReportUserVK,     # Полный отчёт о друзьях VK
                    # DeletingObjects,       # Удаление объектов

                    # SendCollections,       # РАЗОВО! Дарить коллекции по списку
                    # BoltGift,              # РАЗОВО! Передача другу Болтов по 1
                    # TiketReceiverBot,      # Собираем билеты, обновляем самолет/пасхальную корзинку
                    # BowReceiverBot,        # Собираем банты из циркового шатра
                    # Barabashka,            # Собираем барабашек из дома приведений
                    # VisitingUsers,         # Посещение друзей

                    # CakesReceiverBot,      # Сбор пряников
                    # GiftReceiverBot,       # Принятие подарков
                    # PremiumGifts,          # Принятие платных выставляемых подарков
                    # FreeGifts,             # Дарить бесплатки
                    # GiftsToFake,           # Дарить фейкам по списку
                    # SendColl,              # Передача коллекций (!)
                    # DigBot,                # Закапывать друзей получая мозги
                    # MonsterPit,            # Работа с Моней
                    # GameBuffFixHarvest,    # Применение суперурожая
                    # GameBuffDigger,        # Активировать супер-поиск
                    # GameBuffFixCook,       # Активировать повара-минутки
                    # GameTravelBuff,        # Применение проездного
                    # SellBot,               # Продажа чего либо
                    # UseEggItemBot,         # Бить ценности
                    # PutStorage,            # Выставлять объекты со склада

                    # ExchangeHarvest,       # Обмен роз/лилий на монеты (в останкино)
                    # ExchangeEmeraldObserv, # Создание изумрудки (в планетарии)
                    # ExchangeShovelsBamboo, # Создание лопат из бамбука (в глаз-алмаз)
                    # ExchangeShovelsNail,   # Создание лопат из досок и гвоздей (в глаз-алмаз)
                    # ExchangeFlyingShip,    # Cоздание всего в летучем корабле. Клеверх.,чесн.лил.,хеллия,черепки
                    # Exchange1in1000,       # Cоздание металлолома ШТУКИ В 1000 (в склепе)
                    # ExchangeEmeraldic,     # Создание в изумрудных постройках
                    # ExchangeBabel,         # Создание зомбаксов (в Вавилоне)
                    # ExchangeInstantrert,   # Создание красных удобрений из черепков в томате (зомбоящик)
                    # ExchangeTube,          # Cоздание труб (в склепе)
                    # ExchangeSuperglue,     # Cоздание супер-клея (в Ёлке)
                    # ExchangeBolt,          # Создание болтов (в Эйфелевой)
                    # ExchangeRubber,        # Создание резины (в Останкино)
                    # ExchangeTransformator, # Создание трансформаторов (в Башне)
                    # ExchangeIronHeart,     # Создание железных сердец (в Вожде)
                    # ExchangeBlueHeart,     # Создание синих сердец (в Вожде)
                    # ExchangeFire,          # Создание огня (в Вожде)
                    # ExchangeFire2,         # Создание огня (в Цветике)
                    # ExchangeBoard,         # Создание досок (в Мельнице)
                    # ExchangeKraska,        # Создание желтой краски (в Пирамиде)
                    # ExchangeDiz,           # Создание дизайнерских яиц (в Семейном гнезде)
                    # ExchangeTermo,         # Создание термо яиц (в Семейном гнезде)
                    # ExchangeLove2,         # Создание любви(сердец) из лилий (в Особняке)
                    # ExchangeLove1,         # Создание любви(сердец) из роз (в Особняке)
                    # ExchangeBrains,        # Создание мозгов (в останкино)
                    # ChangePalach,          # Обмен коллекции палача на дублоны
                    # ChangeInferno,         # Обмен адской коллекции
                    # Collectionsell,        # Обмен любых коллекций

                    # BuildingBuyer,         # Покупать ракету
                    # BuildingTent,          # Удалено
                    # BuyShovel,             # Покупать золотые лопаты
                    # BuyGreenFertilizer,    # Покупать зелёные удобрения
                    # BuyAny,                # Покупка чего либо выставляемого
                    # BuyCaravel,            # Покупать каравеллы
                    # Upgrader,              # Достраивать строения
                    
                    RouletteRoller,        # Кручение рулеток
                    # RouletteTavernaDub,    # Кручение таверны за дублоны
                    # ShipCheck,             # Выкидывание из кораблей неугодных матросов
                    # KnockTeam,             # Работа команды стукачей
                    # AutoPirat,             # Автопиратство
                    WoodPicker,            # Сбор дерева
                    StonePicker,           # Сбор камня
                    WoodTargetSelecter,    # Отправка работать дровосекам
                    StoneTargetSelecter,   # Отправка работать камнетёсов
                    BagsPicker,            # Сбор сумок
                    BrewPicker,            # Сбор сваренного
                    CookerBot,             # Работа с поварами (подъем из могил, установка рецептов)
                    # CookSpeed,             # Cолить рецепты
                    # TradeBot,              # Ставить обмен у торговцев
                    # TradeSet,              # Супер торговец (админы добавили автобан! Аккуратно!)

                    # FertilPlantBot,        # Удобрение растений (красным)
                    # FertilBot,             # Удобрение деревьев
                    HarvesterBot,          # Сбор чего либо + вскапывание грядок
                    SeederBot,             # Посейка
                    # FertilPlantGreenBot,   # Удобрение растений (зелёным)
                    # TreePlant,             # Посадка деревьев 
                    # MagicWand,             # Добыча ресурсов палочками

                    # ScrollBot,             # Бъём свитки
                    # PirateTreeCutBroot,    # Удалено
                    PirateTreeCut,         # Рубка на острове сокровищ
                    BoxPickuper,           # Вскрытие чего либо
                    Pickuper,              # Сбор дропа
                    ChangeLocationBot      # Переход по локациям
                    ]


# Режимы работы бота ===========================================================
    # отладочный лог для поиска ошибок
    def err_log(self):
        if self.group == 1: return False
        elif self.group in [2, 3]: return False
        else: return False

    # грузим инфу друзей
    def get_load_info_users(self):
        if self.group == 1: return True
        elif self.group == 2: return True
        elif self.group == 3: return True
        else: return True

    # сохраняем id/ник друзей
    def save_users_id_nick(self):
        if self.group == 1: return True
        elif self.group == 2: return False
        elif self.group == 3: return False
        else: return False

    # крутить бот по кругу
    def get_loop(self):
        if self.group == 1: return True
        elif self.group in [2, 3]: return True
        else: return False

    # интервал между островами, сек
    def interval(self):
        if self.group in [1, 5]: return 1
        elif self.group in [2, 3]: return 10
        else: return 7

    # интервал перезагрузок, мин
    def refresh_min(self):
        if self.group == 1: return 31
        elif self.group in [2, 3]: return 20
        else: return 1

    # диапазон рандомной паузы при сбое, сек
    def wait_refresh_sec(self):
        if self.group == 1: return (10,15)              # пауза 10-30 секунд
        elif self.group in [2, 3]: return (3,3)      # пауза 3 секунды (от 3 до 3)
        else: return (3,3)

    # вывод мини инфы по складу
    def storage2file(self):
        if self.group in [1, 2, 3]:
            return {'activated':True,
                    'predmet':['@CR_47', '@CR_53', '@CR_68', '@CR_33', '@CR_11', '@CR_41', '@METAL_SCRAP', '@S_34', '@CR_31', '@CR_29', '@CR_23', '@CR_17', '@R_33', '@CR_08'],
                    'collect':['C_48', 'C_19', 'C_16', 'C_17', 'C_8', 'C_22', 'C_1', 'C_15']
                    }
        else:
            return {'activated':False}

    # настройки частоты посещения островов. Как часто туда идём (в минутах)
    def time_isle(self):
        if self.group == 1: return {
                    # 'main':0,                   # Домашний
                    'isle_03':4.7,              # Любви
                    'isle_02':4.7,              # Майя
                    'isle_x':4.7,               # X
                    'isle_faith':4.7,           # Веры
                    'isle_hope':4.7,            # Надежды
                    'isle_scary':4.7,           # Страшный
                    'isle_alpha':4.7,           # Альфа
                    'isle_omega':4.7,           # Омега
                    'isle_5years':4.7,          # Пионерский лагерь
                    'isle_sand':4.7,            # Песочный
                    'isle_polar':4.7,           # Полярной ночи
                    'isle_wild':4.7,            # Дремучий
                    'isle_mobile':4.7,          # Мобильный
                    'isle_ufo':4.7,             # НЛО
                    'isle_dream':4.7,           # Мечты
                    'isle_scarecrow':4.7,       # Пик Админа
                    'isle_elephant':4.7,        # Ужасный
                    'isle_emerald':4.7,         # Город Призрак
                    'isle_monster':4.7,         # Чудовища
                    'isle_halloween':1441,      # Лысая гора
                    'isle_light':1321,          # Вишневый
                    ###############     Платные     ###############
                    'isle_01':4.7,              # Секретный
                    'isle_small':4.7,           # Маленькой ёлочки
                    'isle_star':2161,           # Звездный
                    'isle_large':4.7,           # Большой ёлки
                    'isle_moon':4.7,            # Лунный
                    'isle_giant':4.7,           # Гигантов
                    'isle_xxl':4.7,             # Огромной ёлки
                    'isle_desert':4.7,          # Необитаемый
                    ###############     Подземелье     ###############
                    'un_01':4.7,                # Подножье
                    # 'un_02':1,                  # Пещеры ЗУ
                    'un_03':4.7,                # Мексиканский каньон
                    'un_04':4.7,                # Копи царя Зомби
                    'un_05':4.7,                # Нижнее днище
                    'un_06':4.7,                # Бездна
                    'un_07':4.7,                # Хрустальный
                    'un_08':4.7,                # Мраморная
                    'un_09':4.7                 # Склад Хакера
                    }
        if self.group in [2, 3]: return {
                    # 'main':0,                   # Домашний
                    # 'isle_03':1,                # Любви
                    # 'isle_02':10,               # Майя
                    # 'isle_x':61,                # X
                    # 'isle_faith':61,            # Веры
                    # 'isle_hope':61,             # Надежды
                    # 'isle_scary':61,            # Страшный
                    # 'isle_alpha':61,            # Альфа
                    # 'isle_omega':61,            # Омега
                    # 'isle_5years':61,           # Пионерский лагерь
                    # 'isle_sand':61,             # Песочный
                    # 'isle_polar':61,            # Полярной ночи
                    # 'isle_wild':61,             # Дремучий
                    # 'isle_mobile':61,           # Мобильный
                    # 'isle_ufo':61,              # НЛО
                    # 'isle_dream':61,            # Мечты
                    # 'isle_scarecrow':61,        # Пик Админа
                    # 'isle_elephant':61,         # Ужасный
                    # 'isle_emerald':61,          # Город Призрак
                    # 'isle_monster':61,          # Чудовища
                    # 'isle_halloween':1441,      # Лысая гора
                    # 'isle_light':1321,          # Вишневый 
                    ###############     Платные     ###############
                    # 'isle_01':1,                # Секретный
                    # 'isle_small':1,             # Маленькой ёлочки
                    # 'isle_star':1,              # Звездный
                    # 'isle_large':1,             # Большой ёлки
                    # 'isle_moon':1,              # Лунный
                    # 'isle_giant':1,             # Гигантов
                    # 'isle_xxl':1,               # Огромной ёлки
                    # 'isle_desert':1,            # Необитаемый
                    ###############     Подземелье     ###############
                    # 'un_01':1,                  # Подножье
                    # 'un_02':1,                # Пещеры ЗУ
                    # 'un_03':1,                  # Мексиканский каньон
                    # 'un_04':1,                  # Копи царя Зомби
                    # 'un_05':1,                  # Нижнее днище
                    # 'un_06':1,                  # Бездна
                    # 'un_07':1,                  # Хрустальный
                    # 'un_08':1,                  # Мраморная
                    # 'un_09':1                   # Склад Хакера
                    }
        else: return {}


# Приём/дарение подарков =====================================================
    # модуль приёма подарков GiftReceiverBot (-gift.py-)
    def receive_options(self):
        if self.group in [1]:
            return {'admins': False,                # принимать подарки от администрации
                    'active_npc_love':False,        # принимать подарки от "Любви"
                    'with_messages': False,         # принимать подарки с сообщением
                    'coll':True,                    # принимать коллекции
                    'non_free': False,              # принимать платные подарки
                    'logging_message': True,        # сохранять лог подарков с ключевыми словами в сообщении
                    'words':[u'перрон',u'перон']    # ключевые слова в сообщениях (достаточно строчными)
                    }
        elif self.group in [2, 3]:
            return {'admins': False,                # принимать подарки от администрации
                    'active_npc_love':False,        # принимать подарки от "Любви"
                    'with_messages': False,         # принимать подарки с сообщением
                    'coll':True,                    # принимать коллекции
                    'non_free': False,              # принимать платные подарки
                    'logging_message': True,        # сохранять лог подарков с ключевыми словами в сообщении
                    'words':[u'перрон',u'перон']    # ключевые слова в сообщениях (достаточно строчными)
                    }
        else:
            return {'admins': False,                # принимать подарки от администрации
                    'active_npc_love':True,         # принимать подарки от "Любви"
                    'with_messages': True,          # принимать подарки с сообщением
                    'coll':True,                    # принимать коллекции
                    'non_free': True,               # принимать платные подарки
                    'logging_message': False,       # сохранять лог подарков с ключевыми словами в сообщении
                    'words':['zombio']              # ключевые слова в сообщениях (достаточно строчными)
                    }

    # модуль дарения бесплаток FreeGifts (-gift.py-)
    def free_gifts_options(self):
        # @CR_31-Любовь, @CR_44-Мир, @CR_70-Время, @CR_01-Цемент, @CR_97-Рогатка
        # @CR_06-Металл, @CR_16-Шестерня, @CR_40-Капля, @CR_25-Стекло, @CR_11-Доска
        if self.group == 1:
            return {
                    'SMS':u'',                  # сообщение к подарку u'Всем добра'
                    # 'SMS':u'Monster',           # по медведю u'Monster'
                    'other':'@CR_06',           # подарок тем у кого нет бесплатки в хотелке
                    'working_hours':{           # часы работы модуля
                            'from':'11:00',     # с час:мин
                            'to': '23:55'       # до час:мин
                    }}
        else:
            return {'SMS':u'',                  # сообщение к подарку
                    'other':'@CR_06',           # подарок тем у кого нет бесплатки в хотелке
                    'working_hours':{}
                    }

    # модуль передачи коллекций (постоянная) SendColl (-gift.py-)
    def send_coll_options(self):
        if self.group == 4:
            return {
                    'saveCollection':['C_48']       # какие коллекции не пересылать
                    }
        else:
            return {'saveCollection':[]}            # какие коллекции не пересылать

    # рассылка коллекций SendCollections (-gift.py-)
    def send_collections(self):
        adr = 'f_send_gifts_' + self.curuser + '.txt'
        if self.group == 1: return {
                    'SMS':u'подарочек...',          # сообщение
                    # 'file':adr,                     # брать данные для рассылки из файла
                    'delay':5,                      # задержка между отправками, мс
                    'only_frends':True,             # только тем кто друг
                    'users':[
                            ['11111', 'C_16', 3],
                            ['22222', 'C_17', 5],
                            ['33333', 'C_18', 10]
                            ]                       # id друга, id коллекции, количество
                    }

    # рассылка по списку предметов и коллекций GiftsToFake (-gift.py-)
    def send_gifts2fake(self):
        if self.group == 1: return {
                    'working_hours':{           # часы работы модуля
                            'from':'14:00',     # с час:мин
                            'to': '23:55'       # до час:мин
                            },
                    'SMS':u'',                      # сообщение
                    'delay':50,                     # задержка между отправками, мс
                    'only_frends':True,             # только тем кто друг
                    'data':[
                            {'id':['1111'],
                                    'SMS':u'мутабор',
                                    'gifts':{
                                        'CR_11':90
                                        }},
                            {'id':['2222','3333','4444','5555'],
                                    'SMS':u'мутабор',
                                    'gifts':{
                                        'CR_11':80
                                        }},
                            {'id':['6666','7777'],
                                    'SMS':u'мутабор',
                                    'gifts':{
                                        'CR_11':70
                                        }},
                            # {'id':['1111'],
                                    # 'SMS':u'мутабор',
                                    # 'gifts':{
                                        # 'METAL_SCRAP':45000
                                        # }},
                            ]}

    # передача другу болтов по 1 BoltGift (-bolt_gift.py-)
    def bolt_gift(self):
        return {'user':'1111',   # ID игрока, кому шлём '1111'
                'item_id':'@CR_53',             # что '@CR_53'-болт, '@CR_148'-кнопка Z, '@CR_66'-лампочка/микросхемы
                'msg':u'Лови гайку',            # сообщение
                'count':12,                     # cколько посылок слать
                'nut_count':1                   # по сколько штук
                }

    # принятие платных выставляемых подарков PremiumGifts (-premium_gifts.py-)
    def premium_gifts(self):
        if self.group in [1]:
            return {'location':['main','isle_desert','isle_xxl','isle_giant','isle_moon','isle_large','isle_star','isle_01','isle_halloween','isle_monster','isle_emerald','isle_elephant','isle_scarecrow','isle_dream','isle_ufo','isle_wild','isle_polar','isle_sand','isle_5years','isle_alpha','isle_scary','isle_hope','isle_faith','isle_x','isle_02','isle_03'],            # на каких островах, если пусто - все
                    'gift':['SNOWDROP_BOX1'],    # какие подарки (зомбилетто), если пусто - все 'SNOWDROP_BOX1'
                    'num':500                        # партиями по ... шт.
                    }

        else: return {'location':[],            # на каких островах, если пусто - все
                    'gift':['SNOWDROP_BOX1'],    # какие подарки (зомбилетто), если пусто - все 'SNOWDROP_BOX1'
                    'num':500                        # партиями по ... шт.
                    }

    # выставление нашей хотелки (-standing.py-)
    def wishlist_options(self):
        if self.group == 1:
            # return [u'@CR_11']                          # список хотелки
            pass
        elif self.group in [2, 3]:
            # return [u'@CR_11']                          # список хотелки u'@CR_04'
            pass
        else:
            # return [u'@CR_11']                          # список хотелки
            pass


# Покупка и постройка ========================================================
    # покупка/продажа ракеты BuildingBuyer
    def change_rocket_options(self):
        return {'location':'main',          # на каком острове
                'min_money':1750000000,     # оставляем монет
                'count':2000}               # партиями по ... шт.

    # покупка золотых лопат BuyShovel (-buy.py-)
    def buy_shovel(self):
        if self.group == 1:
            return {
                    'max_result':500,           # поддерживаем max лопат (0 и коммент -без ограничения)
                    'min_money':1800000000,     # оставляем монет
                    'count':2000                # запросы по ... шт. лопаты х3
                    }
        elif self.group in [2, 3]:
            return {
                    'max_result':500,           # поддерживаем max лопат (0 и коммент -без ограничения)
                    'min_money':10000000,       # оставляем монет
                    'count':2000                # запросы по ... шт. лопаты х3
                    }
        else:
            return {
                    'max_result':100,           # поддерживаем max лопат (0 и коммент -без ограничения)
                    'min_money':50000000,       # оставляем монет
                    'count':2000                # запросы по ... шт. лопаты х3
                    }

    # покупка зелёных удобрений BuyGreenFertilizer (-buy.py-)
    def buy_green_fertilizer(self):
        if self.group in [1, 2, 3]:
            return {
                    'max_result':1000,          # поддерживаем max удобр. (0 и коммент -без ограничения)
                    'min_money':100000000,      # оставляем монет
                    'count':500}                # запросы по ... шт. удобрений х50
        else:
            return {
                    'max_result':300,           # поддерживаем max удобр. (0 и коммент -без ограничения)
                    'min_money':1999999999,     # оставляем монет
                    'count':500}                # запросы по ... шт. удобрений х50

    # покупка чего либо выставляемого BuyAny (-buy.py-)
    def buy_any(self):
        if self.group == 1: return [
                # {                                   # дуб маленький
                # 'location':'main',                  # на каком острове
                # 'building':'SC_OAK1',               # покупаем дуб маленький
                # 'max_result':100,                   # поддерживаем максимум результата
                # 'rezerv_1':1500000000               # оставляем резерв средств
                # },
                {                                   # флаг Великобритании
                'location':'isle_02',               # на каком острове
                'building':'B_FLAG_ENGLAND',        # покупаем флаги Великобритании
                'max_result':3,                     # поддерживаем максимум результата
                'rezerv_1':1500000000               # оставляем резерв средств
                },
                {'location':'un_08',                # на каком острове (мраморная пещера)
                'building':'UN_SKULL_01',           # что покупаем (черепки)
                'max_result':30,                    # поддерживаем максимум результата
                'rezerv_1':1700000000               # оставляем резерв средств
                }]
        if self.group == 5: return [
                {'location':'un_08',                # на каком острове (мраморная пещера)
                'building':'UN_HAND_01',            # что покупаем (черепки)
                'max_result':100,                   # поддерживаем максимум результата
                'rezerv_1':3000000                  # оставляем резерв средств
                }]
        else: return []

    # покупка каравелл BuyCaravel (-buy.py-)
    def buy_caravell(self):
        if self.group == 1:
            return {'location':'main',                  # на каком острове
                    'building':'B_PIRATE_CARAVEL_2',    # что покупаем
                    'max_result':1,                     # поддерживаем максимум каравелл
                    'rezerv_1':500                      # оставляем резерв дублонов
                    }
        elif self.group in [2, 3, 8]:
            return {'location':'main',                  # на каком острове
                    'building':'B_PIRATE_CARAVEL_2',    # что покупаем
                    'max_result':1,                     # поддерживаем максимум каравелл
                    'rezerv_1':100                      # оставляем резерв дублонов
                    }

    # достраиваем строения Upgrader (-upgrade.py-)
    def upgrader_options(self):
        if self.group == 1: return {
                u'Строим':['@B_PIRATE_CARAVEL_2', '@B_PIRATE_CARAVEL', '@B_FLAG_ENGLAND'],  # что достраиваем
                u'НЕ строим':[]                                                             # что не трогаем
                }
        elif self.group in [2, 3, 5, 8]: return {
                u'Строим':['@B_PIRATE_CARAVEL_2', '@B_FLAG_ENGLAND'],  # что достраиваем
                u'НЕ строим':[]                                                             # что не трогаем
                }


# Пиратские модули ===========================================================
    # автопиратство AutoPirat (auto_pirat.py)
    def auto_pirate_options(self):
        fill_box = {'CHOP_MACHETE':30,  # мачете
                    'CHOP_AXE':20,      # топоры
                    'CHOP_HAMMER':30}   # кирки
        if self.group in [1, 2, 3]: return {                # === 1-й состав ===
                    'sostav':1,                             # номер состава
                    'gop_company':[
                                '1111',
                                '2222',
                                '3333'
                                 ],
                    'min_caravel_stuk':1,
                    'fill_box':fill_box,
                    'isle_go':'main',                       # остров с каравеллами с которого отплываем
                    'seaman_return':True,                   # матроса сразу возвращать домой
                    # 'ignore_alien_stop':True,             # игнорировать чужие СТОП
                    'nahlebniki':[]                         # доп товарищи для настука в корабли
                    }
        else: return {
                    'sostav':500,                           # номер состава
                    'gop_company':[],
                    'min_caravel_stuk':90,
                    'fill_box':fill_box,
                    'isle_go':'main',                       # остров с каравеллами с которого отплываем
                    'seaman_return':True,                   # матроса сразу возвращать домой
                    # 'ignore_alien_stop':True              # игнорировать чужие СТОП
                    }

    # команда стукачей (auto_pirat.py)
    def knock_team(self):
        # ['0:55', '3:55', '6:55', '9:55', '12:55', '15:55', '18:55', '21:55']
        if self.group == 7: return {
                    'seaman':['Seaman_'+str(i) for i in range(1,10)],    # имена учёток-стукачей
                    'knock_time':[str(h)+':55' for h in range(0,24, 3)], # время начала обхода
                    'na_vse_pro_vse':10                                  # в течении скольких минут уходить на обстук
                    }
        # ['0:28', '0:58', '1:28', '1:58', ...]
        if self.group == 10: return {
                    'seaman':[                                           # имена учёток-стукачей
                            'Vasya_1',
                            'Vasya_2',
                            'Vasya_3',
                            'Vasya_4',
                            'Vasya_5'
                            ],    
                    'knock_time':[str(h)+':'+str(m) for h in range(0,24) for m in (28,58)], # время начала обхода
                    'na_vse_pro_vse':10                                  # в течении скольких минут уходить на обстук
                    }
        else: return {}

    # проверять каравеллы на чужих матросов ShipCheck (chop.py)
    def ship_check_options(self):
        if self.group == 1: return {
                    'ships':['B_PIRATE_CARAVEL_2'],         # какие корабли проверяются
                    'file_seaman':'seaman_legal.txt',       # файл со списком разрешённых пиратов
                    # 'seaman':[]                             # список разрешённых пиратов (альтернатива файлу)
                    }
        if self.group in [2, 3, 8]: return {
                    'ships':['B_PIRATE_CARAVEL_2'],         # какие корабли проверяются
                    'file_seaman':'seaman_legal.txt',       # файл со списком разрешённых пиратов
                    # 'seaman':[]                             # список разрешённых пиратов (альтернатива файлу)
                    }
        else: return {}

    # бъём свитки ScrollBot (-plants.py-)
    def scroll_options(self):
        return {'count':100,               # сколько бъём свитков
                'reserv':1000}             # оставляем резерв

    # рубка на острове сокровищ PirateTreeCut (-chop.py-)
    def chop_options(self):
        if self.group == 1:
            return {'action':[
                        u'вскрытие сокровищ',
                        u'пинатель сильверов',
                        u'ломиться вглубь острова',
                        # u'хитрые условия',
                        # u'квестовый остров',
                        # u'брут колодцев',
                        # u'брут бочек и рулеток',
                        # u'брут сокровищ'
                        ],
                    'waits':15                # дожидаться рулетки в диапазоне, сек
                    }
        else:
            return {'action':[
                        u'вскрытие сокровищ',
                        u'пинатель сильверов',
                        u'ломиться вглубь острова',
                        # u'хитрые условия',
                        # u'квестовый остров',
                        # u'брут колодцев',
                        # u'брут рулеток и бочек',
                        # u'брут сокровищ'
                        ],
                    'waits':15                # дожидаться рулетки в диапазоне, сек
                    }

    # настукиватель, ходилка по друзьям в автопирате (auto_pirat.py)
    def friends_pirat(self):
        return {
                'что делаем':[
                    # 'pirateBoats',        # Стучим в лодки
                    # 'pirateSchooner',     # Стучим в шхуны
                    'pirateCaravel',        # Стучим в каравеллы
                    'pirateCheckin',        # Стучать в пиратские сундуки
                    'fruitTree',            # Удобрять фруктовые деревья
                    # 'box',                # Сундуки
                    'conifer',              # Ёлки
                    'monster',              # Мишка
                    # 'kopatel',            # Копатель
                    # 'tower',              # Башня
                    # 'airplane',           # Стук в шатёр (самолёты)
                    # 'valentine',          # Стук в Дерево Страсти
                    # 'valentine2',         # Стучим в сад бабочек
                    # 'korzina',            # Стук в пасхальную корзинку
                    # 'split_caches',       # Преобразовывать дружеские объекты  (разбивать тайники, надувать мячи)
                    # 'thanksgiving'        # Стучим в разные постройки
                    ],
                'параметры':{
                    'shovels':0,            # используем лопат
                    'max_monster':99,       # максимальная глубина закопки мони, которого будем копать мы
                    'con_user':50,          # сколько ложить пряников, НЕ БОЛЬШЕ! если больше, остат.стереть
                    'color_print':True,     # цветной лог
                    # 'circle_dig':True,    # обходить по кругу (по окончании обхода, идти по новой)
                    'only_firs':True,       # копать только и только первый нашедшийся объект для копки
                    # 'sort_green':True,      # ходить только по тем, у кого можно копать (по зелёным)
                    },
                'что копаем':[
                    # перрон
                    ['D_PLATFORM', 'D_PLATFORM2', 'D_BOOT_SEREBRO'],
                    # мыло
                    # ['D_SAKURASMALL','D_REDTREE','D_CONIFER','D_GATE','D_STATUETTE'],
                    # скакалки
                    # ['D_BUSINESS','D_BALLOONS','D_SUNUMBRELLA'],
                    # Е
                    # ['DS_SYMBOL_E', 'D_SYMBOL_E'],
                    # Е + японская
                    # ['DS_SYMBOL_E', 'D_SYMBOL_E', 'D_JAPAN_ARBOR', 'D_ARBOR'],
                    # ёлочная
                    # ['B_NYTREE','B_SNOWMAN','D_CLOCKTOWER','D_OLYMPIAD_STATUE','D_FLAG_OLIMPIADA','D_LANTERN_BIG_C'],
                    # звёздная
                    # ['B_SKLEP','B_SPRUCE_SMOLL'], # D_CRYPT  D_SKLEP D_CRYPTA D_SKLEP2
                    # брендовая колл.(флюгер)
                    # ['D_SHIP','D_POOL2','B_POOL','B_WHITEHOUSE','B_BUSINESS','D_IDOL2','D_FLOWER4_WHITE','D_FLOWER4_YELLOW','DS_SYMBOL_U_NESKL','DS_SYMBOL_I_BEL','D_OLYMPIAD_STATUE','B_FLAG_OLIMPIADA','B_VAN_ICE_CREAM','B_CUPOLA','B_CUPOLA_CASH','B_ZAPOROZHETS','B_ZAPOROZHETS_OLD','B_HUT_CH_LEGS','B_RUSALKA','B_YACHT'],
                    # школьная
                    # ['D_BALLOON_BLUE2'],
                    # футбольная
                    # ['B_FLAG_MILAN', 'D_FLAG_OLIMPIADA', 'D_OLYMPIAD_STATUE', 'D_L_ROSE'],
                    # металолом
                    # ['D_EIFFEL','B_JAPAN','B_JAPAN_LAKE'],
                    # школьная + любовь
                    # ['D_BALLOON_BLUE2', 'SC_GUARD_GRAVE', 'SC_GUARD_GRAVE_WITH_BRAINS', 'D_FLOWER4_YELLOW', 'D_CLOUDS'],
                    # белый кролик
                    # ['SC_TEAM_GRAVE', 'SC_TEAM_GRAVE2', 'D_OWL', 'B_FLAG_KAZAKSTAN', 'B_FLAG_GERMANY', 'D_BENCH_BIG_C', 'D_BENCH'],
                    # игрушек
                    # ['D_CASTLE', 'D_TENT', 'D_BEAR1', 'D_BEAR3', 'D_DETIDAY', 'D_CLOWN', 'D_ZOMB_HAND', 'D_HAND2', 'D_GARGOY', 'D_GARGOYA', 'SC_AIRPLANE_CASH'],
                    # фобий
                    # ['D_PINKHEART1', 'D_PINKHEART2'],
                    # Рука терминатора
                    # ['D_HAND1'],
                    # Кафель
                    # ['D_FLOWER4_WHITE','D_FLOWER4_YELLOW','D_BUSINESS','D_WHITEHOUSE','B_SHIP','B_VAN_ICE_CREAM'],
                    # кувалды/газеты
                    # ['B_LOUVRE','D_IGLOO'],
                    ]}

    # обмен коллекции палача на дублоны ChangePalach (-change_palach-)
    def change_palach_options(self):
        if self.group == 1:
            return {'support_dublon':1000,      # поддерживать дублонов
                    'reserv_palach':4000}       # резерв коллекций палача
        else:
            return {'support_dublon':100,       # поддерживать дублонов
                    'reserv_palach':50}         # резерв коллекций палача


# Копатель ===================================================================
    # копатель, ходилка по друзьям VisitingUsers (-friends.py-)
    def friends_options(self):
        if self.group == 1: return {
                    'что делаем':[
                        # 'pirateBoats',    # Стучим в лодки
                        # 'pirateSchooner', # Стучим в шхуны
                        # 'pirateCaravel',  # Стучим в каравеллы
                        'pirateCheckin',    # Стучать в пиратские сундуки
                        'fruitTree',        # Удобрять фруктовые деревья
                        'box',              # Сундуки
                        'conifer',          # Ёлки
                        'monster',          # Мишка
                        'kopatel',          # Копатель
                        # 'tower',          # Башня
                        # 'airplane',       # Стук в шатёр (самолёты)
                        # 'valentine',      # Стук в Дерево Страсти/Купидона
                        # 'valentine2',     # Стучим в сад бабочек
                        # 'korzina',        # Стук в пасхальную корзинку
                        # 'split_caches',   # Преобразовывать дружеские объекты  (разбивать тайники, надувать мячи)
                        # 'thanksgiving'    # Стучим в разные постройки
                        ],
                    'параметры':{
                        'color_print':True,     # цветной лог
                        # 'friends_file':'',      # список друзей из файла, если пусто - по нашим друзьям
                        'legal_friends':True,   # фильтровать id которые нам не друзья
                        'level_down':True,      # сортировать друзей по уровню, от больших к меньшим
                        'sort_green':True,      # ходить только по тем, у кого можно копать (по зелёным)
                        'shovels':50,           # используем лопат
                        'shovels_chu_u':300,    # используем лопат у Чуда Юда
                        'max_monster':99,       # максимальная глубина закопки мони, которого будем копать мы
                        'con_user':1,           # сколько ложить пряников каждому, НЕ БОЛЬШЕ! если больше, остат.стереть
                        'passing_number':500,   # проходить номеров из списка (если 0 - до конца)
                        'only_firs':True,       # копать только и только первый нашедшийся объект для копки

                        'circle_dig':True,      # обходить по кругу (по окончании обхода, идти по новой)
                        'period_between':90,    # период между обходами в минутах (чистим счётчики)
                        # 'returned_main':True,   # возвращаться на домашний (если нет, возврат на остров отплытия)
                        'free_list':True,       # если список шатров (самолётов) пуст, стучать всем подряд

                        'bot':True,             # добавить в начало хождения Чудо Юдо
                        'conifer_file':True,    # добавить в начало хождения список из conifer_user.txt
                        'perron_file':True,     # добавить в начало хождения список из perron.txt
                        'only_con_file':True,   # как прошли conifer_user.txt, другим не стучать

                        # 'new_friends':True,     # обходить только новых - добавленных друзей
                        # 'only_file_perron':True,# ходить только по списку юзеров с перронами
                        # 'airplane_list':True,   # ходить только по списку шатров (airplane)УСТАРЕЛО/снова в строю на пасху
                        },
                    'что копаем':[
                        # перрон
                        ['D_PLATFORM', 'D_PLATFORM2', 'D_BOOT_SEREBRO'],
                        # мыло
                        # ['D_SAKURASMALL','D_REDTREE','D_CONIFER','D_GATE','D_STATUETTE'],
                        # скакалки
                        # ['D_BUSINESS','D_BALLOONS','D_SUNUMBRELLA'],
                        # Е
                        # ['DS_SYMBOL_E', 'D_SYMBOL_E'],
                        # Е + японская
                        # ['DS_SYMBOL_E', 'D_SYMBOL_E', 'D_JAPAN_ARBOR', 'D_ARBOR'],
                        # ёлочная
                        # ['B_NYTREE','B_SNOWMAN','D_CLOCKTOWER','D_OLYMPIAD_STATUE','D_FLAG_OLIMPIADA','D_LANTERN_BIG_C'],
                        # редкая + звёздная, склеп и таверна короче
                        # ['B_SKLEP', 'B_TAVERNA'] 
                        # звёздная
                        # ['B_SKLEP','B_SPRUCE_SMOLL'], # D_CRYPT  D_SKLEP D_CRYPTA D_SKLEP2
                        # брендовая колл.(флюгер)
                        # ['D_SHIP','D_POOL2','B_POOL','B_WHITEHOUSE','B_BUSINESS','D_IDOL2','D_FLOWER4_WHITE','D_FLOWER4_YELLOW','DS_SYMBOL_U_NESKL','DS_SYMBOL_I_BEL','D_OLYMPIAD_STATUE','B_FLAG_OLIMPIADA','B_VAN_ICE_CREAM','B_CUPOLA','B_CUPOLA_CASH','B_ZAPOROZHETS','B_ZAPOROZHETS_OLD','B_HUT_CH_LEGS','B_RUSALKA','B_YACHT'],
                        # школьная
                        # ['D_BALLOON_BLUE2'],
                        # футбольная
                        # ['B_FLAG_MILAN', 'D_FLAG_OLIMPIADA', 'D_OLYMPIAD_STATUE', 'D_L_ROSE'],
                        # металолом
                        # ['D_EIFFEL','B_JAPAN','B_JAPAN_LAKE'],
                        # школьная + любовь
                        # ['D_BALLOON_BLUE2', 'SC_GUARD_GRAVE', 'SC_GUARD_GRAVE_WITH_BRAINS', 'D_FLOWER4_YELLOW', 'D_CLOUDS'],
                        # белый кролик
                        # ['SC_TEAM_GRAVE', 'SC_TEAM_GRAVE2', 'D_OWL', 'B_FLAG_KAZAKSTAN', 'B_FLAG_GERMANY', 'D_BENCH_BIG_C', 'D_BENCH'],
                        # игрушек
                        # ['D_CASTLE', 'D_TENT', 'D_BEAR1', 'D_BEAR3', 'D_DETIDAY', 'D_CLOWN', 'D_ZOMB_HAND', 'D_HAND2', 'D_GARGOY', 'D_GARGOYA', 'SC_AIRPLANE_CASH'],
                        # фобий
                        # ['D_PINKHEART1', 'D_PINKHEART2'],
                        # Рука терминатора
                        # ['D_HAND1'],
                        # Кафель
                        # ['D_FLOWER4_WHITE','D_FLOWER4_YELLOW','D_BUSINESS','D_WHITEHOUSE','B_SHIP','B_VAN_ICE_CREAM'],
                        # кувалды/газеты
                        # ['B_LOUVRE','D_IGLOO'],
                        ]}
        if self.group in [2, 3, 4, 8]: return {
                    'что делаем':[
                        # 'pirateBoats',    # Стучим в лодки
                        # 'pirateSchooner', # Стучим в шхуны
                        # 'pirateCaravel',  # Стучим в каравеллы
                        'pirateCheckin',    # Стучать в пиратские сундуки
                        'fruitTree',        # Удобрять фруктовые деревья
                        # 'box',              # Сундуки
                        'conifer',          # Ёлки
                        'monster',          # Мишка
                        'kopatel',          # Копатель
                        # 'tower',          # Башня
                        # 'airplane',       # Стук в шатёр (самолёты)
                        # 'valentine',      # Стук в Дерево Страсти/Купидона
                        # 'valentine2',     # Стучим в сад бабочек
                        # 'korzina',        # Стук в пасхальную корзинку
                        # 'split_caches',   # Преобразовывать дружеские объекты  (разбивать тайники, надувать мячи)
                        # 'thanksgiving'    # Стучим в разные постройки
                        ],
                    'параметры':{
                        'color_print':True,     # цветной лог
                        # 'friends_file':'',      # список друзей из файла, если пусто - по нашим друзьям
                        'legal_friends':True,   # фильтровать id которые нам не друзья
                        'level_down':True,      # сортировать друзей по уровню, от больших к меньшим
                        # 'sort_green':True,      # ходить только по тем, у кого можно копать (по зелёным)
                        'shovels':50,           # используем лопат
                        'shovels_chu_u':10,     # используем лопат у Чуда Юда
                        'max_monster':99,       # максимальная глубина закопки мони, которого будем копать мы
                        'con_user':100,         # сколько ложить пряников каждому, НЕ БОЛЬШЕ! если больше, остат.стереть
                        'passing_number':100,    # проходить номеров из списка (если 0 - до конца)
                        'only_firs':True,       # копать только и только первый нашедшийся объект для копки

                        'circle_dig':True,      # обходить по кругу (по окончании обхода, идти по новой)
                        'period_between':180,   # период между обходами в минутах
                        'returned_main':True,   # возвращаться на домашний (если нет, возврат на остров отплытия)
                        'free_list':True,       # если список шатров (самолётов) пуст, стучать всем подряд

                        'bot':True,             # добавить в начало хождения Чудо Юдо
                        # 'conifer_file':True,    # добавить в начало хождения список из conifer_user.txt
                        # 'perron_file':True,     # добавить в начало хождения список из perron.txt
                        # 'only_con_file':True,   # как прошли conifer_user.txt, другим не стучать

                        # 'new_friends':True,     # обходить только новых - добавленных друзей
                        # 'only_file_perron':True,# ходить только по списку юзеров с перронами
                        # 'airplane_list':True,   # ходить только по списку шатров (airplane)УСТАРЕЛО/снова в строю на пасху
                        },
                    'что копаем':[
                        # перрон
                        ['D_PLATFORM', 'D_PLATFORM2', 'D_BOOT_SEREBRO'],
                        # мыло
                        # ['D_SAKURASMALL','D_REDTREE','D_CONIFER','D_GATE','D_STATUETTE'],
                        # скакалки
                        # ['D_BALLOONS','D_SUNUMBRELLA','D_BUSINESS'],
                        # Е
                        # ['DS_SYMBOL_E', 'D_SYMBOL_E'],
                        # Е + японская
                        # ['DS_SYMBOL_E', 'D_SYMBOL_E', 'D_JAPAN_ARBOR', 'D_ARBOR'],
                        # ёлочная
                        # ['B_NYTREE','B_SNOWMAN','D_CLOCKTOWER','D_OLYMPIAD_STATUE','D_FLAG_OLIMPIADA','D_LANTERN_BIG_C'],
                        # звёздная
                        # ['B_SKLEP','B_SPRUCE_SMOLL'], # D_CRYPT  D_SKLEP D_CRYPTA D_SKLEP2
                        # брендовая колл.(флюгер)
                        # ['D_SHIP','D_POOL2','B_POOL','B_WHITEHOUSE','B_BUSINESS','D_IDOL2','D_FLOWER4_WHITE','D_FLOWER4_YELLOW','DS_SYMBOL_U_NESKL','DS_SYMBOL_I_BEL','D_OLYMPIAD_STATUE','B_FLAG_OLIMPIADA','B_VAN_ICE_CREAM','B_CUPOLA','B_CUPOLA_CASH','B_ZAPOROZHETS','B_ZAPOROZHETS_OLD','B_HUT_CH_LEGS','B_RUSALKA','B_YACHT'],
                        # школьная
                        # ['D_BALLOON_BLUE2'],
                        # футбольная
                        # ['B_FLAG_MILAN', 'D_FLAG_OLIMPIADA', 'D_OLYMPIAD_STATUE', 'D_L_ROSE'],
                        # металолом
                        # ['D_EIFFEL'], # 'B_JAPAN','B_JAPAN_LAKE'
                        # школьная + любовь
                        # ['D_BALLOON_BLUE2', 'SC_GUARD_GRAVE', 'SC_GUARD_GRAVE_WITH_BRAINS', 'D_FLOWER4_YELLOW', 'D_CLOUDS'],
                        # белый кролик
                        # ['SC_TEAM_GRAVE', 'SC_TEAM_GRAVE2', 'D_OWL', 'B_FLAG_KAZAKSTAN', 'B_FLAG_GERMANY', 'D_BENCH_BIG_C', 'D_BENCH'],
                        # игрушек
                        # ['D_CASTLE', 'D_TENT', 'D_BEAR1', 'D_BEAR3', 'D_DETIDAY', 'D_CLOWN', 'D_ZOMB_HAND', 'D_HAND2', 'D_GARGOY', 'D_GARGOYA', 'SC_AIRPLANE_CASH'],
                        # фобий
                        # ['D_PINKHEART1', 'D_PINKHEART2'],
                        # Рука терминатора
                        # ['D_HAND1'],
                        # Кафель
                        # ['D_FLOWER4_WHITE','D_FLOWER4_YELLOW','D_BUSINESS','D_WHITEHOUSE','B_SHIP','B_VAN_ICE_CREAM'],
                        # кувалды/газеты
                        # ['B_LOUVRE','D_IGLOO'],
                        ]}

# Создание в постройках - Craft ==============================================
    # создание всего в постройках Exchange (-craft.py-)
    def craft_options(self):
        if self.group == 1: return {
                    'ExchangeHarvest':{              # Обмен роз/лилий на монеты
                    'min_money':1740000000,     # делаем только если монет ниже чем...
                    'max_result':1900000000,    # поддерживаем максимум монет
                    'rezerv_1':60000,           # оставляем резерв роз
                    'rezerv_2':60000            # оставляем резерв лилий
                    },
                    'ExchangeEmeraldObserv':{       # Создание изумрудки (в Планетарии)
                    # 'max_result':10000,       # поддерживаем максимум изумрудки
                    'rezerv_1':1000,            # оставляем резерв Японской коллекции
                    'rezerv_2':10               # оставляем резерв бозона
                    },
                    'ExchangeShovelsBamboo':{       # Создание лопат из бамбука (Глаз-алмаз)
                    'max_result':4500000,       # поддерживаем максимум золотых лопат
                    'rezerv_1':95000,           # оставляем резерв бамбука
                    'rezerv_2':1000000000       # оставляем резерв монет
                    },
                    'ExchangeShovelsNail':{         # Создание лопат из досок и гвоздей (Глаз-алмаз)
                    'max_result':4500000,       # поддерживаем максимум золотых лопат
                    'rezerv_1':20000,           # оставляем резерв досок
                    'rezerv_2':10000            # оставляем резерв гвоздей
                    },
                    'ExchangeInstantrert':{         # Создание красных удобрений из черепков в томате (Зомбоящик)
                    'max_result':3000,          # поддерживаем максимум мгновенных удобрений
                    'rezerv_1':12000,           # оставляем резерв черепков в томате
                    'rezerv_2':10000            # оставляем резерв монет
                    },
                    'ExchangeTube':{                # Cоздание труб (в Склепе)
                    'max_result':200,           # поддерживаем максимум труб
                    'rezerv_1':1000,            # оставляем резерв металла
                    'rezerv_2':1000             # оставляем резерв шестерни
                    },
                    'Exchange1in1000':{             # Cоздание металлолома ШТУКИ В 1000 (в Склепе)
                    'max_result':100000000,     # поддерживаем максимум 1000 металлолома
                    'rezerv_1':1000000,         # оставляем резерв металлолома поштучных
                    'rezerv_2':1000             # оставляем резерв монет
                    },
                    'Exchange1000in1':{             # Cоздание металлолома 1000 В ШТУКИ (в Склепе)
                    'max_result':100000,        # поддерживаем максимум металлолома поштучных
                    # 'rezerv_1':0,             # оставляем резерв 1000 металлолома
                    'rezerv_2':1000             # оставляем резерв монет
                    },
                    'ExchangeEmeraldicStrah':{      # Создание в изумрудных постройках 'страшная'
                    # 'max_result':100000,      # поддерживаем максимум страшной колл.
                    'rezerv_1':10000,           # оставляем резерв ручной колл.
                    'rezerv_2':10000            # оставляем резерв обувной  колл.
                    },
                    'ExchangeEmeraldicLuxor':{      # Создание в изумрудных постройках 'луксорская'
                    # 'max_result':100000,      # поддерживаем максимум луксорской колл.
                    'rezerv_1':10000,           # оставляем резерв байкерской колл.
                    'rezerv_2':10000            # оставляем резерв колл. знаков
                    },
                    'ExchangeFlyingShipKlevHell':{  # Cоздание в летучем корабле. Клеверх
                    'max_result':40000,         # поддерживаем максимум клеверхелла
                    'rezerv_1':10000,           # оставляем резерв тыквахелла
                    'rezerv_2':10000            # оставляем резерв клевера
                    },
                    'ExchangeFlyingShipChesn':{     # Cоздание в летучем корабле. чесн.лил.
                    'max_result':10000,         # поддерживаем максимум чесночной лилии
                    'rezerv_1':10000,           # оставляем резерв чеснока
                    'rezerv_2':10000            # оставляем резерв лилий
                    },
                    'ExchangeFlyingShipHelia':{     # Cоздание в летучем корабле. хеллия
                    'max_result':2000,          # поддерживаем максимум хеллии
                    'rezerv_1':50,              # оставляем резерв клеверхелла
                    'rezerv_2':50               # оставляем резерв чесночной лилии
                    },
                    'ExchangeFlyingShipTomato':{    # Cоздание в летучем корабле. черепки
                    'max_result':12000,         # поддерживаем максимум черепков в томате
                    'rezerv_1':1000,            # оставляем резерв момидор
                    'rezerv_2':1000             # оставляем резерв костирузы
                    },
                    'ExchangeBrains':{              # Создание мозгов в останкино
                    'max_result':1,             # поддерживаем максимум мозгов без имеющихся у игрока бесплатных
                    'rezerv_1':1500,            # оставляем резерв хелий
                    'rezerv_2':500000           # оставляем резерв Любви - красных сердец
                    },
                    'ExchangeTransformator':{       # Cоздание трансформаторов (в Башне)
                    'max_result':250,           # поддерживаем максимум трансформаторов
                    'rezerv_1':1000,            # оставляем резерв хелии
                    'rezerv_2':1000             # оставляем резерв стекла
                    },
                    'ExchangeSuperglue':{           # Cоздание супер-клея (в Ёлке)
                    'max_result':250,           # поддерживаем максимум супер-клея
                    'rezerv_1':1000,            # оставляем резерв желтой краски
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeBolt':{                # Cоздание болтов (в Эйфелевой башне)
                    'max_result':450,           # поддерживаем максимум болтов
                    'rezerv_1':500,             # оставляем резерв стали
                    'rezerv_2':10000            # оставляем резерв чёрной руки
                    },
                    'ExchangeRubber':{              # Создавать резину (в Бизнес центре)
                    'max_result':5000,           # поддерживаем максимум резины
                    'rezerv_1':1000,            # оставляем резерв огня
                    'rezerv_2':100              # оставляем резерв клея
                    },
                    'ExchangeIronHeart':{           # Создавать железные сердца (в Вожде)
                    'max_result':50,            # поддерживаем максимум синих сердец
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeBlueHeart':{           # Создавать синие сердца (в Вожде)
                    'max_result':50,            # поддерживаем максимум синих сердец
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeFire':{                # Создавать огонь (в Вожде)
                    'max_result':50,            # поддерживаем максимум огня
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':10               # оставляем резерв железных сердец
                    },
                    'ExchangeFire2':{               # Создавать огонь (в Цветике)
                    'max_result':50,            # поддерживаем максимум огня
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':10000            # оставляем резерв чеснока
                    },
                    'ExchangeBabel':{               # Cоздание зомбаксов (в Вавилоне)
                    'max_result':10000,         # поддерживаем максимум ЗБ
                    'rezerv_1':100000000,       # оставляем резерв монет
                    'rezerv_2':10               # оставляем резерв зомбоксида
                    },
                    'ExchangeBoard':{               # Cоздание досок (в Мельнице)
                    'max_result':1000,          # поддерживаем максимум досок
                    'rezerv_1':10000,           # оставляем резерв брёвен
                    'rezerv_2':100000000        # оставляем резерв монет
                    },
                    'ExchangeKraska':{              # Cоздание желтой краски (в Пирамиде)
                    'max_result':30,            # поддерживаем максимум жёлтой краски
                    'rezerv_1':1000,            # оставляем резерв хелий
                    'rezerv_2':100000000        # оставляем резерв монет
                    },
                    'ExchangeDiz':{                 # Cоздание дизайнерского яйца (в Семейном гнезде)
                    'max_result':10,            # поддерживаем максимум дизайнерских яиц
                    'rezerv_1':10,              # оставляем резерв гарбузиков
                    'rezerv_2':50000            # оставляем резерв маракасов
                    },
                    'ExchangeTermo':{               # Cоздание термо яйца (в Семейном гнезде)
                    'max_result':10,            # поддерживаем максимум термо яиц
                    'rezerv_1':100,             # оставляем резерв волчьего штыка
                    'rezerv_2':100000000        # оставляем резерв красных драконов
                    },
                    'ExchangeLove1':{               # Cоздание любви(сердец) из роз (в Особняке)
                    'max_result':100,           # поддерживаем максимум любви(сердец)
                    'rezerv_1':1000,            # оставляем резерв роз
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeLove2':{               # Cоздание любви(сердец) из лилий (в Особняке)
                    'max_result':100,           # поддерживаем максимум любви(сердец)
                    'rezerv_1':1000,            # оставляем резерв лилий
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    }}
        if self.group in [2, 3]: return{
                    'ExchangeHarvest':{              # Обмен роз/лилий на монеты
                    'min_money':50000000,       # делаем только если монет ниже чем...
                    'max_result':1900000000,    # поддерживаем максимум монет
                    'rezerv_1':25000,           # оставляем резерв роз
                    'rezerv_2':25000            # оставляем резерв лилий
                    },
                    'ExchangeEmeraldObserv':{       # Создание изумрудки (в Планетарии)
                    # 'max_result':10000,       # поддерживаем максимум изумрудки
                    'rezerv_1':100,             # оставляем резерв Японской коллекции
                    'rezerv_2':10               # оставляем резерв бозона
                    },
                    'ExchangeShovelsBamboo':{       # Создание лопат из бамбука (Глаз-алмаз)
                    'max_result':4000000,       # поддерживаем максимум золотых лопат
                    'rezerv_1':60000,           # оставляем резерв бамбука
                    'rezerv_2':1000000000       # оставляем резерв монет
                    },
                    'ExchangeShovelsNail':{         # Создание лопат из досок и гвоздей (Глаз-алмаз)
                    'max_result':4000000,       # поддерживаем максимум золотых лопат
                    'rezerv_1':10000,           # оставляем резерв досок
                    'rezerv_2':10000            # оставляем резерв гвоздей
                    },
                    'ExchangeInstantrert':{         # Создание красных удобрений из черепков в томате (Зомбоящик)
                    'max_result':3000,          # поддерживаем максимум мгновенных удобрений
                    'rezerv_1':12000,           # оставляем резерв черепков в томате
                    'rezerv_2':10000            # оставляем резерв монет
                    },
                    'ExchangeTube':{                # Cоздание труб (в Склепе)
                    'max_result':200,           # поддерживаем максимум труб
                    'rezerv_1':1000,            # оставляем резерв металла
                    'rezerv_2':1000             # оставляем резерв шестерни
                    },
                    'Exchange1in1000':{             # Cоздание металлолома ШТУКИ В 1000 (в Склепе)
                    'max_result':100000000,     # поддерживаем максимум 1000 металлолома
                    'rezerv_1':1000000,         # оставляем резерв металлолома поштучных
                    'rezerv_2':1000             # оставляем резерв монет
                    },
                    'Exchange1000in1':{             # Cоздание металлолома 1000 В ШТУКИ (в Склепе)
                    'max_result':100000,        # поддерживаем максимум металлолома поштучных
                    # 'rezerv_1':0,             # оставляем резерв 1000 металлолома
                    'rezerv_2':1000             # оставляем резерв монет
                    },
                    'ExchangeEmeraldicStrah':{      # Создание в изумрудных постройках 'страшная'
                    # 'max_result':100000,      # поддерживаем максимум страшной колл.
                    'rezerv_1':10000,           # оставляем резерв ручной колл.
                    'rezerv_2':10000            # оставляем резерв обувной  колл.
                    },
                    'ExchangeEmeraldicLuxor':{      # Создание в изумрудных постройках 'луксорская'
                    # 'max_result':100000,      # поддерживаем максимум луксорской колл.
                    'rezerv_1':10000,           # оставляем резерв байкерской колл.
                    'rezerv_2':10000            # оставляем резерв колл. знаков
                    },
                    'ExchangeFlyingShipKlevHell':{  # Cоздание в летучем корабле. Клеверх
                    'max_result':40000,         # поддерживаем максимум клеверхелла
                    'rezerv_1':10000,           # оставляем резерв тыквахелла
                    'rezerv_2':10000            # оставляем резерв клевера
                    },
                    'ExchangeFlyingShipChesn':{     # Cоздание в летучем корабле. чесн.лил.
                    'max_result':10000,         # поддерживаем максимум чесночной лилии
                    'rezerv_1':10000,           # оставляем резерв чеснока
                    'rezerv_2':10000            # оставляем резерв лилий
                    },
                    'ExchangeFlyingShipHelia':{     # Cоздание в летучем корабле. хеллия
                    'max_result':2000,          # поддерживаем максимум хеллии
                    'rezerv_1':50,              # оставляем резерв клеверхелла
                    'rezerv_2':50               # оставляем резерв чесночной лилии
                    },
                    'ExchangeFlyingShipTomato':{    # Cоздание в летучем корабле. черепки
                    'max_result':12000,         # поддерживаем максимум черепков в томате
                    'rezerv_1':1000,            # оставляем резерв момидор
                    'rezerv_2':1000             # оставляем резерв костирузы
                    },
                    'ExchangeBrains':{              # Создание мозгов в останкино
                    'max_result':50,            # поддерживаем максимум мозгов без имеющихся у игрока бесплатных
                    'rezerv_1':1500,            # оставляем резерв хелий
                    'rezerv_2':500000           # оставляем резерв Любви - красных сердец
                    },
                    'ExchangeTransformator':{       # Cоздание трансформаторов (в Башне)
                    'max_result':50,            # поддерживаем максимум трансформаторов
                    'rezerv_1':10,              # оставляем резерв хелии
                    'rezerv_2':50               # оставляем резерв стекла
                    },
                    'ExchangeSuperglue':{           # Cоздание супер-клея (в Ёлке)
                    'max_result':50,            # поддерживаем максимум супер-клея
                    'rezerv_1':30,              # оставляем резерв желтой краски
                    'rezerv_2':20               # оставляем резерв трансформаторов
                    },
                    'ExchangeBolt':{                # Cоздание болтов (в Эйфелевой башне)
                    'max_result':100,           # поддерживаем максимум болтов
                    'rezerv_1':100,             # оставляем резерв стали
                    'rezerv_2':500              # оставляем резерв чёрной руки
                    },
                    'ExchangeRubber':{              # Создавать резину (в Бизнес центре)
                    'max_result':5000,           # поддерживаем максимум резины
                    'rezerv_1':1000,            # оставляем резерв огня
                    'rezerv_2':100              # оставляем резерв клея
                    },
                    'ExchangeIronHeart':{           # Создавать железные сердца (в Вожде)
                    'max_result':50,            # поддерживаем максимум синих сердец
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeBlueHeart':{           # Создавать синие сердца (в Вожде)
                    'max_result':50,            # поддерживаем максимум синих сердец
                    'rezerv_1':100,             # оставляем резерв Любви - красных сердец
                    'rezerv_2':20               # оставляем резерв трансформаторов
                    },
                    'ExchangeFire':{                # Создавать огонь (в Вожде)
                    'max_result':50,            # поддерживаем максимум огня
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':10               # оставляем резерв железных сердец
                    },
                    'ExchangeFire2':{               # Создавать огонь (в Цветике)
                    'max_result':50,            # поддерживаем максимум огня
                    'rezerv_1':1000,            # оставляем резерв Любви - красных сердец
                    'rezerv_2':10000            # оставляем резерв чеснока
                    },
                    'ExchangeBabel':{               # Cоздание зомбаксов (в Вавилоне)
                    'max_result':10000,         # поддерживаем максимум ЗБ
                    'rezerv_1':100000000,       # оставляем резерв монет
                    'rezerv_2':10               # оставляем резерв зомбоксида
                    },
                    'ExchangeBoard':{               # Cоздание досок (в Мельнице)
                    'max_result':200,           # поддерживаем максимум досок
                    'rezerv_1':3000,            # оставляем резерв брёвен
                    'rezerv_2':1000000          # оставляем резерв монет
                    },
                    'ExchangeKraska':{              # Cоздание желтой краски (в Пирамиде)
                    'max_result':30,            # поддерживаем максимум жёлтой краски
                    'rezerv_1':1000,            # оставляем резерв хелий
                    'rezerv_2':100000000        # оставляем резерв монет
                    },
                    'ExchangeDiz':{                 # Cоздание дизайнерского яйца (в Семейном гнезде)
                    'max_result':10,            # поддерживаем максимум дизайнерских яиц
                    'rezerv_1':10,              # оставляем резерв гарбузиков
                    'rezerv_2':50000            # оставляем резерв маракасов
                    },
                    'ExchangeTermo':{               # Cоздание термо яйца (в Семейном гнезде)
                    'max_result':10,            # поддерживаем максимум термо яиц
                    'rezerv_1':100,             # оставляем резерв волчьего штыка
                    'rezerv_2':100000000        # оставляем резерв красных драконов
                    },
                    'ExchangeLove1':{               # Cоздание любви(сердец) из роз (в Особняке)
                    'max_result':100,           # поддерживаем максимум любви(сердец)
                    'rezerv_1':1000,            # оставляем резерв роз
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    },
                    'ExchangeLove2':{               # Cоздание любви(сердец) из лилий (в Особняке)
                    'max_result':100,           # поддерживаем максимум любви(сердец)
                    'rezerv_1':1000,            # оставляем резерв лилий
                    'rezerv_2':100              # оставляем резерв трансформаторов
                    }}
        else: return{}


# Разное =====================================================================
    # сбор/посадка урожая HarvesterBot (-plants.py-)
    def harvester_options(self):
        if self.group == 1:
            return {'waits':20}            # ждать урожай если до него меньше чем..., сек
        elif self.group in [2, 3]:
            return {'waits':20}            # ждать урожай если до него меньше чем..., сек
        else:
            return {'waits':90}             # ждать урожай если до него меньше чем..., сек

    # вскрытие чего либо BoxPickuper (pickups.py)
    def box_pickuper_options(self):
        return ['@FOOTBALL_GIFT_BOX', '@VALENT_GIFT_BOX6', '@SNOWDROP_BOX2']  # исключения. Что НЕ вскрываем

    # удаление объектов DeletingObjects
    def deleting_options(self):
        if self.group == 3:                 # или self.curuser == 'ИМЯ' если аккаунт не тот - пропуск
            return {'object':['GROUND'],    # удалять объект по названию
                    'type':'',              # удалять объект по типу.   'decoration'
                    'isle':[                # На каком острове
                            #'main',            # Домашний
                            #'isle_03',         # Любви
                            #'isle_02',         # Майя
                            #'isle_x',          # X
                            #'isle_faith',      # Веры
                            #'isle_hope',       # Надежды
                            #'isle_scary',      # Страшный
                            #'isle_alpha',      # Альфа
                            #'isle_omega',      # Омега
                            #'isle_sand',       # Песочный
                            #'isle_polar',      # Полярной ночи
                            #'isle_wild',       # Дремучий
                            #'isle_mobile',     # Мобильный
                            #'isle_ufo',        # НЛО
                            #'isle_dream',      # Мечты
                            #'isle_scarecrow',  # Пик Админа
                            #'isle_elephant',   # Ужасный
                            #'isle_emerald',    # Город Призрак
                            #'isle_monster',    # Чудовища
                            #'isle_halloween',  # Лысая гора
                            #'isle_light',      # Вишневый
                            #
                            ############### Платные ###############
                            #'isle_01',         # Секретный
                            #'isle_small',      # Маленькой ёлочки
                            #'isle_star',       # Звездный
                            #'isle_large',      # Большой ёлки
                            #'isle_moon',       # Лунный
                            #'isle_giant',      # Гигантов
                            #'isle_xxl',        # Огромной ёлки
                            #'isle_desert'      # Необитаемый
                            ]}
        else: return {'object':[], 'type':'', 'isle':''}

    # бот продажи со склада SellBot (-storage.py)
    def sell_options(self):
        # продавать если денег меньше чем...
        if self.group == 1: return {
                'min_money':1700000000,     # минимальное количество денег, для начала продажи
                'max_money':1950000000      # максимальное количество денег для прекращения продажи
                }
        elif self.group in [2, 3]: return {
                'min_money':30000000,       # минимальное количество денег, для начала продажи
                'max_money':100000000       # максимальное количество денег для прекращения продажи
                }
        else: return {'min_money':1000000, 'max_money':1000000}

    # супер-урожай/поиск/минутка
    def buff_options(self):
        return {'day_count':5,          # Предупреждает, что через "day_count" дней закончится супер на складе
                'time_activation':30}   # Активировать за "time_activation" секунд до окончания

    # кручение рулеток RouletteRoller (-roulettes.py-)
    def roulettes_options(self):
        # не комментировать ,а то будет крутить до упора,лучше остаток больше поставить
        # рулетка  |  сколько оставлять фруктов  |  сколько оставлять рецептов
        if self.group == 1:
            return {'B_SLOT_APPLE':{'B_SLOT_B_ROULETTE1':50000,'B_SLOT_APPLE_ROULETTE2':300},        # Яблочный автомат
                    'B_SLOT_CHERRY':{'B_SLOT_B_ROULETTE1':150000,'B_SLOT_CHERRY_ROULETTE2':12000},   # Вишнёвый автомат
                    'B_SLOT_MANDARIN':{'B_SLOT_B_ROULETTE1':100000,'B_SLOT_MANDARIN_ROULETTE2':1120},# Мандар. автомат
                    'B_SLOT_LEMON':{'B_SLOT_B_ROULETTE1':10000,'B_SLOT_LEMON_ROULETTE2':10000},      # Лимонный автомат
                    'B_SOLDIER':{'B_SOLDIER_ROULETTE2':3000,'B_SOLDIER_ROULETTE':5},                 # Адмирал
                    }
        else:
            return {'B_SLOT_APPLE':{'B_SLOT_B_ROULETTE1':40000,'B_SLOT_APPLE_ROULETTE2':70},         # Яблочный автомат
                    'B_SLOT_CHERRY':{'B_SLOT_B_ROULETTE1':150000,'B_SLOT_CHERRY_ROULETTE2':15000},   # Вишнёвый автомат
                    'B_SLOT_MANDARIN':{'B_SLOT_B_ROULETTE1':110000,'B_SLOT_MANDARIN_ROULETTE2':1200},# Мандар. автомат
                    'B_SLOT_LEMON':{'B_SLOT_B_ROULETTE1':20000,'B_SLOT_LEMON_ROULETTE2':20000},      # Лимонный автомат
                    'B_SOLDIER':{'B_SOLDIER_ROULETTE2':3000,'B_SOLDIER_ROULETTE':5},                 # Адмирал
                    }

    # солим рецепты CookSpeed
    def cook_speed_options(self):
        if self.curuser == 'ИМЯ':
            return {'recipe_item':[u'@RECIPE_53',u'@RECIPE_28',u'@RECIPE_31'],  # что солим
                    'speed_item':'RED_SPEEDUPER'}                               # какой солью
        else:
            return {'recipe_item':[],'speed_item':'RED_SPEEDUPER'}

    # ставим произвольный обмен у торговцев TradeSet (-trade_graves.py-)
    def trade_options(self):
        if self.group == 1:
            return {
                    'want':{                            # получаем + количество
                                '@C_4_1':1,
                                #'@C_4_1':10,
                                #'@C_4_1':10,
                                #'@CHOP_HAMMER':1000
                            },
                    'give':{                            # отдаём + количество
                                # '@PIRATE_ENEMY_3':1,
                                #'@SHOVEL_EXTRA':30000,
                                #'@C_4_1':10,
                                '@C_43':10,
                            },
                    'id':None,                          # какому торговцу  ,  20200
                    'user':'null',                      # какому юзеру 'null' '1111'
                    'set':True                          # ставить, даже если обмен уже стоит
                    }
        else: return {'want':{},'give':{},'id':None,'user':'null','set':True}

    # удобрение деревьев и растений FertilPlant, FertilPlantGreenBot (-plants.py-)
    def fertil_options(self):
        return {'rezerv_RED_fertilizer':500,            # резерв красных 100% удобрений
                'rezerv_GREEN_fertilizer':500,          # резерв зелёных 30% удобрений
                'locations':[],                         # на каких островах, пусто-все
                'plants':[]                             # типы растений, пусто-все
                }

    # удобрение деревьев FertilBot (-plants.py-)
    def fertil_tree_options(self):
        # u'@FT_APPLE', u'@FT_CHERRY', u'@FT_MANDARINE', u'@FT_LEMON', u'@FT_EYE', u'@FT_SKULL'
        return {'rezerv_RED_TREE_fertilizer':2000,      # резерв удобрений для деревьев
                'locations':[],                         # на каких островах, пусто-все 'isle_faith'
                'tree':[]                               # типы деревьев, пусто-все
                }

    # добыча ресурсов палочками MagicWand (-wand.py-)
    def magicwand_options(self):
        if self.group == 1:
            return {'element':[u'@UN_SKULL_01'],        # u'D_STALAGMIT_2' - золотые листы и пыль
                    'types':[],                         # [GameStone.type, GameWoodTree.type]
                    'location':['un_08'],               # на каких островах
                    'working_hours':{                   # часы работы модуля
                            'from':'11:00',             # с час:мин
                            'to': '23:55'               # до час:мин
                    }}
        elif self.group == 5:
            return {'element':[u'@UN_HAND_01'],         # u'D_STALAGMIT_2' - золотые листы и пыль @UN_SKULL_01
                    'types':[],                         # [GameStone.type, GameWoodTree.type]
                    'location':['un_08'],               # на каких островах
                    'working_hours':{                   # часы работы модуля
                            'from':'11:00',             # с час:мин
                            'to': '23:55'               # до час:мин
                    }}
        else: return {'element':[],
                    'types':[GameStone.type, GameWoodTree.type],
                    'location':[],
                    'working_hours':{                   # часы работы модуля
                            'from':'11:00',             # с час:мин
                            'to': '23:55'               # до час:мин
                    }}

    # посадка деревьев TreePlant (-tree_plant.py-)
    def tree_plant_options(self):
        '''
        Что где сажаем
        u'FT_CHERRY', u'FT_APPLE', u'FT_MANDARINE', u'FT_SKULL', 'FT_LEMON'
        u'GROUND', u'FT_CHERRY_WHITE'
        '''
        if self.group == 1:
            return {'min_money':10000000,                        # оставляем денег
                    'plant_tree':{
                            # u'main':u'FT_CHERRY',                # Домашний
                            # u'isle_03':u'FT_APPLE',              # Любви
                            # u'isle_02':u'FT_CHERRY',             # Майя
                            # u'isle_x':u'FT_APPLE',               # X
                            # u'isle_faith':u'FT_APPLE',           # Веры
                            # u'isle_hope':u'FT_APPLE',            # Надежды
                            # u'isle_scary':u'FT_APPLE',           # Страшный
                            # u'isle_alpha':u'FT_CHERRY',          # Альфа
                            # u'isle_omega':u'FT_CHERRY',          # Омега
                            # u'isle_5years':u'GROUND',            # Пионерский лагерь
                            # u'isle_sand':u'FT_CHERRY',           # Песочный
                            # u'isle_polar':u'FT_CHERRY',          # Полярной ночи
                            # u'isle_wild':u'FT_CHERRY',           # Дремучий
                            # u'isle_mobile':u'FT_CHERRY',         # Мобильный
                            # u'isle_ufo':u'FT_CHERRY',            # НЛО
                            # u'isle_dream':u'FT_APPLE',           # Мечты
                            # u'isle_scarecrow':u'FT_CHERRY',      # Пик Админа
                            # u'isle_elephant':u'FT_SKULL',        # Ужасный
                            # u'isle_emerald':u'FT_MANDARINE',     # Город Призрак
                            # u'isle_monster':u'FT_CHERRY',        # Чудовища
                            # u'isle_halloween':u'FT_SKULL',       # Лысая гора
                            # u'isle_light':u'FT_CHERRY_WHITE',    # Вишневый 
                            #
                            ###############     Платные     ###############
                            # u'isle_01':u'FT_MANDARINE',          # Секретный
                            # u'isle_small':u'FT_CHERRY',          # Маленькой ёлочки
                            # u'isle_star':u'FT_SKULL',            # Звездный
                            # u'isle_large':u'FT_MANDARINE',       # Большой ёлки
                            # u'isle_moon':u'FT_MANDARINE',        # Лунный
                            # u'isle_giant':u'FT_MANDARINE',       # Гигантов
                            # u'isle_xxl':u'FT_MANDARINE',         # Огромной ёлки
                            # u'isle_desert':u'FT_MANDARINE',      # Необитаемый
                            #
                            ###############     Подземелье     ###############
                            # u'un_02':u'UN_FERN',                 # Пещеры ЗУ
                            # u'un_08':u'UN_SKULL_01',             # Мраморная
                            # u'un_09':u'UN_SKULL_01'              # Склад Хакера
                            }}
        elif self.group in [2, 3]:
            return {'min_money':1000000,                         # оставляем денег
                    'plant_tree':{
                            # u'main':u'FT_CHERRY',               # Домашний
                            # u'isle_03':u'FT_APPLE',              # Любви
                            # u'isle_02':u'FT_APPLE',              # Майя
                            # u'isle_x':u'FT_APPLE',               # X
                            # u'isle_faith':u'FT_APPLE',           # Веры
                            # u'isle_hope':u'FT_APPLE',            # Надежды
                            # u'isle_scary':u'FT_APPLE',           # Страшный
                            # u'isle_alpha':u'FT_APPLE',           # Альфа
                            # u'isle_omega':u'FT_APPLE',           # Омега
                            # u'isle_5years':u'FT_APPLE',          # Пионерский лагерь
                            # u'isle_sand':u'FT_APPLE',            # Песочный
                            # u'isle_polar':u'FT_APPLE',           # Полярной ночи
                            # u'isle_wild':u'FT_APPLE',            # Дремучий
                            # u'isle_mobile':u'FT_APPLE',          # Мобильный
                            # u'isle_ufo':u'FT_APPLE',             # НЛО
                            # u'isle_dream':u'FT_APPLE',           # Мечты
                            # u'isle_scarecrow':u'FT_APPLE',       # Пик Админа
                            # u'isle_elephant':u'FT_APPLE',        # Ужасный
                            # u'isle_emerald':u'FT_APPLE',         # Город Призрак
                            # u'isle_monster':u'FT_APPLE',         # Чудовища
                            # u'isle_halloween':u'FT_APPLE',       # Лысая гора
                            # u'isle_light':u'FT_CHERRY_WHITE',    # Вишневый 
                            #
                            ###############     Платные     ###############
                            # u'isle_01':u'FT_APPLE',              # Секретный
                            # u'isle_small':u'FT_APPLE',           # Маленькой ёлочки
                            # u'isle_star':u'FT_APPLE',            # Звездный
                            # u'isle_large':u'FT_APPLE',           # Большой ёлки
                            # u'isle_moon':u'GROUND',              # Лунный
                            # u'isle_giant':u'FT_APPLE',           # Гигантов
                            # u'isle_xxl':u'FT_APPLE',             # Огромной ёлки
                            # u'isle_desert':u'FT_APPLE'           # Необитаемый
                            #
                            ###############     Подземелье     ###############
                            # u'un_02':u'UN_FERN'                 # Пещеры ЗУ
                            # u'un_08':u'UN_FERN'                 # Мраморная
                            # u'un_09':u'UN_FERN'                 # Склад Хакера
                            }}

    # бить ценности UseEggItemBot (-plants.py-)
    def values_options(self):
        # ЧИСЛО - сколько оставляем
        if self.group == 1: return {
                    'EGG_01':2500,                 # Бэйби-сюрприз
                    'EGG_02':2000,                 # Простое
                    # 'EGG_03':100,                  # Непростое
                    'EGG_04':2500,                 # Русское
                    # 'EGG_05':100,                  # Пингвин-яйцо
                    # 'EGG_06':100,                  # Зомби сюрприз ???
                    # 'EGG_06_ADMIN':100,            # Зомби сюрприз ???
                    # 'EGG_07':100,                  # Ромашковое
                    # 'EGG_08':100,                  # Сердешное
                    # 'EGG_09':100,                  # Глазное
                    # 'EGG_10':100,                  # Медовое
                    # 'EGG_11':100,                  # Цитрусовое
                    # 'EGG_12':100,                  # Цветное
                    # 'EGG_13':100,                  # Детское
                    # 'EGG_15':100,                  # Звёздное
                    # 'EGG_16':100,                  # Расписное
                    # 'EGG_17':100,                  # Васильковое
                    # 'EGG_18':100,                  # Строгое
                    # 'EGG_19':100,                  # Ананасное
                    # 'EGG_20':100,                  # Клубничное
                    # 'EGG_21':100,                  # Арбузное
                    # 'EGG_22':100,                  # Вейдер-сюрприз
                    # 'EGG_23':100,                  # Бендер сюрприз
                    # 'EGG_24':100,                  # Картман-сюрприз
                    # 'EGG_25':100,                  # Дизайнерское
                    # 'EGG_26':100,                  # Термо яйцо
                    # 'EGG_27':100,                  # Губка-сюрприз
                    # 'EGG_33':100,                  # Полосатое
                    # 'EGG_34':100,                  # Сюрприз повара
                    # 'EGG_31':100,                  # Рогатое
                    # 'EGG_10':100,                  # Медовое
                    # 'WEALTH_BOTTLE':1000,          # Бутылка
                    # 'WEALTH_ROLL':10000,           # Свиток
                    # 'WEALTH_VASE':4000,            # Ваза
                    # 'WEALTH_BOWL':2000,            # Чаша
                    # 'WEALTH_SEQ':1000,             # Связка брёвен секвойи
                    # 'WEALTH_CASKET':1000,          # Шкатулка
                    # 'WEALTH_WOODPALM':1000,        # Связка брёвен пальмы
                    # 'WEALTH_WHITEM':1000,          # Груда белого мрамора
                    # 'WEALTH_BLACKM':1000,          # Груда черного мрамора
                    # 'WEALTH_MARBLE':1000,          # Груда зеленого мрамора
                    # 'WEALTH_SKULL':3000,           # Череп
                    # 'SOCK_NY_BIG':1000,            # Носок Изобилия
                    # 'SOCK_NY_MIDDLE':1000,         # Полярный носок
                    # 'TURKEY_BOX':3000,             # Пернатый подарок
                    # 'MONSTER_BOX_0':100,           # Сундук чудовища
                    'MONSTER_BOX_1':3000,          # Сундук чудовища
                    # 'MONSTER_BOX_2':1000,         # Сундук чудовища
                    # 'MONSTER_BOX_3':1000,         # Сундук чудовища
                    # 'MONSTER_BOX_4':1000,         # Сундук чудовища
                    # 'WEALTH_CONE':1200,           # шишка
                    # 'FREE_NY_BOX':2600,           # сюрприз
                    # 'WEALTH_MITTENS':1000,        # варежки
                    # 'WEALTH_PITCHER':1000,        # кувшин
                    # 'WEALTH_LARGEBARREL':100,     # большая бочка 
                    # 'WEALTH_FLAG':0               # Пиратский флаг            
                    }
        if self.group in [2, 3, 8]: return {
                    'EGG_01':2500,                 # Бэйби-сюрприз
                    'EGG_02':2000,                 # Простое
                    # 'EGG_03':100,                  # Непростое
                    'EGG_04':2500,                 # Русское
                    # 'EGG_05':100,                  # Пингвин-яйцо
                    # 'EGG_06':100,                  # Зомби сюрприз ???
                    # 'EGG_06_ADMIN':100,            # Зомби сюрприз ???
                    # 'EGG_07':100,                  # Ромашковое
                    # 'EGG_08':100,                  # Сердешное
                    # 'EGG_09':100,                  # Глазное
                    # 'EGG_10':100,                  # Медовое
                    # 'EGG_11':100,                  # Цитрусовое
                    # 'EGG_12':100,                  # Цветное
                    # 'EGG_13':100,                  # Детское
                    # 'EGG_15':100,                  # Звёздное
                    # 'EGG_16':100,                  # Расписное
                    # 'EGG_17':100,                  # Васильковое
                    # 'EGG_18':100,                  # Строгое
                    # 'EGG_19':100,                  # Ананасное
                    # 'EGG_20':100,                  # Клубничное
                    # 'EGG_21':100,                  # Арбузное
                    # 'EGG_22':100,                  # Вейдер-сюрприз
                    # 'EGG_23':100,                  # Бендер сюрприз
                    # 'EGG_24':100,                  # Картман-сюрприз
                    # 'EGG_25':100,                  # Дизайнерское
                    # 'EGG_26':100,                  # Термо яйцо
                    # 'EGG_27':100,                  # Губка-сюрприз
                    # 'EGG_33':100,                  # Полосатое
                    # 'EGG_34':100,                  # Сюрприз повара
                    # 'EGG_31':100,                  # Рогатое
                    # 'EGG_10':100,                  # Медовое
                    'WEALTH_BOTTLE':50,             # Бутылка
                    # 'WEALTH_ROLL':10000,           # Свиток
                    'WEALTH_VASE':50,               # Ваза
                    'WEALTH_BOWL':50,               # Чаша
                    'WEALTH_SEQ':100,               # Связка брёвен секвойи
                    # 'WEALTH_CASKET':1000,          # Шкатулка
                    'WEALTH_WOODPALM':100,          # Связка брёвен пальмы
                    'WEALTH_WHITEM':100,           # Груда белого мрамора
                    'WEALTH_BLACKM':100,           # Груда черного мрамора
                    'WEALTH_MARBLE':100,           # Груда зеленого мрамора
                    'WEALTH_SKULL':100,            # Череп
                    # 'SOCK_NY_BIG':1000,            # Носок Изобилия
                    # 'SOCK_NY_MIDDLE':1000,         # Полярный носок
                    # 'TURKEY_BOX':3000,             # Пернатый подарок
                    # 'MONSTER_BOX_0':100,           # Сундук чудовища
                    'MONSTER_BOX_1':3000,          # Сундук чудовища
                    # 'MONSTER_BOX_2':1000,         # Сундук чудовища
                    # 'MONSTER_BOX_3':1000,         # Сундук чудовища
                    # 'MONSTER_BOX_4':1000,         # Сундук чудовища
                    # 'WEALTH_CONE':1200,           # шишка
                    # 'FREE_NY_BOX':2600,           # сюрприз
                    # 'WEALTH_MITTENS':1000,        # варежки
                    # 'WEALTH_PITCHER':1000,        # кувшин
                    # 'WEALTH_LARGEBARREL':100,     # большая бочка 
                    # 'WEALTH_FLAG':0               # Пиратский флаг            
                    }
        else: return {}

    # обмен коллекций Collectionsell (-collections_sell.py-)
    def collections_sell_options(self):
        # ЧИСЛО - сколько оставляем
        if self.group == 1:
            return {
                    # 'C_1':10000,          # Звёздная
                    # 'C_2':1000,           # Луксорская
                    # 'C_3':10000,          # Байкерская
                    # 'C_4':10000,          # Знаков
                    # 'C_5':10000,          # Ручная
                    # 'C_6':10000,          # Обувная
                    # 'C_7':1000,           # Страшная
                    # 'C_8':10000,          # Строительная
                    # 'C_9':10000,          # Столовая
                    # 'C_10':10000,         # Редкая
                    # 'C_11':10000,         # Автомобильная
                    # 'C_12':10000,         # Туристическая
                    # 'C_13':10000,         # Домашняя
                    # 'C_14':10000,         # Игрушек
                    # 'C_15':10000,         # Ёлочная
                    # 'C_16':10000,         # Кролика
                    # 'C_17':10000,         # Цветов
                    # 'C_18':10000,         # Деда Мороза
                    # 'C_19':10000,         # Анти-зомби
                    # 'C_20':10000,         # Брендов
                    # 'C_21':10000,         # Весенняя
                    # 'C_22':10000,         # Тинейджерская
                    # 'C_23':10000,         # Компа
                    # 'C_24':10000,         # Морская
                    # 'C_25':10000,         # Пляжная
                    # 'C_26':10000,         # Майя
                    # 'C_27':2000,          # Секретная
                    # 'C_28':2000,          # Гипер
                    # 'C_29':10000,         # Хэллоуин
                    # 'C_30':10000,         # Президентская
                    # 'C_31':10000,         # Зимняя
                    # 'C_32':10000,         # Подземельная
                    # 'C_33':10000,         # Любовная
                    # 'C_34':10000,         # Адская
                    # 'C_35':10000,         # Райская
                    # 'C_36':10000,         # Японская
                    # 'C_37':10000,         # Школьная
                    # 'C_38':10000,         # Пиратская
                    # 'C_39':10000,         # Рыбака
                    # 'C_40':10000,         # Военная
                    # 'C_41':10000,         # Футбольная
                    # 'C_42':10000,         # Изумрудная
                    # 'C_43':10000,         # Песочная 
                    # 'C_44':10000,         # Котят
                    # 'C_45':10000,         # Щенков
                    # 'C_46':10000,         # Тропическая
                    # 'C_47':10000,         # Плохая
                    # 'C_48':10000,         # Палача
                    # 'C_49':10000,         # Фобий
                    # 'C_50':10000,         # Вкусная
                    # 'C_51':10000          # Временная
                    }
        else: return {}

    # выставляем что либо со склада PutStorage (-storage.py-)
    def put_storage_options(self):
        if self.group == 1: return {
                'location':['main'],                    # на каком острове (если нет или пусто-на всех)
                'objects':{                             # объект/оставляемый резерв на складе
                        u'SYMBOL_D_BOX':80,             # празничная Д
                        u'BIRTHDAY_GIFT_BOX1':80,       # корзинка с сердечком
                        u'BIRTHDAY_GIFT_BOX2':80,       # коробка с жёлтой лентой
                        u'BIRTHDAY_GIFT_BOX3':80,       # рука с сердцем
                        u'BIRTHDAY_GIFT_BOX4':80        # пакет с розой
                        }}
        if self.group in [2, 3]: return {
                # 'location':['main'],                    # на каком острове (если нет или пусто-на всех)
                'objects':{                             # объект/оставляемый резерв на складе
                        u'SYMBOL_D_BOX':50,             # празничная Д
                        u'BIRTHDAY_GIFT_BOX1':50,       # корзинка с сердечком
                        u'BIRTHDAY_GIFT_BOX2':50,       # коробка с жёлтой лентой
                        u'BIRTHDAY_GIFT_BOX3':50,       # рука с сердцем
                        u'BIRTHDAY_GIFT_BOX4':50        # пакет с розой
                        }}
        else: return {'object':{}}

    # обмен адской коллекции на палочки ChangeInferno (-change_inferno-)
    def change_inferno_options(self):
        if self.group == 1:
            return {'support_wand':1000,        # поддерживать волшебных палочек
                    'reserv_inferno':100000}    # резерв Адских коллекций
        else:
            return {'support_wand':1000,        # поддерживать волшебных палочек
                    'reserv_inferno':100}       # резерв Адских коллекций



    # Сюда добавляем настройки для новых модулей !!!




    # а так примерно, принимаем параметры в модуле
    # self.mega().ФУНКЦИЯ()
    # или если внутри словарь
    # self.mega().ФУНКЦИЯ()['ПАРАМЕТР']


    #=========================================================================

    # служебные, не лезем
    def get_group(self, groups):
        for group in groups.keys():
            if self.curuser in groups[group]:
                gr = int(group.lstrip('group_'))
                break
        else:
            gr = 1
        return gr

    def print_group(self):
        print self.cprint(u'14Аккаунт из группы^15_%d' % self.group)

    def cprint(self, cstr):
        clst = cstr.split('^')
        color = 0x0001

        for cstr in clst:
            dglen = re.search('\D', cstr).start()
            color = int(cstr[:dglen])
            text = cstr[dglen:]
            if text[:1] == '_': text = text[1:]
            SetConsoleTextAttribute(stdout_handle, color | 0x0070) #78
            print text.replace(u'\u0456', u'i').encode('cp866', 'ignore'),
        #sys.stdout.flush()
        print ''
        SetConsoleTextAttribute(stdout_handle, 0x0001 | 0x0070)
