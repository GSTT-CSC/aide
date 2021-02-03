# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast

import logging
logger = logging.getLogger('esb.dispatcher-plugin')

class Dispatcher(Plugin):
    def __init__(self):
        super().__init__()
        self.description = 'Handle message and dispatch it over the whole workflow'

    def process(self):
        logger.info("Start processing ....")
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        local_variables = {
            "job": self.data.job,
            "data": self.data.data
        }

        processed = False

        for pipe in self.data.config_plugin.workflow.pipeline:
            qualify = False
            if 'condition_complex' in pipe:
                condition = pipe['condition_complex']
                exec(condition, None, local_variables)
                qualify = local_variables["result"] == True
            else:
                condition = pipe['condition']
                qualify = eval(condition, None, local_variables)

            if qualify:
                # we now push job to appropirate queue
                # and when we do return processed TRUE
                # we will save it to database as a stage

                if 'data' in pipe:
                    exec(pipe['data'], None, local_variables)
                    self.data.job = {**self.data.job, **local_variables['data']}

                self.data.job['_stage'] = pipe['stage']
                self.data.msg_queue.job_send(self.data.job, pipe['queue'])
                processed = True

                break
        
        if not processed:
            logger.warn("Have not found relayable pipeline for this JOB: " + self.data.job["_uid"])

        return processed
