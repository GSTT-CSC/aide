* 1

```mongo
db.getCollection('history.jobs').aggregate([
    {
        $match: {
            __create_date: {$lte: ISODate("2020-08-29T18:22:27.294+02:00")}
        }
    },
    {
        $sort: {
            __create_date: 1
        }
    },
    {
        $group: {
            _id: "$_uid",
            md: { $max: "$__create_date" },
            mdf: { $first: "$__create_date" },
            name: { $addToSet: "$name" },
        }
    }
    // , { "$unwind": "$name" }
])
```

* 2

```
db.getCollection('history.jobs').find({"_uid" : "e022f7de-ed42-11ea-b4e4-0242ac120009"}).sort({"__create_date": 1})
```
