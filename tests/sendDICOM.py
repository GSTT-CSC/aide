import json
import pynetdicom
import pydicom

import smtplib
import time

import os
import re

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
MIME-Version: 1.0
Content-type: text/html
Subject: SMTP HTML e-mail test

This is an e-mail message to be sent in HTML format

<b>This is HTML message.</b>
<h1>This is headline.</h1>
"""


def send_test_study_path_remote(path):
    ae = pynetdicom.AE()
    ae.requested_contexts = pynetdicom.StoragePresentationContexts
    assoc = ae.associate('127.0.0.1', 11112)

    if assoc.is_established:
        for base_path, _directory_names, file_names in os.walk(path):
            for file_name in file_names:
                if not file_name.endswith("dcm"):
                    continue
                
                file_path = os.path.join(base_path, file_name)
                # local_file_name = re.sub(
                #     '[^0-9a-zA-Z]+', '_', base_path[len(path)+1:]) + "_" + file_name

                print("Uploading {} ...".format(file_path))

                with open(file_path, 'rb') as infile:
                    ds = pydicom.dcmread(infile)
                    assoc.send_c_store(ds)
                    del ds
                    infile.close()
        assoc.release()
    else:
        print("Error !!!")


def send_test_study_path(path):
    ae = pynetdicom.AE()
    ae.requested_contexts = pynetdicom.StoragePresentationContexts
    assoc = ae.associate('localhost', 11112)

    if assoc.is_established:
        for base_path, _directory_names, file_names in os.walk(path):
            for file_name in file_names:
                file_path = os.path.join(base_path, file_name)
                # local_file_name = re.sub(
                #     '[^0-9a-zA-Z]+', '_', base_path[len(path)+1:]) + "_" + file_name

                with open(file_path, 'rb') as infile:
                    ds = pydicom.dcmread(infile)
                    assoc.send_c_store(ds)
                    del ds
                    infile.close()
        assoc.release()
    else:
        print("Error !!!")


def send_test_study():
    ae = pynetdicom.AE()
    ae.requested_contexts = pynetdicom.StoragePresentationContexts
    # assoc = ae.associate('localhost', 11112)
    assoc = ae.associate('192.168.50.11', 11112)

    if assoc.is_established:
        res = assoc.send_c_store(pydicom.read_file(
            "d:\\Projects\\Fortrus\\ai\\demo\\data\\test_dicom_study_gstt\\Zzzshuaib_Haris___Mr\\Mri_Head - 0\\Localizers_1\\IM-0013-0006.dcm"
        ))
        res = assoc.send_c_store(pydicom.read_file(
            "d:\\Projects\\Fortrus\\ai\\demo\\data\\test_dicom_study_gstt\\Zzzshuaib_Haris___Mr\\Mri_Head - 0\\Localizers_1\\IM-0013-0007.dcm"
        ))
        res = assoc.send_c_store(pydicom.read_file(
            "d:\\Projects\\Fortrus\\ai\\demo\\data\\test_dicom_study_gstt\\Zzzshuaib_Haris___Mr\\Mri_Head - 0\\Localizers_1\\IM-0013-0008.dcm"
        ))

        # time.sleep(6)
        assoc.release()
        return res
    else:
        print("some error?")


def send_email():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        # https://security.google.com/settings/security/apppasswords
        server.login("marcin.dudkowski@cubegames.pl", "<enter your password here>")

        # sender_email = "marcin.dudkowski@lt2.pl"
        # receiver_email = "marcin.dudkowski@fortrus.com"
        # message = """\
        # From: marcin.dudkowski@lt2.pl
        # Subject: Hi there

        # This message is sent from Python."""
        # server.sendmail(sender_email, receiver_email, message)

        sent_from = 'marcin.dudkowski@lt2.pl'
        to = ['marcin.dudkowski@fortrus.com']

        # message = "From: From Person <from@fromdomain.com>\nTo: To Person <to@todomain.com>\nMIME-Version: 1.0\nContent-type: text/html\nSubject: SMTP HTML e-mail test\n\nThis is an e-mail message to be sent in HTML format\n\n<b>This is HTML message.</b>\n<h1>This is headline.</h1>\n"

        server.sendmail(sent_from, to, message)

    except Exception as ex:
        print('Something went wrong...')
        raise ex


def test_message():
    message = """\
    From: marcin.dudkowski@lt2.pl
    Subject: Hi there

    This message is sent from Python."""
    print(message)


# send_test_study()

# send_test_study_path(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\test_dicom_study_gstt\\")


# send_test_study_path_remote(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\test_dicom_study_gstt\\")

send_test_study_path_remote(
    "/Users/dudi/Projects/ai_project/ai_engine/demo/some")

# send_test_study_path_remote(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\t_multi\\")
# send_test_study_path_remote(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\Spectralis OCT\\")
# send_test_study_path_remote(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\Topcon Maestro OCT\\")
# send_test_study_path_remote(
#     "d:\\Projects\\Fortrus\\ai\\demo\\data\\Topcon Triton OCT\\")

# send_email()


# print(json.dumps({
#     "t": message
# }))

# test_message()

# simple send example !
# dcmsend --verbose 192.168.50.11 11112 *.dcm
