import json
import arrow
import datetime

from bson.objectid import ObjectId

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, arrow.Arrow):
            return {"__date": obj.isoformat(), "__isDate": True}
        if isinstance(obj, datetime.datetime):
            return {"__date": arrow.get(obj).isoformat(), "__isDate": True}
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def as_date(dct):
    if "__date" in dct:
        return arrow.get(dct['__date'])
    return dct


def as_date_datetime(dct):
    if "__date" in dct:
        return arrow.get(dct['__date']).datetime
    return dct


def to_json(what):
    return json.dumps(what, cls=DateEncoder)


def from_json(what):
    return json.loads(what, object_hook=as_date)


def from_json_db(what):
    return json.loads(what, object_hook=as_date_datetime)
