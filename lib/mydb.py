from os import getenv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = AsyncIOMotorClient(getenv("MONGODB"))
db = client.get_database("chick")
print("[+] Database Connected")


async def find_list(filter_=None):
    collection = db.get_collection("users")
    if filter_ is not None:
        cursor = collection.find(filter=filter_)
    else:
        cursor = collection.find()
    print("Going for it")
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


async def runtest():
    col = 0
    while True:
        print(col)
        col += 1
        await asyncio.sleep(0.1)


async def main():
    print("In main")
    data = {
        "discord.roles": 22211121}
    filter_ = {"_id": 1002}
    k = await update_data("$pull", filter_, data)
    print(k)
