import asyncio
from random import randint

from aiohttp import request
from lib.util import constants as C
from discord.ext.commands import Cog, command
from discord import Embed, Colour, Member, DMChannel
from lib.leader.leaderboard import create_leaderboard, create_leaderboard_data
from os import getenv
from lib.mylogs.mylogger import getlogger
from lib.util.constants import cache_data

mylogs = getlogger()
bot1 = getenv("BOT1")
bot2 = getenv("BOT2")
bot3 = getenv("BOT3")
bot4 = getenv("BOT4")
bot5 = getenv("BOT5")
bottokens = [bot1, bot2, bot3, bot4, bot5]


class LeaderBoard(Cog):

    def __init__(self, bot):
        self.bot = bot

    # @command(name="leaders")
    # async def lead(self, ctx):
    #     await self.leaderboard()
    @command(name="verify", aliases=["join"])
    async def verify(self, ctx):
        mylogs.info(f"{ctx.author.name} used verify")
        uid = ctx.author.id
        if not isinstance(ctx.channel, DMChannel):
            mes = await ctx.reply("Please Wait..")
            C.to_be_handled.append((mes, ctx))
            return
        await ctx.send(embed=Embed(title="Verify you address",
                                   description=f" [Click Here](https://chickenderby.github.io/verify/?{uid})"))

        cache_data[uid] = {"user": ctx.author, "address": ""}

    async def leaderboard(self):
        if self.bot.leader_raw is None:
            self.bot.leader_raw = await create_leaderboard_data()
        # prev_top30 = self.bot.top30
        # self.bot.leaderboard, self.bot.top30 = create_leaderboard(self.bot.leader_raw)
        # if self.bot.message_board is None:
        #     ch = self.bot.get_channel(874679638364946582)
        #     self.bot.message_board = await ch.fetch_message(874305955444162590)
        # if prev_top30 != self.bot.top30:
        #     embed = create_another_embed(self.bot.top30)
        #     await self.bot.message_board.edit(embed=embed)

    def which_role(self, points):
        if points > 200:
            return C.cluck_norris
        elif points > 100:
            return C.attila
        elif points > 50:
            return C.chicking
        elif points >= 15:
            return C.coop
        elif points >= 1:
            return C.coop
        else:
            mylogs.warning(f"I think its {points}")
            return None

    async def giverole(self, user):
        allroles = [C.cluck_norris, C.chicking, C.coop, C.attila, C.rancher]
        role = self.which_role(user[1])
        if role is not None:
            allroles.remove(role)
        mem = self.main_guild.get_member(user[0])
        if mem is None:
            mylogs.warning(f"Not found {user[0]}")
            return
        for ee in allroles:
            if ee in mem.roles:
                await mem.remove_roles(*allroles)
                break
        if role is not None:
            await mem.add_roles(role)
            mylogs.info(f"{mem.name} given {role.name}")
        else:
            mylogs.info("It was 0")

    @command(name="giveroles")
    async def giveroles(self, ctx):
        mylogs.info(f"{ctx.author} used giveroles")
        alla = len(self.bot.leader_raw.keys())
        count = 0
        for user in self.bot.leader_raw.items():
            try:
                await self.giverole(user)
            except Exception as E:
                mylogs.error(E)
                pass
            count += 1
            print(f"{count}/{alla}")

    @command(name="set")
    async def addd(self, ctx, mem: Member, num: int):
        mylogs.info(f"{ctx.author} used set")
        self.bot.leader_raw[mem.id] = num
        # await self.leaderboard()
        await self.giverole((mem.id, num))

    @Cog.listener()
    async def on_ready(self):
        loop = asyncio.get_event_loop()
        loop.create_task(handle_tasks(self.bot))
        await self.leaderboard()
        self.main_ch = await self.bot.fetch_channel(C.main_ch)
        self.main_guild = self.main_ch.guild
        roles = self.main_guild.roles
        print(roles)
        for i in roles:
            if i.id == C.attila:
                C.attila = i
            elif i.id == C.coop:
                C.coop = i
            elif i.id == C.chicking:
                C.chicking = i
            elif i.id == C.cluck_norris:
                C.cluck_norris = i
            elif i.id == C.rancher:
                C.rancher = i
        print(C.cluck_norris, C.chicking, C.attila, C.coop, C.rancher)


async def get_dm_channel_id(bot, bottoken, userid):
    headers = {"Authorization": f"Bot {bottoken}", "Content-Type": "application/json"}
    data = {"recipient_id": userid}
    link = "https://discord.com/api/v9/users/@me/channels"
    async with request("POST", link, headers=headers, json=data) as re:
        if re.status != 200:
            await bot.error_channel.send(f"{bottoken} gave an error")
            mylogs.warning(f"{bottoken} gave an error")
        res = await re.json()
        return res["id"], bottoken


async def get_dm_channel_id_again(bot, bottoken, userid):
    await bot.error_channel.send(f"Error Occured with {bottoken}")
    bottoken = bottokens[bottokens.index(bottoken) + 1]
    headers = {"Authorization": f"Bot {bottoken}", "Content-Type": "application/json"}
    data = {"recipient_id": userid}
    link = "https://discord.com/api/v9/users/@me/channels"
    async with request("POST", link, headers=headers, json=data) as re:
        if re.status != 200:
            await bot.error_channel.send(f"Critical Crictical Critical{bottoken} {userid}")
            mylogs.critical(f"Critical Crictical Critical{bottoken} {userid}")
            raise ValueError
        res = await re.json()
        return res["id"], bottoken


async def send_the_dm(bot, dmchannelid, bottoken, uid):
    header = {"Authorization": f"Bot {bottoken}", "Content-Type": "application/json"}
    data = {
        "embeds": [{
            "title": "Verify you address",
            "description": f"[Click Here](https://chickenderby.github.io/verify/?{uid})"
        }]
    }
    link = f"https://discord.com/api/v9/channels/{dmchannelid}/messages"
    async with request("POST", link, headers=header, json=data) as re:
        if re.status != 200:
            await bot.error_channel.send(f"Critical Crictical Critical{bottoken} {uid}")
            raise ValueError
        re = await re.json()
        return re["id"]


async def handle_dms(bot, token):
    mes, ctx = C.to_be_handled.pop(0)
    uid = ctx.author.id
    dmchannelid, bottoken = await get_dm_channel_id(bot, token, uid)
    success = await send_the_dm(bot, dmchannelid, bottoken, uid)
    cache_data[uid] = {"user": ctx.author, "address": ""}
    await mes.edit(content="Please check your Dm")
    mylogs.info(f"Success {success}")


async def handle_tasks(bot):
    loop = asyncio.get_event_loop()
    count = 0
    while True:
        if len(C.to_be_handled) == 0:
            await asyncio.sleep(5)
            continue
        token = bottokens[count]
        loop.create_task(handle_dms(bot, token))
        print("To be handled", len(C.to_be_handled))
        if count >= len(bottokens) - 1:
            count = 0
        else:
            count += 1
        await asyncio.sleep(1)


def create_another_embed(data):
    description = ""
    for no, cup in enumerate(data):
        description += f"**#{no + 1}  •  {cup[1]}** Points ** • **  <@{cup[0]}>\n"
    embed = Embed(title="Chicken Leaderboard", description=description, colour=Colour.blue())
    return embed


def setup(bot):
    bot.add_cog(LeaderBoard(bot))
