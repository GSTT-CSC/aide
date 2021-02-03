# this task will send error to preconfigured set of emails
# this will be last task - message will not be send anywhere else

# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast
import arrow

# pylint: disable=import-error
# pylint: disable-msg=E0611
from util.Mail import email_error_big

import logging
logger = logging.getLogger('esb.send-error')


class SendError(Plugin):
    def __init__(self):
        super().__init__()
        self.description = 'this task will send error to preconfigured set of emails'

    def process(self):
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        # {
        #     "error_subject": "Not and MRI Series",
        #     "error_problem": "Data send are not valid",
        #     "error_traceback": "None"
        #     "error_link": "http://192.168.50.11/transaction/d2f8753a-fb3d-11ea-9202-0242ac140008"
        # }

        self.data.job["error_desc"]["error_link"] = "http://{}/transaction/{}".format(self.data.config_plugin.appHost, self.data.job["_uid"])
        email_error_big(self.data.config_plugin.mail, self.data.job["error_desc"])

        self.data.job['_stage'] = "error_sent"

        processed = True
        return processed
