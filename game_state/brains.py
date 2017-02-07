# coding=utf-8
import logging

logger = logging.getLogger(__name__)


class PlayerBrains(object):

    zombies_brains_required = {
        'woodGrave': 1,
        'woodGraveDouble': 2,
        'cookGrave': 2,
        'cookGraveWithBrains': 0,
        'guardGrave': 1,
        'stoneGrave': 1,
        'stoneGraveDouble': 2,
        'diggerGrave': 1,
        'diggerGraveWithBrains': 0
        }

    def __init__(self, game_state, game_location, item_reader, timer):
        self.__game_state = game_state
        self.__game_location = game_location
        self.__item_reader = item_reader
        self.__timer = timer

    def get_total_brains_count(self):
        brains_count = self.__game_state.brainsCount
        for buyed_brain in self.__game_state.buyedBrains:
            if self.__timer.has_elapsed(buyed_brain.endTime):continue
            brains_count += buyed_brain.count
        for burySlot in self.__game_state.burySlots:
            if (hasattr(burySlot, u"user") is True): brains_count += 1
        # logger.info(u'Всего мозгов %d'%(brains_count))
        return brains_count

    def get_occupied_brains_count(self):
        occupied_brains_count = 0
        for loc_info in self.__game_state.locationInfos:
            occupied_brains_count += loc_info.occupiedBrainsCount
        # logger.info(u'Занято мозгов на островах всего %d'%(occupied_brains_count))
        zombie_types = PlayerBrains.zombies_brains_required.keys()
        brains_objects = self.__game_location.get_all_objects_by_types(zombie_types)
        for brains_object in brains_objects:
            # print u'Объект с зомби', brains_object.item, 'id = ', brains_object.id
            # if hasattr(brains_object, 'target'): print 'target', brains_object.target
            # if hasattr(brains_object, 'isUp'): print 'isUp', brains_object.isUp
            # if hasattr(brains_object, 'started'): print 'started', brains_object.started
            if self.is_using_brains(brains_object):
                occupied_brains_count += self.get_brains_required(brains_object)
        # logger.info(u'+ работающие здесь %d'%(occupied_brains_count))
        player_status_item = self.__game_state.playerStatus
        player_status = self.__item_reader.get(player_status_item)
        if player_status.useBrain: occupied_brains_count += 1
        return occupied_brains_count

    def get_free_brain_count(self):
        return self.get_total_brains_count() - self.get_occupied_brains_count()

    def get_brains_required(self, brains_object):
        brains_object_type = self.__item_reader.get(brains_object.item)
        object_type = brains_object_type.type
        brains_required = 0
        if not (hasattr(brains_object_type, 'haveBrains') and brains_object_type.haveBrains):
            if object_type in PlayerBrains.zombies_brains_required:
                brains_required = PlayerBrains.zombies_brains_required[object_type]
            else:
                logger.error("Unknown object type: " + object_type)
        return brains_required

    def is_using_brains(self, brains_object):
        if hasattr(brains_object, 'target') and brains_object.target: using = True
        elif hasattr(brains_object, 'isUp') and brains_object.isUp: using = True
        elif hasattr(brains_object, 'started') and brains_object.started: using = True
        else: using = False
        return using

    def has_sufficient_brains_count(self, brains_object):
        return (self.get_brains_required(brains_object) <= self.get_free_brain_count())
