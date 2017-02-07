# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_actors_and_handlers.workers import TargetSelecter
from game_actors_and_handlers.workers import ResourcePicker

logger = logging.getLogger(__name__)


class WoodTargetSelecter(TargetSelecter):

    def get_worker_types(self):
        return [GameWoodGrave.type, GameWoodGraveDouble.type]

    def get_object_type(self):
        return GameWoodTree.type

    def get_sent_job(self):
        return "Рубим дерево"


class WoodPicker(ResourcePicker):

    def get_worker_types(self):
        return [GameWoodGrave.type, GameWoodGraveDouble.type]

