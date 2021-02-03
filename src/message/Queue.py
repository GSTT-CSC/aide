class Queue:
    def __init__(self):
        pass

    def init(self, config):
        raise NotImplementedError

    def job_send(self, job, queue_name=None):
        raise NotImplementedError

    def job_recieve(self, callback):
        # callback(job)
        #
        raise NotImplementedError
