# this task will send success information to preconfigured set of emails
# this will be last task - message will not be send anywhere else

# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast
import arrow

# pylint: disable=import-error
# pylint: disable-msg=E0611
from util.Mail import email_success_big

import logging
logger = logging.getLogger('esb.send-success')


class SendSuccess(Plugin):
    def __init__(self):
        super().__init__()
        self.description = 'this task will send success information to preconfigured set of emails'

    def process(self):
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        self.data.job["error_desc"]["success_link"] = "http://{}/transaction/{}".format(self.data.config_plugin.appHost, self.data.job["_uid"])
        email_success_big(self.data.config_plugin.mail, self.data.job["error_desc"])

        self.data.job['_stage'] = "success_sent"

        processed = True
        return processed
