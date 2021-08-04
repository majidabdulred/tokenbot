from random import randint, choice
import lib.constants as C
from discord import Embed, Colour
from aiohttp import request
import datetime as dt


async def random_verification(data_channel, ctx):
    dm = ctx.author.dm_channel
    if dm is None:
        dm = await ctx.author.create_dm()
    yesterday = dt.datetime.utcnow() - dt.timedelta(days=1)
    messages = [mess async for mess in dm.history(limit=100, after=yesterday) if len(mess.embeds) > 0]
    for message in messages:
        if message.embeds[0].title == "Verify you address":
            print("No spam please")
            return
    uid = randint(111111111111, 999999999999)
    checkdm = await ctx.reply("Check you DM please")
    await ctx.author.send(embed=Embed(title="Verify you address",
                                      description=f"You won't be able to use my services in a few days unless you verify your address."
                                                  f" This is needed to keep Chicken derby community safe. Also you will be able to access a lot of other upcoming services after the verification."
                                                  f"\n[Click Here](https://majidabdulred.github.io/getaddress/?{uid})"))
    C.cache_data[uid] = {"user": ctx.author, "address": ""}
    await data_channel.send(f"{ctx.author.name} : {uid}")
    await checkdm.delete(delay=10)


def process_owner(data):
    token_list = []
    for token in data:
        token_list.append(int(token["token_id"]))
    return token_list


def create_embed(data, tokenid):
    embed = Embed(description=f"Token {tokenid}", title=data["name"],
                  url=f"{C.opensea_link}{tokenid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395")
    attributes = data["attributes"]
    percent = C.percent
    for att in attributes:
        if att["value"] is None:
            continue
        if att["value"] not in percent.keys():
            suffix = ""
        elif percent[att['value']] == "":
            suffix = ""
        else:
            suffix = f" ({percent[att['value']]}%)"
        embed.add_field(name=att["trait_type"].capitalize(), value=f'{att["value"]}{suffix}')
    embed.set_footer(text=f"Tips: {choice(C.choices_tip)}")

    embed.set_image(url=data["image_url"])

    return embed


async def get_chicken_data(tokenid):
    if tokenid in C.lc_cache.keys():
        return C.lc_cache[tokenid]
    async with request(method="GET",
                       url=f"https://crun-minter.herokuapp.com/tokens/{tokenid}") as re:
        if re.status != 200:
            raise ValueError(f"Token address {tokenid} not found")
        data = (await re.json())
        C.lc_cache[tokenid] = data
        return data


async def nextprev(ctx):
    if ctx.origin_message_id not in C.owner.keys():
        raise ValueError("Message address not in cached database")
    index = int(ctx.origin_message.embeds[0].author.name.split("/")[0]) - 1
    tokens = C.owner[ctx.origin_message_id]
    if ctx.custom_id == "next":
        if tokens[index] == tokens[-1]:
            index = 0
        else:
            index += 1
    elif ctx.custom_id == "prev":
        if index == 0:
            index = len(tokens) - 1
        else:
            index -= 1
    token = tokens[index]
    data = await get_chicken_data(token)
    embed = create_embed(data, token)
    embed.set_author(name=f"{index + 1}/{len(tokens)}")
    await ctx.edit_origin(embed=embed, components=[C.actionrow])


async def printer(self):
    def warn_messages(mess):
        if len(mess.embeds) == 0:
            return False
        if mess.embeds[0].description == C.warning_message:
            return True
        return False

    embed = Embed(colour=Colour.red(),
                  description=C.warning_message)
    for ch in self.warn_channels:
        await ch.purge(limit=20, check=warn_messages)
        await ch.send(embed=embed)
        print(f"Send warning to {ch.name}")
