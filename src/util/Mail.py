import json
import smtplib


def email_error(config, error_text, is_html=True):
    server = smtplib.SMTP(config.smtp_host, config.smtp_port)
    server.ehlo()
    server.starttls()
    server.login(config.smtp_user, config.smtp_password)

    message = """From: {}
To: {}
MIME-Version: 1.0
Content-type: text/html
Subject: {}

{}
"""
    eml = config.error_message_template.format(error_text)
    formated_message = message.format(config.email_from, ', '.join(
        config.email_to), config.email_subject, eml)
    server.sendmail(config.email_from, config.email_to, formated_message)


def email_error_big(config, error_object, is_html=True):
    server = smtplib.SMTP(config.smtp_host, config.smtp_port)
    server.ehlo()
    server.starttls()
    server.login(config.smtp_user, config.smtp_password)

    message = """From: {}
To: {}
MIME-Version: 1.0
Content-type: text/html
Subject: {}

{}
"""
    eml = config.error_message_template.format(error_object["error_problem"],
                                               error_object["error_traceback"], error_object["error_link"])
    formated_message = message.format(config.email_from, ', '.join(
        config.email_to), config.email_subject.format(error_object["error_subject"]), eml)
    server.sendmail(config.email_from, config.email_to, formated_message)


def email_success_big(config, success_object, is_html=True):
    server = smtplib.SMTP(config.smtp_host, config.smtp_port)
    server.ehlo()
    server.starttls()
    server.login(config.smtp_user, config.smtp_password)

    message = """From: {}
To: {}
MIME-Version: 1.0
Content-type: text/html
Subject: {}

{}
"""
    eml = config.error_message_template.format(
        success_object["success_message"], success_object["success_link"])
    formated_message = message.format(config.email_from, ', '.join(
        config.email_to), config.email_subject.format(success_object["success_subject"]), eml)
    server.sendmail(config.email_from, config.email_to, formated_message)
