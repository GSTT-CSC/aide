import logging
import arrow
import json
import os
from flask import Flask, request, Response
from flask_cors import CORS
from pymongo import MongoClient
from pydicom import dcmread

from util.Serialize import from_json, to_json, from_json_db

from config.Config import Config
config = Config("api", "api")

logger = logging.getLogger('esb')
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)
CORS(app)


def get_collection():
    host = config.config.app.database.host
    port = int(config.config.app.database.port)
    client = MongoClient(host, port)
    db = client[config.config.app.database.db]
    collection = db[config.config.app.database.collection]
    return collection


def get_fields_names(collection, data_filter=None, filter_db=None):
    data = collection.aggregate([
        {"$sort": {"__create_date": -1}},
        # {"$skip": data_filter['page'] * data_filter['limit']},
        # {"$limit": data_filter['limit']},
        {"$match": {"$and": filter_db}},
        {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT"}}},
        {"$unwind": "$arrayofkeyvalue"},
        {"$match": {"arrayofkeyvalue.k": {"$regex": "display_.*"}}},
        {"$group": {"_id": None, "display_fields": {
            "$addToSet": "$arrayofkeyvalue.k"}}},
        {"$unset": "_id"}
    ])
    fields_display = []
    if data.alive:
        d = data.next()
        for f in d['display_fields']:
            fields_display.append({
                "name": f,
                "display": f[8:]
            })

    return sorted(fields_display, key=lambda field: field['display'])


def get_trasactions_from_db(collection, data_filter=None):
    filter_db = []
    if data_filter['start_date'] is not None:
        filter_db.append(
            {"__create_date": {"$gte": data_filter['start_date'].datetime}})
    if data_filter['end_date'] is not None:
        filter_db.append(
            {"__create_date": {"$lte": data_filter['end_date'].datetime}})

    fields = get_fields_names(collection, data_filter, filter_db)

    grouping = {
        "_id": "$_uid",
        "stage": {"$first": "$_stage"},
        "is_error": {"$max": "$__is_error"},
        "is_finished": {"$max": "$__is_finished"},
        "last_update": {"$max": "$__create_date"}
    }

    for field in fields:
        grouping[field["display"]] = {"$addToSet": "$" + field["name"]}

    no_limir = collection.aggregate([
        {
            "$match": {
                "$and": filter_db
            }
        },
        {
            "$sort": {
                "__create_date": -1
            }
        },
        {"$group": grouping},
        {"$count": "size"}
    ])
    size = no_limir.next()["size"]

    data = collection.aggregate([
        {
            "$match": {
                "$and": filter_db
            }
        },
        {
            "$sort": {
                "__create_date": -1
            }
        },
        {"$group": grouping},
        {
            "$sort": {
                "last_update": -1
            }
        },
        {"$skip": data_filter['page'] * data_filter['limit']},
        {"$limit": data_filter['limit']},
    ])
    all_data = list(data)

    return (all_data, size, fields)


@app.route('/')
def main():
    return ''


@app.route('/transactions', methods=['GET', 'POST'])
def get_transactions():
    if request.method == 'POST':
        collection = get_collection()

        start_date = None
        end_date = None
        if request.json['filter']['start'] is not None:
            start_date = arrow.get(request.json['filter']['start'])
        if request.json['filter']['end'] is not None:
            end_date = arrow.get(request.json['filter']['end'])

        filters = {
            "start_date": start_date,
            "end_date": end_date,
            "page": request.json['filter']['page']['current'],
            "limit": request.json['filter']['page']['max']
        }

        transactions = get_trasactions_from_db(collection, filters)
        return {
            "trasactions": json.loads(to_json(transactions[0])),
            "size": transactions[1],
            "fields": transactions[2]
        }
    else:
        return "NONE"


@app.route('/details/<uid>')
def get_details(uid):
    collection = get_collection()
    data = collection.find({"_uid": uid}).sort([("__create_date", 1)])
    return {
        "details": json.loads(to_json(list(data)))
    }


def logical_trim(v):
    if len(str(v)) > 100:
        return str(v)[:100] + " ..."
    return str(v)


def recurse(ds, list_ref):
    for elem in ds:
        if elem.VR == 'SQ':
            [recurse(item, list_ref) for item in elem]
        else:
            if elem.name.startswith("[CSA") or elem.name.startswith("Pixel Data"):
                continue
            list_ref.append({
                "name": elem.name,
                "tag": str(elem.tag),
                "value": logical_trim(elem.value),
            })


def recurse_simple(ds, list_ref):
    for elem in ds:
        if elem.name.startswith("[CSA") or elem.name.startswith("Pixel Data"):
            continue
        list_ref.append({
            "name": elem.name,
            "tag": str(elem.tag),
            "value": logical_trim(elem.value),
        })


@app.route('/dcm/details/<uid>/<file_name>')
def get_dcm_data(uid, file_name):
    # collection = get_collection()
    # data = collection.find({"_uid": uid}).sort([("__create_date", 1)])
    path = os.path.join(config.config.app.destination_path, uid,
                        file_name)
    dm = None
    if os.path.exists(path):
        ds = dcmread(path)
        dm = list()
        recurse(ds, dm)
        # recurse_simple(ds, dm)

    return {
        "dm": dm
    }


@app.route('/dcm/file/<uid>/<file_name>')
def get_dcm_file(uid, file_name):
    # collection = get_collection()
    # data = collection.find({"_uid": uid}).sort([("__create_date", 1)])
    path = os.path.join(config.config.app.destination_path, uid,
                        file_name)
    # if os.path.exists(path):
    #     return app.send_static_file(path)

    if os.path.exists(path):
        return Response(open(path, "rb").read(), mimetype='application/dicom')

    return None
