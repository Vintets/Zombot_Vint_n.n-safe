# coding=utf-8

from game_state.base import BaseActor
from game_state.game_event import dict2obj

class FreeSpace(BaseActor):

    def spaces(self):
        ostrov = self.location_id()
        map = []
        # Map isle_01   Веры, Мечты
        if(ostrov in ['isle_dream', 'isle_faith']):
            map = [ str(i)+':'+str(j) for i in range(14,16) for j in range(14,16)]
            add = [ str(i)+':'+str(j) for i in range(12,14) for j in range(14,64)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(12,18) for j in range(74,76)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(40,82) for j in range(74,76)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(82,84) for j in range(72,76)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(82,84) for j in range(14,22)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(80,84) for j in range(12,14)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(12,70) for j in range(12,14)]
            map.extend(add)
            crd = {'x1':12, 'x2':83, 'y1':12, 'y2':75}

        # Map world   Домашний
        elif(ostrov in ['main']):
            submap = []
            submap.append(u'снизу от дороги')
            submap.append(u'сверху от дороги')
            if hasattr(self._get_game_state().get_state().location,'openedAreas'):
                openAreas = self._get_game_state().get_state().location.openedAreas
            else: openAreas = []
            if len(openAreas) > 0:
                for area in openAreas:
                    if area == 'second': submap.append(u'за забором')
                    if area == 'mount': submap.append(u'на горе')
            map = [ str(i)+':'+str(j) for i in range(48,62) for j in range(12,48)]
            add = [ str(i)+':'+str(j) for i in range(54,60) for j in range(48,100)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(62,112) for j in range(30,48)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(14,62) for j in range(0,12)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(112,128) for j in range(30,100)]
            map.extend(add)
            if submap != []:
                if not u'снизу от дороги' in submap:
                    add = [ str(i)+':'+str(j) for i in range(14,54) for j in range(48,100)]
                    map.extend(add)
                if not u'сверху от дороги' in submap:
                    add = [ str(i)+':'+str(j) for i in range(60,112) for j in range(48,100)]
                    map.extend(add)
                if not u'за забором' in submap:
                    add = [ str(i)+':'+str(j) for i in range(14,48) for j in range(12,48)]
                    map.extend(add)
                if not u'на горе' in submap:
                    add = [ str(i)+':'+str(j) for i in range(62,128) for j in range(0,30)]
                    map.extend(add)
            crd = {'x1':14, 'x2':127, 'y1':0, 'y2':99}

        # Map isle_02   Альфа, Омега, Пик Админа, Ужасный, Чудовища, Майя, звёздный, гигантов 
        elif(ostrov in ['isle_alpha', 'isle_omega', 'isle_scarecrow', 'isle_elephant', 'isle_monster', 'isle_02', 'isle_star', 'isle_giant']):
            map = [ str(i)+':'+str(j) for i in range(10,12) for j in range(10,12)]
            add = [ str(i)+':'+str(j) for i in range(10,12) for j in range(42,44)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,44) for j in range(42,44)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,44) for j in range(10,12)]
            map.extend(add)
            crd = {'x1':10, 'x2':43, 'y1':10, 'y2':43}

        # Map isle_03   Любви, X, Песочный, Необитаемый
        elif(ostrov in ['isle_03', 'isle_x', 'isle_sand', 'isle_desert']):
            map = []
            crd = {'x1':16, 'x2':65, 'y1':14, 'y2':71}

        # Map isle_04   Надежды, Страшный
        elif(ostrov in ['isle_hope', 'isle_scary']):
            map = [ str(i)+':'+str(j) for i in range(12,14) for j in range(12,14)]
            add = [ str(i)+':'+str(j) for i in range(46,50) for j in range(12,14)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(48,50) for j in range(34,42)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(48,50) for j in range(72,74)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(12,20) for j in range(72,74)]
            map.extend(add)
            crd = {'x1':12, 'x2':49, 'y1':12, 'y2':73}

        # Map isle_05   Город-призрак, Секретный 
        elif(ostrov in ['isle_emerald', 'isle_01']):
            map = [ str(i)+':'+str(j) for i in range(16,20) for j in range(12,16)]
            add = [ str(i)+':'+str(j) for i in range(70,72) for j in range(30,38)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(70,72) for j in range(70,72)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(16,18) for j in range(64,72)]
            map.extend(add)
            crd = {'x1':16, 'x2':71, 'y1':12, 'y2':71}

        # Map isle_snow1   Дремучий, Мобильный, Маленькой ёлочки, Огромной ёлки
        elif(ostrov in ['isle_wild', 'isle_mobile', 'isle_small', 'isle_xxl']):
            map = [ str(i)+':'+str(j) for i in range(8,12) for j in range(6,8)]
            add = [ str(i)+':'+str(j) for i in range(8,10) for j in range(8,10)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,46) for j in range(6,8)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(44,46) for j in range(8,10)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(44,46) for j in range(42,46)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,44) for j in range(44,46)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(8,10) for j in range(44,46)]
            map.extend(add)
            crd = {'x1':8, 'x2':45, 'y1':6, 'y2':45}

        # Map isle_snow2   Полярной ночи, НЛО, Лысая гора, Большой ёлки, Лунный, Вишнёвый
        elif(ostrov in ['isle_polar', 'isle_ufo', 'isle_halloween', 'isle_large', 'isle_moon', 'isle_light']):
            map = [ str(i)+':'+str(j) for i in range(8,12) for j in range(6,10)]
            add = [ str(i)+':'+str(j) for i in range(8,10) for j in range(44,46)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,46) for j in range(44,46)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(44,46) for j in range(42,44)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,46) for j in range(6,8)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(44,46) for j in range(8,10)]
            map.extend(add)
            crd = {'x1':8, 'x2':45, 'y1':6, 'y2':45}

        # Map underground_01 Мраморная
        elif(ostrov in ['un_03', 'un_04', 'un_06', 'un_08']):
            # map = [ str(i)+':'+str(j) for i in range(8,10) for j in range(12,16)]
            # add = [ str(i)+':'+str(j) for i in range(10,12) for j in range(12,14)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(24,28) for j in range(12,14)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(28,34) for j in range(12,16)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(40,46) for j in range(12,14)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(56,58) for j in range(12,14)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(60,62) for j in range(12,40)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(60,62) for j in range(58,72)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(8,24) for j in range(72,74)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(30,62) for j in range(72,74)]
            # map.extend(add)
            # add = [ str(i)+':'+str(j) for i in range(8,10) for j in range(66,72)]
            # map.extend(add)
            # crd = {'x1':8, 'x2':61, 'y1':12, 'y2':73}
            map = []  # грубо
            crd = {'x1':10, 'x2':59, 'y1':16, 'y2':71}  # грубо
        
        # Map underground_02   Склад Хакера 
        elif(ostrov in ['un_09']): 
            map = [ str(i)+':'+str(j) for i in range(14,38) for j in range(14,16)]
            add = [ str(i)+':'+str(j) for i in range(46,52) for j in range(14,16)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(12,14) for j in range(14,18)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(50,52) for j in range(16,28)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(50,52) for j in range(42,74)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(12,14) for j in range(64,74)]
            map.extend(add)
            crd = {'x1':12, 'x2':51, 'y1':14, 'y2':73}

        # Map un_02   Пещеры ЗУ 
        elif(ostrov in ['un_02']):
            map = [ str(i)+':'+str(j) for i in range(12,14) for j in range(14,18)]
            add = [ str(i)+':'+str(j) for i in range(14,38) for j in range(14,16)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(42,46) for j in range(14,17)]
            map.extend(add)
            add = [ str(i)+':'+str(j) for i in range(47,52) for j in range(14,16)]
            map.extend(add)            
            add = [ str(i)+':'+str(j) for i in range(50,52) for j in range(17,28)]
            map.extend(add)            
            add = [ str(i)+':'+str(j) for i in range(50,52) for j in range(42,51)]
            map.extend(add)            
            add = [ str(i)+':'+str(j) for i in range(50,52) for j in range(70,74)]
            map.extend(add)            
            add = [ str(i)+':'+str(j) for i in range(12,14) for j in range(64,74)]
            map.extend(add)            
            crd = {'x1':12, 'x2':51, 'y1':14, 'y2':73}
        
        # Map isle_06   спортивный
        elif(ostrov in ['isle_5years']):
            map = []
            crd = {'x1':18, 'x2':71, 'y1':4, 'y2':65}

        else: crd = {'x1':0, 'x2':0, 'y1':0, 'y2':0}
        
        W = crd['x2'] - crd['x1'] + 1
        H = crd['y2'] - crd['y1'] + 1
        
        space = []
        
        for iw in range(W):
            iw += crd['x1']
            for ih in range(H):
                ih += crd['y1']
                space.append(str(iw)+':'+str(ih))
        
        for m in map:
            space.remove(m)
        objects = self._get_game_state().get_state().gameObjects
        for object in list(objects):
            if not hasattr(object, 'x') or not hasattr(object, 'item'):continue
            reader_object = self._get_item_reader().get(object.item)
            x = object.x
            y = object.y
            if hasattr(object, 'rotate') and object.rotate != 0:ob_anim=reader_object.objAnim[1]
            else:ob_anim = reader_object.objAnim[0]
            
            for rect in self._get_game_state().get_state().rectsObjects:
                if ob_anim == rect.objAnim:
                    h = int(rect.rects.rectH)
                    if int(rect.rects.rectX) < 0:
                        x = int(x) + int(rect.rects.rectX)
                        w = int(rect.rects.rectW) + int(rect.rects.rectX)*-1
                    else:w = int(rect.rects.rectW) + int(rect.rects.rectX)
                    if int(rect.rects.rectY) < 0:
                        y = int(y) + int(rect.rects.rectY)
                        h = int(rect.rects.rectH) + int(rect.rects.rectY)*-1
                    else:h = int(rect.rects.rectH) + int(rect.rects.rectY)
                    for ix in range(w):
                        for iy in range(h):
                            k = str(int(x) + ix)+':'+str(int(y) + iy)
                            if k in space: space.remove(k) 
        return space
        
    def newObject(self, need):
        has_max_id = [_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos] + [_m.id for _m in self._get_game_state().get_state().gameObjects]
        if len(has_max_id) > 1:
            next_id = max(has_max_id) + 1
        elif len(has_max_id) == 1:
            next_id = has_max_id[0] + 1
        else:
            next_id = 1

        # print 'locationInfos', [_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos]
        # print 'objects', [_m.id for _m in self._get_game_state().get_state().gameObjects]
        # print
        # print 'sum', [_i.maxGameObjectId for _i in self._get_game_state().get_state().locationInfos] + [_m.id for _m in self._get_game_state().get_state().gameObjects]
        # print 'next_id', next_id
            
        need = self._get_item_reader().get(need)
        for obj in self._get_game_state().get_state().rectsObjects:
            if str(need.objAnim[0]) == str(obj.objAnim):
                need.w = int(obj.rects.rectW)
                need.h = int(obj.rects.rectH)
        newObjects=[]
        bad_crd = []
        space = self.spaces()
        for coord in space:
            if coord in bad_crd: continue
            x = int(coord[:coord.find(':')])
            y = int(coord[coord.find(':')+1:])
            space_need = [ str(i+x)+':'+str(j+y) for i in range(need.w) for j in range(need.h)]
            free = True
            for coord_need  in space_need:
                #if not coord_need in space: free = False
                if not coord_need in space or coord_need in bad_crd: free = False
            if free:
                if need.type == 'woodTree' or need.type == 'stone':
                    mat_count=int(need.materialCount)
                    new = {u'rotate': 0L, u'materialCount': mat_count, u'item': u'@'+need.id, u'gainStarted': False, u'y': long(y), u'x': long(x), u'type': need.type, u'id': next_id}
                elif need.type == 'decoration':
                    new = {u'rotate': 0L, u'placeTime': u'-69191572', u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': u'decoration', u'id': next_id}
                elif need.type == 'building':
                    new = {u'rotate': 0L, u'level': 0, u'nextPlayTimes': {}, u'playsCounts': {}, u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': u'building', u'id': next_id}
                elif need.type == 'ground' or need.type=='pirateBox':
                    new = {u'rotate': 0L, u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': need.type, u'id': next_id}
                elif need.type == 'pickupBox':
                    new = {u'rotate': 0L, u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': u'pickup', u'id': next_id}
                elif need.type == 'fruitTree':
                    jobFinishTime=int(need.fruitingTime)*1000
                    fruitingCount=int(need.fruitingCount)
                    new = {u'rotate': 0, u'fruitingCount': fruitingCount, u'fertilized': False,
                                        u'item': u'@'+need.id, u'jobFinishTime': jobFinishTime, u'jobStartTime': 0,
                                        u'y': long(y), u'x': long(x), u'type': need.type, u'id': next_id}
                elif need.type== 'pirateShip':
                    new = {u'rotate': 0L, u'level': 0, u'team': [], u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': need.type, u'id': next_id}
                elif need.type == 'pirateBox':
                    new = {u'rotate': 0L, u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': u'pirateBox', u'id': next_id}
                else:
                    new = {u'rotate': 0L, u'item': u'@'+need.id, u'y': long(y), u'x': long(x), u'type': u'notype', u'id': next_id}
                newObjects.append(dict2obj(new))
                bad_crd.extend(space_need)
                next_id += 1
        return newObjects