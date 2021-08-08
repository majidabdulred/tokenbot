from os import getenv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from lib.mylogs.mylogger import getlogger
mylogs = getlogger()

client = AsyncIOMotorClient(getenv("MONGODB"))
db = client.get_database("chick")
mylogs.info("Database Connected")


async def find_list(filter_=None):
    collection = db.get_collection("users")
    if filter_ is not None:
        cursor = collection.find(filter=filter_)
    else:
        cursor = collection.find()
    items = await cursor.to_list(length=500)
    return items


async def insertdata(data):
    collection = db.get_collection("users")
    return await collection.insert_one(data)


async def update_data(type_, filter_, data):
    collection = db.get_collection("users")

    update_ = {
        type_: data,
        "$currentDate": {
            "updatedAt": True
        },
        "$setOnInsert": {
            "createdAt": datetime.utcnow()
        }

    }
    return await collection.update_one(filter_, update_)

