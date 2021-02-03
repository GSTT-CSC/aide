# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast
import arrow
import numpy as np

import logging
logger = logging.getLogger('esb.qc-make-measurements')


class QCMakeMeasurements(Plugin):
    def __init__(self):
        super().__init__()
        self.description = ''

    def find_series_by_id(self, series, serie_id):
        for serie in series:
            for image in series[serie]:
                if image["id"] == serie_id:
                    return (serie, series[serie], image)

        return None

    def process(self):
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        pixels_means = []

        series_mean = dict()
        for dcm in self.data.data:
            series_id = dcm.SeriesInstanceUID
            if series_id is not None and dcm.get_item("PixelData") is not None:
                m = np.mean(dcm.pixel_array)

                serie, serie_object, image = self.find_series_by_id(self.data.job["_series"], series_id)
                if not serie in series_mean:
                    series_mean[serie] = {
                        "means": [],
                        "mean": 0
                    }

                series_mean[serie]["means"].append(m)
                series_mean[serie]["mean"] = np.mean(series_mean[serie]["means"])

                pixels_means.append(m)
            else:
                pixels_means.append(0)

        mean = np.mean(pixels_means)

        self.data.job['qc_object'] = {
            "mean": mean,
            "series_mean": series_mean
        }

        # step 2 - set to display as a demo

        self.data.job['display_Mean'] = round(mean, 2)

        # step 3

        self.data.job['_stage'] = "qc_make_done"
        # let's use variable from pipeline !
        rq = self.data.job['response_queue']
        self.data.msg_queue.job_send(self.data.job, rq)

        processed = True
        return processed
