# coding=utf-8
import pdb
import logging
import datetime
import random as random_number
import math
import time
from game_state.game_types import GameBuilding, GamePlayGame, DailyBonus, GamePlant
from game_state.base import BaseActor
from game_state.game_event import dict2obj, obj2dict
from game_actors_and_handlers.auto_pirat import AutoPirat


logger = logging.getLogger(__name__)

class Work(BaseActor):
    def perform_action(self):
        return
