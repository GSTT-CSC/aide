# pylint: disable=import-error
from plugin.Plugin import Plugin
# pylint: disable=import-error
# pylint: disable-msg=E0611
from util.Mail import email_error
from pydicom import dcmread

import time
import os
import re
import pynetdicom
import uuid

import logging
logger = logging.getLogger('scanner.dicom-plugin')


class DICOMScanner(Plugin):
    def __init__(self):
        super().__init__()
        self.description = 'DICOM server for scanner interface'

        self.assoc_jobs = {}

    def handle_assoc_start(self, event):
        k = str(event.assoc.native_id)

        logger.info("new association established ... [{}]".format(k))

        # if k not in self.assoc_jobs:
        #     self.assoc_jobs[k] = {}
        self.assoc_jobs[k] = self.data.scanner.job_create()

    def handle_assoc_finish(self, event):
        k = str(event.assoc.native_id)

        if k not in self.assoc_jobs:
            logger.error(
                "association already gone / before close ... [{}]".format(k))
        else:
            logger.info(
                "association ginished ... [{}] ... saving job".format(k))

            # print(repr(self.assoc_jobs[k]))
            self.data.scanner.job_send(self.assoc_jobs[k])

            del self.assoc_jobs[k]

    def handle_assoc_error(self, event):
        msg = "{} [ {} ]".format(event.event.description, event.event.name)
        logger.error(msg)
        email_error(self.data.config_plugin.mail, msg)

    def handle_store(self, event):
        try:
            """Handle a C-STORE request event."""
            k = str(event.assoc.native_id)

            event.dataset.file_meta = event.file_meta
            ds = event.dataset

            # TODO: maybe lets make file name more human readable
            file_name = str(uuid.uuid4())

            series_id = ds.get("SeriesInstanceUID", None)
            if series_id is None:
                return None

            series_name = ds.get("SeriesDescription", "Unknown")
            series_key = series_id.replace(
                ".", "_") + ";" + series_name.replace(";", "_").replace(".", "_")

            logger.info('adding image for series: ' +
                        series_name + ", " + series_id)

            if "_series" not in self.assoc_jobs[k]:
                series = {}
            else:
                series = self.assoc_jobs[k]["_series"]
            if series_key not in series:
                series[series_key] = []
            series[series_key].append({
                "file_name": file_name + ".dcm",
                "id": series_id,
                "name": series_name,
                "sort_num": ds.get("InstanceNumber", 0)
            })
            self.assoc_jobs[k]["_series"] = series

            self.data.scanner.job_add_attachment(
                self.assoc_jobs[k], file_name, ds)

            # Return a 'Success' status
            return 0x0000
        except Exception as exception:
            logger.exception(exception)

            # Return a 'Error' status
            return 0x0211

    def process(self):
        self.ae = pynetdicom.AE()
        self.ae.network_timeout = int(self.data.config_plugin.net_timeout)
        self.ae.supported_contexts = pynetdicom.AllStoragePresentationContexts

        # Start listening for incoming association requests
        handlers = [
            (pynetdicom.evt.EVT_C_STORE, self.handle_store),

            (pynetdicom.evt.EVT_ESTABLISHED, self.handle_assoc_start),
            (pynetdicom.evt.EVT_ABORTED, self.handle_assoc_error),
            (pynetdicom.evt.EVT_REJECTED, self.handle_assoc_error),

            (pynetdicom.evt.EVT_RELEASED, self.handle_assoc_finish)
        ]
        self.ae.start_server(
            ('', int(self.data.config_plugin.port)), evt_handlers=handlers)
