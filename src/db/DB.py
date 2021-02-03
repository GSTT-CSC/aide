class DB:
    def __init__(self):
        pass

    def init(self, config):
        raise NotImplementedError

    def store_job_stage(self, job, date=None):
        raise NotImplementedError

    # TODO: we should extend this interface for future use like ie. retrieve previous scan or something ...
