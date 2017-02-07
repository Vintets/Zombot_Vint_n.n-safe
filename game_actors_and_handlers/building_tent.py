# coding=utf-8
import logging
from game_state.game_types import GameWoodGrave, GameWoodGraveDouble,\
    GamePickItem, GameWoodTree, GameGainItem, GamePickup
from game_state.game_event import dict2obj
from game_state.base import BaseActor

logger = logging.getLogger(__name__)


class BuildingTent(BaseActor):

    def perform_action(self):
        return