import logging
import pika
from util.Serialize import from_json, to_json

import arrow
import logging

from message.Queue import Queue

logger = logging.getLogger('rmq')

# http://192.168.50.11:15672/


class RMQ(Queue):
    def __init__(self):
        super().__init__()

    def init(self, config):
        self.config = config

        credentials = pika.PlainCredentials(
            self.config.config.app.queue.user, self.config.config.app.queue.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.config.config.app.queue.host,
            credentials=credentials
        ))
        self.queue_channel = connection.channel()

    def callback(self, ch, method, properties, body):
        job = from_json(body)
        processed = self.local_callback(job)
        if processed:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_reject(delivery_tag=method.delivery_tag)

    def job_send(self, job, queue_name=None):
        try:
            # read from config if name not provided
            if queue_name is None:
                queue_name = self.config.config.app.queue.name

            jobs = to_json(job)

            self.queue_channel.queue_declare(
                queue=queue_name, durable=True)
            self.queue_channel.basic_publish(exchange='',
                                             routing_key=queue_name,
                                             body=jobs,
                                             properties=pika.BasicProperties(
                                                 delivery_mode=2,  # make message persistent
                                             ))
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as exception:
            # in this case we should reconnect
            logger.exception(exception)
            self.init(self.config)
            self.job_send(job, queue_name)

    def job_recieve(self, callback):
        self.local_callback = callback

        self.queue_channel.queue_declare(
            queue=self.config.config.app.queue.name, durable=True)

        self.queue_channel.basic_qos(prefetch_count=1)
        self.queue_channel.basic_consume(
            queue=self.config.config.app.queue.name, on_message_callback=self.callback)
        self.queue_channel.start_consuming()
