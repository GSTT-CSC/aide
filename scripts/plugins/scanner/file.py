# pylint: disable=import-error
from plugin.Plugin import Plugin

from pydicom import dcmread

import time
import os
import re

import logging
logger = logging.getLogger('scanner.file-plugin')


class FileDirectoryScanner(Plugin):
    def __init__(self):
        super().__init__()
        self.description = 'Scan for .dcm files in selected directory'

    def handle_folder(self, path, job):
        series = {}

        for base_path, _directory_names, file_names in os.walk(path):
            # print(root[len(path)+1:], d_names, f_names)
            for file_name in file_names:
                file_path = os.path.join(base_path, file_name)
                local_file_name = re.sub(
                    '[^0-9a-zA-Z]+', '_', base_path[len(path)+1:]) + "_" + file_name

                with open(file_path, 'rb') as infile:
                    ds = dcmread(infile)

                    series_id = ds.get("SeriesInstanceUID", None)
                    if series_id is None:
                        continue

                    series_name = ds.get("SeriesDescription", "Unknown")

                    # print(ds.get("SeriesInstanceUID", None), ds.get("AcquisitionNumber", None))
                    # print(ds.get("SeriesDescription", "Unknown"), ds.get("SeriesInstanceUID", None),
                    #     ds.get("AcquisitionNumber", None), ds.get("InstanceNumber", None))

                    series_key = series_id.replace(
                        ".", "_") + ";" + series_name.replace(";", "_").replace(".", "_")
                    if series_key not in series:
                        series[series_key] = []

                    logger.info('adding image for series: ' +
                                series_name + ", " + series_id)
                    series[series_key].append({
                        "file_name": local_file_name,
                        "id": series_id,
                        "name": series_name,
                        "sort_num": ds.get("InstanceNumber", 0)
                    })

                    # print(ds["SeriesDescription"])

                    # if ds.get("SeriesInstanceUID", None) == "1.3.12.2.1107.5.2.19.46229.2018051607405864241101831.0.0.0":
                    #     for a in ds:
                    #         print(a)
                    #     a = 1

                    # add this as attachment

                    self.data.scanner.job_add_attachment(
                        job, os.path.splitext(local_file_name)[0], ds)

                    del ds
                    infile.close()
        job["_series"] = series

    def handle_file(self, path, file_name, job):
        # Ready dcm files ...
        with open(path, 'rb') as infile:
            ds = dcmread(infile)

            series_id = ds.get("SeriesInstanceUID", None)
            if series_id is None:
                return None

            series_name = ds.get("SeriesDescription", "Unknown")
            series_key = series_id.replace(
                ".", "_") + ";" + series_name.replace(";", "_").replace(".", "_")

            logger.info('adding image for series: ' +
                        series_name + ", " + series_id)

            series = {}
            series[series_key] = []
            series[series_key].append({
                "file_name": file_name + ".dcm",
                "id": series_id,
                "name": series_name,
                "sort_num": ds.get("InstanceNumber", 0)
            })
            job["_series"] = series

            infile.close()
        return ds

    def process(self):
        while True:
            logger.info('checking for new files in folder: ' +
                        self.data.config_plugin.path)

            files_in_directory = os.listdir(self.data.config_plugin.path)
            for single_file in files_in_directory:
                file_name, file_ext = os.path.splitext(single_file)
                if file_ext.lower() == self.data.config_plugin.ready_file:

                    job = self.data.scanner.job_create()

                    study_path = os.path.join(
                        self.data.config_plugin.path, file_name)
                    if self.data.config_plugin.study == True and os.path.isdir(study_path):
                        self.handle_folder(study_path, job)
                    else:
                        # print(file_name, single_file)
                        for attachment_ext in self.data.config_plugin.attachemnts:
                            attachment_file_path = os.path.join(
                                self.data.config_plugin.path, file_name + attachment_ext)
                            # add file to job (this is possible to add more than one)
                            self.data.scanner.job_add_attachment(
                                job, file_name, self.handle_file(attachment_file_path, file_name, job))

                    self.data.scanner.job_send(job)

                    # FIXME: unlink all the files now ....
                    ss = os.path.join(
                        self.data.config_plugin.path, single_file)
                    os.rename(ss, ss + "_done")

            time.sleep(self.data.config_plugin.scanning_period)
