# -*- coding: utf-8 -*-
import game_state.vkutils
import game_state.mrutils
import game_state.okutils

def Site(settings):
    if settings.getSite() == 'vk':
        return game_state.vkutils.VK(settings)
    elif settings.getSite() == 'mr':
        return game_state.mrutils.MR(settings)
    else:
        return game_state.okutils.OK(settings)
