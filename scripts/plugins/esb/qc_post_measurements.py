# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast
import arrow

import logging
logger = logging.getLogger('esb.qc-post-measurements')


class QCPostMeasurements(Plugin):
    def __init__(self):
        super().__init__()
        self.description = ''

    def process(self):
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        self.data.job['_stage'] = "qc_post_done"
        rq = self.data.job['response_queue'] # let's use variable from pipeline !
        self.data.msg_queue.job_send(self.data.job, rq)

        processed = True
        return processed
