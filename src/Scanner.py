#!/usr/bin/python

import sys
import getopt
import uuid
import os
import logging
import pika
import json
import arrow

from config.Config import Config
from plugin.Manager import PluginManager
from message.QueueUtil import InstantiateQueue
from db.DBUtil import InstantiateDB
from dateutil.tz import tzlocal

PLUGIN_TYPE = "scanner"


class Scanner:
    def __init__(self, config, config_name):
        self.config = config
        self.config_name = config_name

    def start(self):
        logger.info("Scanner start ...")

        pm = PluginManager()
        self.plugin = pm.get(PLUGIN_TYPE, self.config_name)
        self.plugin.data.scanner = self
        self.plugin.data.config_plugin = self.config.config.plugin

        logger.info('Initialize message queue ...')
        self.msg_queue = InstantiateQueue(self.config.config.app.queue.type)
        self.msg_queue.init(self.config)

        logger.info('Database initialization ...')
        db = InstantiateDB(self.config.config.app.database.type)
        db.init(self.config)
        self.db = db

        logger.info('Starting ...')
        self.plugin.process()

    def job_create(self):
        return {
            "_uid": str(uuid.uuid1()),
            "_date": arrow.now(),
            # stages:
            # * created
            # * dispatched
            # * [custom name from plugin]
            # * finished
            "_stage": "created",
            "_attachments": list()}

    def ensure_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    # def copy_to_file_system(self, path_from, path_to, is_dir=False):
    #     pass

    # def job_add_attachment_study(self, job, attachment_name, attachment_data):
    #     # FIXME: we may need to handle this or not?
    #     pass
    #     # print("TODO: add attachemnt STUDY: ", job, attachment_name, attachment_data)

    def job_add_attachment(self, job, attachment_name, attachment_data):
        """
        attachment_name : str
            File name or None and filename will be generated.
        attachment_data : pydicom.dataset.Dataset
            The dataset that the peer has requested be stored. 
        """
        if attachment_name is None:
            i = 1
            while True:
                # attachment_name = os.path.join(self.config.config.app.destination_path, job['_uid'], job['_uid'] + "_" + str(i) + ".dcm")
                attachment_name = os.path.join(
                    job['_uid'] + "_" + str(i) + ".dcm")
                if not os.path.exists(os.path.join(self.config.config.app.destination_path, job['_uid'], attachment_name)):
                    break
            # print(attachment_name)
        else:
            attachment_name = os.path.join(attachment_name + ".dcm")

        self.ensure_dir(os.path.join(
            self.config.config.app.destination_path, job['_uid']))
        attachment_data.save_as(
            os.path.join(self.config.config.app.destination_path, job['_uid'], attachment_name), write_like_original=False)

        job["_attachments"].append({
            "_path": attachment_name
        })

    def job_send(self, job):
        try:
            dt = arrow.now().datetime
            self.msg_queue.job_send(job)
            logger.debug("job sent ... {}".format(job['_uid']))
            # now we can save it to database 
            self.db.store_job_stage(job, dt)
            logger.debug("job saved to db ... {}".format(job['_uid']))
        except Exception as exception:
            # FIXME: should we save with error?
            logger.exception(exception)
            raise


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
# fh = logging.FileHandler('scanner.log')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(formatter)
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
# logger.addHandler(fh)
logger.addHandler(ch)

plg_config = Config(PLUGIN_TYPE, config)
Scanner(plg_config, config).start()
# Scanner(config).start()
