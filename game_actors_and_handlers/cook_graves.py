# coding=utf-8
import logging
from game_state.game_types import GameCookGrave, GameCookGraveWithBrains, GameCookItem, GameCookSpeed, GameCookStart, GameCookStop
from game_state.item_reader import LogicalItemReader
from game_actors_and_handlers.workers import ResourcePicker, TargetSelecter
from game_state.game_event import obj2dict
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class BrewPicker(ResourcePicker):

    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]

class CookSpeed(BaseActor):

    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]
  
    def perform_action(self):
        if self.if_location_pirate(): return
        wood_graves = self._get_game_location().get_all_objects_by_types(
            self.get_worker_types())
        recipe_item = self.mega().cook_speed_options()['recipe_item']
        speed_item = self.mega().cook_speed_options()['speed_item']
        if self._get_game_state().count_in_storage('@'+speed_item) > 0:
            for wood_grave in wood_graves:
                #print u'До', obj2dict(wood_grave)
                #{u'rotate': 0L, u'jobEndTime': u'2258993', u'speeduped': False, u'id': 3620L, u'materials': [], u'item': u'@SC_COOK_GRAVE', u'isUp': True, u'recipeNo': 360L, u'y': 35L, u'x': 21L, u'type': u'cookGrave', u'pendingRecipes': [u'@RECIPE_09', u'@RECIPE_09'], u'currentRecipe': u'@RECIPE_09'}
                if hasattr(wood_grave, "isUp") or wood_grave.isUp:
                    if hasattr(wood_grave, "currentRecipe"):
                        count_speed = 0
                        materials = []
                        names = u''
                        if wood_grave.currentRecipe in recipe_item: 
                            #print u'солим currentRecipe'
                            count_speed += 1
                            mat = self._get_item_reader().get(wood_grave.currentRecipe)
                            materials.append(mat.result)
                            names += mat.name + u' '
                            del wood_grave.currentRecipe
                        pend = 0
                        for i in wood_grave.pendingRecipes:
                            if i in recipe_item:
                                #print u'солим pendingRecipes'
                                count_speed += 1
                                mat = self._get_item_reader().get(i)
                                materials.append(mat.result)
                                names += mat.name + u' '
                                pend += 1
                            else: break
                        if pend == 2:
                            wood_grave.pendingRecipes = []
                        elif pend == 1:
                            wood_grave.pendingRecipes.pop(0)
                        if count_speed == 0: break

                        logger.info(u'Посолим %d рецепта у поваров №%d'%(count_speed,wood_grave.id))
                        logger.info(names)
                        for i in range(count_speed):
                            if self._get_game_state().count_in_storage('@'+speed_item)>0:
                                #{"objId":3494,"type":"item","action":"speedup","itemId":"RED_SPEEDUPER"}
                                event=GameCookSpeed(objId=wood_grave.id,itemId=unicode(speed_item))
                                self._get_events_sender().send_game_events([event])
                                self._get_game_state().remove_from_storage('@'+speed_item,1)
                            else: break

                        wood_grave.jobEndTime = 3000
                        wood_grave.materials = materials
                        #print u'После', obj2dict(wood_grave)

                        #{"type":"recipe","id":"RECIPE_28","name":"Синяя краска","description":"Материал для строительства.","cookingTime":7200,"ingridients":[{"count":5,"item":"@S_06"},{"count":3,"item":"@S_41"}],"result":"@CR_51"}
                        pass

class CookerBot(TargetSelecter):
    MAX_PENDING_RECIPES = 2

    def get_worker_types(self):
        return [GameCookGrave.type, GameCookGraveWithBrains.type]

    def perform_action(self):
        if self.if_location_pirate(): return
        wood_graves = self._get_game_location().get_all_objects_by_types(
            self.get_worker_types()
            )
        free_workers = []
        for wood_grave in wood_graves:
            if wood_grave.item == '@SC_BLACKSMITH': continue
            if self.is_busy(wood_grave):
                free_workers.append(wood_grave)
        for free_worker in free_workers:
            self.start_job(free_worker)

    def is_busy(self, worker):
        return (not self._get_player_brains().is_using_brains(worker)) or (self.free_pendig(worker) > 0)

    def free_pendig(self, free_worker):
        empty_buckets = CookerBot.MAX_PENDING_RECIPES - len(free_worker.pendingRecipes)
        if (hasattr(free_worker, "currentRecipe") is False): empty_buckets += 1
        return empty_buckets

    def select_recipe(self, cook_items):
        recipe_type = 1
        cook_item = None
        count = 0
        if type(cook_items) == str or type(cook_items) == unicode:
            cook_item = self._get_item_reader().get(cook_items)
            count = self.has_count_ingredients(cook_item.ingridients)
        elif type(cook_items) == dict:
            location = self._get_game_state().get_game_loc().get_location_id()
            if location in cook_items.keys(): cook_id = cook_items[location]
            else: cook_id = cook_items.get('other', None)
            if not(cook_id == 'None' or cook_id == None):
                cook_item = self._get_item_reader().get(cook_id)
                count = self.has_count_ingredients(cook_item.ingridients)
        elif type(cook_items) == list and (type(cook_items[0]) == str or type(cook_items[0]) == unicode):
            recipe_type = 2
            for cook_ in cook_items:
                cook_item = self._get_item_reader().get(cook_)
                count = self.has_count_ingredients(cook_item.ingridients)
                if count: break
        elif type(cook_items) == list and type(cook_items[0]) == tuple:
            recipe_type = 3
            for cook_ in cook_items:
                cook_item = self._get_item_reader().get(cook_[0])
                has = self._get_game_state().count_in_storage(cook_item.result)
                needed = cook_[1]
                # print cook_
                # print 'has', has, 'needed', needed
                if needed != -1 and has >= needed: continue
                count = self.has_count_ingredients(cook_item.ingridients)
                if count: break
        # print u'тип рецептов', recipe_type
        return recipe_type, cook_item, count

    def start_job(self, free_worker):
        cook_items = self._get_options()
        if cook_items == None or cook_items == 'None' or cook_items == '': return

        recipe_type, cook_item, count = self.select_recipe(cook_items)
        if not count:
            logger.info(u'Нет ингредиентов поварам или сварили лимит!')
            return

        # поднятие поваров
        self.cook_up(free_worker)

        empty_buckets = self.free_pendig(free_worker)
        if recipe_type == 1:
            for _ in range(min(empty_buckets, count)):
                self.fill_basket(free_worker, cook_item)
                self.remove_ingredients(cook_item.ingridients)
        else:
            while empty_buckets != 0:
                if count > 0:
                    self.fill_basket(free_worker, cook_item)
                    self.remove_ingredients(cook_item.ingridients)
                    empty_buckets -= 1
                    count -= 1
                else:
                    recipe_type, cook_item, count = self.select_recipe(cook_items)
                    if not count:
                        logger.info(u'Нет ингредиентов поварам или сварили лимит!')
                        break

    def cook_up(self, free_worker):  # поднятие поваров
        if self._get_player_brains().has_sufficient_brains_count(free_worker):
            if not hasattr(free_worker, "isUp") or not free_worker.isUp:
                logger.info(u'Повара отдыхают запустим работать №' + str(free_worker.id))
                start_item_event = GameCookStart(free_worker.id)
                self._get_events_sender().send_game_events([start_item_event])
                free_worker.isUp = True

    def has_count_ingredients(self, ingredients):
        count_recipe_ingredients = []
        for ingredient in ingredients:
            has_count = self._get_game_state().count_in_storage(ingredient.item)
            count_recipe_ingredients.append(has_count / ingredient.count)
        return min(count_recipe_ingredients)

    def has_enough_ingredients(self, ingredients):
        for ingredient in ingredients:
            if not self._get_game_state().has_in_storage(ingredient.item,
                                                        ingredient.count):
                return False
        return True

    def remove_ingredients(self, ingredients):
        for ingredient in ingredients:
            self._get_game_state().remove_from_storage(ingredient.item,
                                                       ingredient.count)

    def fill_basket(self, free_worker, cook_item):
        #print 'cook_item', obj2dict(cook_item)
        #print 'cook_item', cook_item.id
        logger.info(u'Добавляем рецепт "%s" поварам №%d' %(cook_item.name,free_worker.id))
        time = self._get_item_reader().get('@'+cook_item.id).cookingTime*1000
        free_worker.jobEndTime = self._get_timer()._get_current_client_time() + time + 3000
        # free_worker.jobEndTime = time
        cook_item_event = GameCookItem(cook_item.id,free_worker.id)
        self._get_events_sender().send_game_events([cook_item_event])
        if not self.has_current_recipe(free_worker):
            free_worker.currentRecipe = '@' + cook_item.id
        else:
            free_worker.pendingRecipes.append('@' + cook_item.id)

    def has_current_recipe(self, free_worker):
        return hasattr(free_worker, "currentRecipe") and free_worker.currentRecipe

    """
    if 'RECIPE_13' in cook_items:
        r13_index = cook_items.index('RECIPE_13')
        if len(cook_items) >= 2+r13_index and\
                cook_items[1+r13_index] == 'RECIPE_08' and cook_items[2+r13_index] == 'RECIPE_03':
            if self._get_game_state().count_in_storage('@R_08') > self._get_game_state().count_in_storage('@R_03'):
                cook_items[1+r13_index],cook_items[2+r13_index] = cook_items[2+r13_index],cook_items[1+r13_index]
        if len(cook_items) >= 2+r13_index and\
                cook_items[1+r13_index] == 'RECIPE_03' and cook_items[2+r13_index] == 'RECIPE_08':
            if self._get_game_state().count_in_storage('@R_03') > self._get_game_state().count_in_storage('@R_08'):
                cook_items[1+r13_index],cook_items[2+r13_index] = cook_items[2+r13_index],cook_items[1+r13_index]
    """


class RecipeReader(LogicalItemReader):
    def __init__(self, game_item_reader):
        self._item_reader = game_item_reader

    def _get_item_type(self):
        return 'recipe'

    def _get_all_item_ids(self):
        return self._item_reader.get('recipes').items


# TODO cooker event: set isUp to False, currentRecipe to the next pending recipe
