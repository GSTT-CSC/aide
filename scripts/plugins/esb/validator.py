# here we simply check for hospital number vs NHS number checksum test

# pylint: disable=import-error
from plugin.Plugin import Plugin

import time
import os
import ast
import arrow

import logging
logger = logging.getLogger('esb.validator-plugin')


class Validator(Plugin):
    def __init__(self):
        super().__init__()
        self.description = ''

    def process(self):
        logger.info("Start validation processing ....")
        logger.info("Job ID: " + self.data.job["_uid"])
        logger.info("Job Stage: " + self.data.job["_stage"])

        processed = False

        # step 1 - is it MRI modality

        all_are_valid = True
        for dcm in self.data.data:
            modality = dcm.get_item("Modality")
            if modality is not None and modality.value != b"MR":
                all_are_valid = False
                break

        # step 2 - simply handle the queue

        # all_are_valid = True
        # cnt = 1

        # for dcm in self.data.data:
        #     if dcm.get_item("PixelData") is not None:
        #         from PIL.Image import fromarray
        #         import matplotlib.pyplot as plt
        #         import numpy as np

        #         # slope = float(dcm.RescaleSlope)
        #         # intercept = float(dcm.RescaleIntercept)
        #         # df_data = intercept + dcm.pixel_array * slope

        #         # tell matplotlib to 'plot' the image, with 'gray' colormap and set the
        #         # min/max values (ie 'black' and 'white') to correspond to 
        #         # values of -100 and 300 in your array
        #         # plt.imshow(df_data, cmap='gray', vmin=-100, vmax=300)

        #         # save as a png file
        #         # plt.imshow(dcm.pixel_array, cmap=plt.cm.gray)
        #         # print(dcm[(0x28,0x4)])
        #         # plt.imshow(dcm.pixel_array, cmap=plt.cm.gray)
        #         # plt.savefig('d:\\zz\\a\\png-copy.png')

        #         try:
        #             # a = (dcm.pixel_array * 255).astype(np.uint8)
        #             # im = fromarray(a)
        #             # im = fromarray(dcm.pixel_array)
        #             # print(dcm.pixel_array.shape)
        #             if len(dcm.pixel_array.shape) > 2 and dcm.pixel_array.shape[2] > 3: # jak nie rgb to bedzie wiecej niz 3 - problem ale na test ok !
        #                 # this is multiframe !
                        
        #                 frames_cnt = dcm.pixel_array.shape[0]
        #                 # frame = 1
        #                 if not os.path.exists(f'd:\\zz\\a\\{cnt:04d}_{dcm.SeriesInstanceUID}'):
        #                     os.makedirs(f'd:\\zz\\a\\{cnt:04d}_{dcm.SeriesInstanceUID}')

        #                 for frame in range(frames_cnt):
        #                     im = fromarray(np.uint8(dcm.pixel_array[frame]))
        #                     im.save(f'd:\\zz\\a\\{cnt:04d}_{dcm.SeriesInstanceUID}\\img_{frame + 1:04d}.png')
        #             else:
        #                 im = fromarray(np.uint8(dcm.pixel_array))
        #                 im.save(f'd:\\zz\\a\\img_{cnt:04d}_{dcm.SeriesInstanceUID}.png')
        #             # import cv2
        #             # cv2.imwrite(f'd:\\zz\\a\\img_{cnt}_{dcm.SeriesInstanceUID}.jpg', dcm.pixel_array)
        #         except Exception as exception:
        #             logger.exception(exception)
        #             pass
        #         cnt = cnt + 1

        if not all_are_valid:
            self.data.job["error_desc"] = {
                "error_subject": "Not and MRI Series",
                "error_problem": "Data send are not valid",
                "error_traceback": "-- There is an image which is not MRI --"
            }
            self.data.job["__is_error"] = True
            self.data.msg_queue.job_send(self.data.job, "error")
            
            self.data.job['display_ERROR'] = "Not an MRI"
            self.data.job['_stage'] = "error"

            processed = True
        else:
            self.data.job["validated"] = {
                "status": True,
                "when": arrow.now()
            }
            self.data.job['_stage'] = "validated"

            rq = self.data.job['response_queue']
            self.data.msg_queue.job_send(self.data.job, rq)

            processed = True

        # let's check
        # there always should be some kind of error / status / rejected queue ...

        return processed
