from db.DB import DB

from pymongo import MongoClient
from util.Serialize import from_json, to_json, from_json_db

import arrow


class Mongo(DB):
    def __init__(self):
        super().__init__()

    def init(self, config):
        host = config.config.app.database.host
        port = int(config.config.app.database.port)
        self.client = MongoClient(host, port)
        self.db = self.client[config.config.app.database.db]
        self.collection = self.db[config.config.app.database.collection]

    def store_job_stage(self, job, date=None):
        # TODO: add _create_date
        # TODO: add something?
        job_deep_copy = from_json_db(to_json(job))
        job_deep_copy["__create_date"] = arrow.now().datetime
        self.collection.insert_one(job_deep_copy)
        pass
