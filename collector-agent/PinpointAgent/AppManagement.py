#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# ------------------------------------------------------------------------------
#  Copyright  2020. NAVER Corp.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ------------------------------------------------------------------------------

# Created by eeliu at 9/4/19
import json

from CollectorAgent.CollectorAgentConf import CollectorAgentConf
from Common.Logger import TCLogger
from PinpointAgent.PinpointAgent import PinpointAgent
from PinpointAgent.Type import PHP


class AppManagement(object):
    def __init__(self,collector_conf,service_type=PHP):
        assert isinstance(collector_conf,CollectorAgentConf)
        self.collector_conf = collector_conf
        self.default_appid = self.collector_conf.AgentID
        self.default_appname = self.collector_conf.ApplicationName
        self.app_map = {}
        self.default_app = None
        self.recv_count = 0
        self.createDefaultImplement(service_type)

    def createDefaultImplement(self, service_type):

        self.default_app = self.collector_conf.collector_implement(self.collector_conf, self.default_appid, self.default_appname, service_type)

        self.default_app.start()
        self.app_map[self.default_appid] = self.default_app

    def findApp(self, app_id, app_name, service_type):
        if app_id in self.app_map:
            app = self.app_map[app_id]
            ## check app_name
            if app.app_name != app_name:
                TCLogger.warning(" app_name can't change when using ")
                app = self.default_app
            ## check service_type

        else:
            if service_type == PHP:
                TCLogger.info("collector-agent try to create a new application agent.[%s@%s]",app_id,app_name)
                app = self.collector_conf.collector_implement(self.collector_conf, app_id, app_name)
                app.start()
                self.app_map[app_id] = app
            else:
                raise NotImplementedError("service_type:%d not support",service_type)

        return app

    def stopAll(self):
        for app_id,instance in self.app_map.items():
            assert(isinstance(instance,PinpointAgent))
            TCLogger.info("application is stopping [%s]",app_id)
            instance.stop()
        TCLogger.info("recieved %d span from php-fpm",self.recv_count)

    def handleFrontAgentData(self, client, type, body):
        content = body.decode('utf-8')
        try:
            stack = json.loads(content)
        except Exception as e:
            TCLogger.error("json is crash")
            return
        if 'appid' not in stack:
            appid = self.default_appid
        else:
            appid = stack['appid']

        if 'appname' not in stack:
            appname = self.default_appname
        else:
            appname = stack['appname']

        ft = stack['FT']
        app = self.findApp(appid, appname, ft)
        app.sendSpan(stack,body)
        self.recv_count+=1

    def tellMeWho(self):
        return {
            "time": str(self.collector_conf.startTimestamp),
            "id": self.default_appid,
            "name": self.default_appname
        }