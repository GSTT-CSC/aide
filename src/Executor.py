#!/usr/bin/python

from pydicom import dcmread
from dateutil.tz import tzlocal
from db.DBUtil import InstantiateDB
from message.QueueUtil import InstantiateQueue
from plugin.Manager import PluginManager
from config.Config import Config

import sys
import getopt
import uuid
import os
import pika
import json
import arrow

import logging
logger = logging.getLogger('esb')


PLUGIN_TYPE = "esb"


class ESB:
    def __init__(self, config, config_name):
        self.config = config
        self.config_name = config_name

    def callback(self, job):
        data = []
        for attachment in job['_attachments']:
            path = attachment['_path']
            path = os.path.join(self.config.config.app.destination_path, job['_uid'],
                                path)

            # e = os.path.exists(path)

            # f1 = ds.get(0x00000900)
            # # STATUS ...
            # # ds.add_new(0x00000900, 'US', 0)
            # ds.add_new(0x00000900, 'US', 1)
            # f2 = ds.get(0x00000900)
            # f3 = ds.get("Status")

            # FIXME: this should be maybe exception !
            if os.path.exists(path):
                ds = dcmread(path)
                data.append(ds)

        self.plugin.data.job = job
        self.plugin.data.data = data

        processed = False
        try:
            processed = self.plugin.process()
            if processed == True:
                # ack and save to db
                self.db.store_job_stage(self.plugin.data.job)
            else:
                # for now simply reject and leave as it is !
                pass
        except Exception as ex:
            logger.exception(ex)
            processed = False

        return processed

    def start(self):
        logger.info("Processor server queue start ...")

        pm = PluginManager()
        self.plugin = pm.get(PLUGIN_TYPE, self.config_name)
        self.plugin.data.scanner = self
        self.plugin.data.config_plugin = self.config.config.plugin
        self.plugin.data.config_app = self.config.config.app
        # self.plugin.config = self.config

        logger.info("Processor plugin initialized ...")

        # we getting something from queue and init an object for processing
        # after processing we will save this object to database AS IS
        #

        logger.info('Database initialization ...')
        db = InstantiateDB(self.config.config.app.database.type)
        db.init(self.config)
        self.db = db
        # self.plugin.data.db = db

        logger.info('Initialize message queue ...')
        msg_queue = InstantiateQueue(self.config.config.app.queue.type)
        msg_queue.init(self.config)
        self.msg_queue = msg_queue
        self.plugin.data.msg_queue = msg_queue

        logger.info('Waiting for messages ...')
        msg_queue.job_recieve(self.callback)


# FIXME: move to separate file or move class
try:
    opts, args = getopt.getopt(sys.argv[1:], "hc:o:")
except getopt.GetoptError:
    print(sys.argv[0] + ' -h')
    sys.exit(2)

config = None
for opt, arg in opts:
    if opt == "-c":
        config = arg

logger = logging.getLogger(PLUGIN_TYPE)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

plg_config = Config(PLUGIN_TYPE, config)
# enterprise service bus
ESB(plg_config, config).start()
