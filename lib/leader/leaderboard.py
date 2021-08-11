from aiohttp import request
from pickle import load as pkload
import asyncio
from lib.db.mydb import find_list, update_data
import datetime as dt
import csv
from pandas import DataFrame
from lib.util import constants as C

df: DataFrame = C.df


def process_owner(data):
    token_list = []
    for token in data:
        token_list.append(int(token["token_id"]))
    return token_list


async def create_leaderboard_data():
    users = await find_list()
    leaderb = {}
    print("On it")
    for kite in users:
        if "score" not in kite.keys():
            continue
        leaderb[kite["_id"]] = kite["score"]
    return leaderb


def create_leaderboard(leaderb):
    leaders = {}
    leaderb_sorted = sorted(leaderb.items(), key=lambda kv: (kv[1], kv[0]))
    leaderb_sorted.reverse()
    top30 = leaderb_sorted[:30]
    for r, cup in enumerate(leaderb_sorted):
        rank = r + 1
        leaders[cup[0]] = {"rank": rank, "score": cup[1]}
    return leaders, top30


async def get_chickens_1(address):
    async with request(method="GET",
                       url=f"http://api.opensea.io/api/v2/assets/matic?asset_contract=0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2&owner_address={address}") as re:
        data = await re.json()
        if re.status != 200:
            if "does not exist for chain matic" in data[0]:
                print("Chain matic Id dont exist")
                raise ValueError("OpenseaApiError", address)
        return data


async def get_next(url):
    async with request(method="GET",
                       url=url) as re:
        data = await re.json()
        if re.status != 200:
            raise ValueError("OpenseaApiError")
        return data


def give_points(results):
    rst: DataFrame = df.loc[df.index.isin(results)]
    lavenvelder = rst.loc[rst["heritage"].isin(["Lakenvelder"])].shape[0]
    sultan = rst.loc[rst["heritage"].isin(["Sultan"])].shape[0]
    dorking = rst.loc[rst["heritage"].isin(["Dorking"])].shape[0]
    serama = rst.loc[rst["heritage"].isin(["Serama"])].shape[0]
    score = serama * 7 + sultan * 5 + lavenvelder * 3 + dorking * 1
    print("\n----Result----")
    print(f"{serama} * 7 + {sultan} * 5 + {lavenvelder} * 3 + {dorking} * 1 = {score}")
    return score


async def update_score(userid, score):
    type_ = "$set"
    filter_ = {"_id": userid}
    data = {"score": score}
    kl = await update_data(filter_=filter_, data=data, type_=type_)
    print("\n", kl)


async def get_chickens(address):
    results = []
    data = await get_chickens_1(address)
    count = 0
    results += data["results"]
    while True:
        count += 1
        if data['next'] is None or count >= 6:
            break
        print("Going again")
        data = await get_next(data['next'])
        results += data["results"]
    return results


async def get_score(address):
    results = await get_chickens(address)
    tokens = process_owner(results)
    return give_points(tokens)



async def refresh_task(kite):
    prev_score = None
    if "score" in kite.keys():
        prev_score = kite["score"]
    address = kite["accounts"][0]["address"]
    if "updatedAt" in kite.keys():
        onehourago = dt.datetime.utcnow() - dt.timedelta(days=2)
        if kite["updatedAt"] > onehourago:
            print("Already updated")
            return
    try:
        score = await get_score(address)
    except Exception as E:
        print(E)
        return
    if prev_score is None or score != prev_score:
        await update_score(kite["_id"], score)
        print("Updated")
    else:
        print("No update needed")


async def refresh():
    users = await find_list()
    print(f"Total Users = {len(users)}")
    user_completed = 0
    for kite in users:
        await refresh_task(kite)
        user_completed += 1
        print(f"User Completed = {user_completed}")


async def count():
    c = 0
    while True:
        c += 1
        print(c, end=" ")
        await asyncio.sleep(0.1)


async def get_leaders():
    C.leader_raw = await create_leaderboard_data()
    # leader_raw = {790077791059574805: 6, 863324115355697182: 31, 690742527665373195: 3}
    # leaderboard = {819506544110338051: {'rank': 1, 'score': 570}, 467459037932290068: {'rank': 2, 'score': 371}}
    # top10 = [(819506544110338051, 570), (467459037932290068, 371), (827602722575745054, 194)]
