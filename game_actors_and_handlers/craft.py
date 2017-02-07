# coding=utf-8
import logging
from game_state.game_types import GameBuilding
from game_state.base import BaseActor
from game_state.game_event import dict2obj, obj2dict
import time

logger = logging.getLogger(__name__)


# обмен роз/лилий на монеты (в бизнес центре)
class ExchangeHarvest(BaseActor):  # CreateMoney
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeHarvest']
        if self.money() < options['min_money']:
            self.craft(options,'B_BUSINESS','3')


# создание изумрудки (в планетарии)
class ExchangeEmeraldObserv(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeEmeraldObserv']
        self.craft(options,'B_OBSERVATORY','11')
        self.craft(options,'B_OBSERVATORY','12')
        self.craft(options,'B_OBSERVATORY','13')
        self.craft(options,'B_OBSERVATORY','14')
        self.craft(options,'B_OBSERVATORY','15')


# создание лопат из бамбука (в глаз-алмаз)
class ExchangeShovelsBamboo(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeShovelsBamboo']
        self.craft(options,'B_EYE','1')


# создание лопат из досок и гвоздей (в глаз-алмаз)
class ExchangeShovelsNail(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeShovelsNail']
        self.craft(options,'B_EYE','2')


# создание красных удобрений из черепков в томате (в зомбоящике)
class ExchangeInstantrert(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeInstantrert']
        self.craft(options,'B_TVSET','1')


# создание труб (в склепе)
class ExchangeTube(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeTube']
        self.craft(options,'B_SKLEP','2')


# создание металлолома ШТУКИ В 1000 (в склепе)
class Exchange1in1000(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['Exchange1in1000']
        self.craft(options,'B_SKLEP','5')


# создание металлолома 1000 В ШТУКИ (в склепе)
class Exchange1000in1(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['Exchange1000in1']
        self.craft(options,'B_SKLEP','7')

        
# Обмен в изумрудных постройках
class ExchangeEmeraldic(BaseActor):
    def perform_action(self):
        # ручная и обувная в страшную (в изумрудной мельнице)
        options = self.mega().craft_options()['ExchangeEmeraldicStrah']
        self.craft(options,'B_MILL_EMERALD2','1')
        self.craft(options,'B_MILL_EMERALD2','2')
        self.craft(options,'B_MILL_EMERALD2','3')
        self.craft(options,'B_MILL_EMERALD2','4')
        self.craft(options,'B_MILL_EMERALD2','5')

        # байкерская и знаков в луксорскую (в изумрудном маяке)
        options = self.mega().craft_options()['ExchangeEmeraldicLuxor']
        self.craft(options,'B_LIGHT_EMERALD2','1')
        self.craft(options,'B_LIGHT_EMERALD2','2')
        self.craft(options,'B_LIGHT_EMERALD2','3')
        self.craft(options,'B_LIGHT_EMERALD2','4')
        self.craft(options,'B_LIGHT_EMERALD2','5')


# создание всего в летучем корабле
class ExchangeFlyingShip(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeFlyingShipKlevHell']
        self.craft(options,'B_SHIP','1')
        options = self.mega().craft_options()['ExchangeFlyingShipChesn']
        self.craft(options,'B_SHIP','2')
        options = self.mega().craft_options()['ExchangeFlyingShipHelia']
        self.craft(options,'B_SHIP','3')
        options = self.mega().craft_options()['ExchangeFlyingShipTomato']
        self.craft(options,'B_SHIP','4')
        

# ----------------------------------------------------------------------------
# Всё из летучего коробля вразнобой (не подключено в энжине)
# создание клеверхелла (в корабле)
class ExchangeKleverhell(BaseActor):
    def perform_action(self):
        options = {
                'max_result':40000,     # поддерживаем максимум клеверхелла
                'rezerv_1':10000,       # оставляем резерв тыквахелла
                'rezerv_2':10000        # оставляем резерв клевера
                }
        self.craft(options,'B_SHIP','1')

# создание чесночной лилии (в корабле)
class ExchangeChesnLiliy(BaseActor):
    def perform_action(self):
        options = {
                'max_result':10000,     # поддерживаем максимум чесночной лилии
                'rezerv_1':10000,       # оставляем резерв чеснока
                'rezerv_2':10000        # оставляем резерв лилий
                }
        self.craft(options,'B_SHIP','2')

# создание хеллии (в корабле)
class ExchangeHeliya(BaseActor):
    def perform_action(self):
        options = {
                'max_result':2000,      # поддерживаем максимум хеллии
                'rezerv_1':50,          # оставляем резерв клеверхелла
                'rezerv_2':50           # оставляем резерв чесночной лилии
                }
        self.craft(options,'B_SHIP','3')

# создание черепков в томате (в корабле)
class ExchangeTomatoskulls(BaseActor):
    def perform_action(self):
        options = {
                'max_result':12000,     # поддерживаем максимум черепков в томате
                'rezerv_1':1000,        # оставляем резерв момидор
                'rezerv_2':1000         # оставляем резерв костирузы
                }
        self.craft(options,'B_SHIP','4')
# ----------------------------------------------------------------------------

# cоздание мозгов (в останкино)
class ExchangeBrains(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeBrains']
        result, name_result = self.craft(options,'B_OSTANKINO','1')
        if not result:
            self.craft(options,'B_OSTANKINO_CASH','1')

    def clock(self, timems):
        timems = int(timems)
        h = timems/1000/60/60
        m = timems/1000/60 - (h*60)
        s = round(timems/float(1000) - (timems/1000/60*60), 3)
        ms = timems - (timems/1000*1000)
        # print u'Время: %d:%d:%.3f'%(h,m,s)
        return str(h) + ':' + str(m) + ':' + str(s)

# создание трансформаторов (в башне)
class ExchangeTransformator(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeTransformator']
        self.craft(options,'B_PISA','1')

# создание супер-клея (в ёлке)
class ExchangeSuperglue(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeSuperglue']
        self.craft(options,'B_NYTREE','1')
        
# создание болтов (в Эйфелевой башне)
class ExchangeBolt(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeBolt']
        self.craft(options,'B_EIFFEL','1')

# создание зомбаксов (в Вавилоне)
class ExchangeBabel(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeBabel']
        self.craft(options,'B_BABEL','1')

# создание резины (в Бизнес центре)
class ExchangeRubber(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeRubber']
        self.craft(options,'B_BUSINESS','1')

# создание железных сердец (в Вожде)
class ExchangeIronHeart(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeIronHeart']
        self.craft(options,'B_LEADER','1')

# создание синих сердец (в Вожде)
class ExchangeBlueHeart(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeBlueHeart']
        self.craft(options,'B_LEADER','2') 

# создание огня (в Вожде)
class ExchangeFire(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeFire']
        self.craft(options,'B_LEADER','3')

# создание огня (в Цветике)
class ExchangeFire2(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeFire2']
        self.craft(options,'B_FLOWER','1')

# создание досок (в Мельнице)
class ExchangeBoard(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeBoard']
        self.craft(options,'B_MILL','1')

# создание желтой краски (в Пирамиде)
class ExchangeKraska(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeKraska']
        self.craft(options,'B_PYRAMID','1')

# создание дизайнерского яйца (в Семейном гнезде)
class ExchangeDiz(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeDiz']
        self.craft(options,'B_TREE_HOUSE','3')

# создание термо яйца (в Семейном гнезде)
class ExchangeTermo(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeTermo']
        self.craft(options,'B_TREE_HOUSE','4')

# создание любви(сердец) из роз (в Особняке)
class ExchangeLove1(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeLove1']
        self.craft(options,'B_VILLA','1')

# создание любви(сердец) из лилий (в Особняке)
class ExchangeLove2(BaseActor):
    def perform_action(self):
        options = self.mega().craft_options()['ExchangeLove2']
        self.craft(options,'B_VILLA','2')


# 'B_LIGHTHOUSE'            # Маяк
# 'B_PYRAMID'       id 1    # Пирамида. Жёлтая краска
# 'B_WALL_F' # Китайская стена
# u'Сфинкс'
# u'АЭС'
