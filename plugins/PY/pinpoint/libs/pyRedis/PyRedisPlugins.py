#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created by eeliu at 8/20/20


import pinpointPy

from pinpoint.common import *


class PyRedisPlugins(Candy):

    def __init__(self,name):
        super().__init__(name)
        self.dst = ''

    def onBefore(self,*args, **kwargs):
        super().onBefore(*args, **kwargs)
        ###############################################################
        pinpointPy.add_clue(PP_INTERCEPTER_NAME,self.getFuncUniqueName())
        pinpointPy.add_clue(PP_SERVER_TYPE, PP_REDIS)
        arg = self.get_arg(*args, **kwargs)
        pinpointPy.add_clues(PP_ARGS, arg)
        ###############################################################
        if self.func_name == 'Redis':
            if 'host' in kwargs:
                self.dst = kwargs['host']+str(kwargs['port'])
            elif 'unix_socket_path' in kwargs:
                self.dst = kwargs['host'] + str(kwargs['port'])

        pinpointPy.add_clue(PP_DESTINATION, self.dst)
        return args,kwargs

    def onEnd(self,ret):
        ###############################################################
        pinpointPy.add_clues(PP_RETURN,str(ret))
        ###############################################################
        super().onEnd(ret)
        return ret

    def onException(self, e):
        pinpointPy.add_clue(PP_ADD_EXCEPTION,str(e))

    def get_arg(self, *args, **kwargs):
        args_tmp = {}
        j = 0

        for i in args:
            args_tmp["arg["+str(j)+"]"] = (str(i))
            j += 1
        # print(str(args_tmp))
        for k in kwargs:
            args_tmp[k] = kwargs[k]
        # print(str(args_tmp))
        return str(args_tmp)
