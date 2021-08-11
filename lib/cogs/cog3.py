from discord.ext.commands import Cog, command
from discord.ext.commands.context import Context
from lib.db.mydb import find_list, insertdata
from random import randint
from discord import Embed, DMChannel, Member
from lib.util.constants import cache_data
import logging
from lib.mylogs.mylogger import getlogger
from lib.leader.leaderboard import get_score

mylogs = getlogger()


class Dbupdate(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(name="submitdata")
    async def submitdata(self, ctx: Context, link: str, address: str):
        cache_data[12345678] = {"user": 510105779274121216, "address": ""}
        if ctx.channel.id != 868331067894013992:
            return
        uid = link.lstrip("https://chickenderby.github.io/verify/?")
        if uid == "" or not uid.isdigit():
            return
        elif int(uid) not in cache_data.keys():
            return
        user = cache_data[int(uid)]["user"]
        previousdata = await find_list({"_id": user.id})
        if len(previousdata) > 0:
            await user.send(f"You are already registered with {previousdata[0]['accounts'][0]['address']}")
            await ctx.reply(f"Already registered with {previousdata[0]['accounts'][0]['address']}")
            mylogs.warning(f"{user.name}'s already stored as {previousdata[0]['accounts'][0]['address']}")
            return
        score = await get_score(address)
        data = {"_id": user.id,
                "discord":
                    {"username": "",
                     "roles": []},
                "accounts": [{
                    "address": address,
                    "chicks": 0}],
                "achievemnts": [],
                "score": score}
        await insertdata(data)
        await user.send(f"Successfully verified your address {address}")
        del cache_data[int(uid)]
        self.bot.leader_raw[user.id] = score
        await self.bot.cogs["LeaderBoard"].giverole((user.id, score))
        await ctx.reply(f"Done and dusted.{score}")


def setup(bot):
    bot.add_cog(Dbupdate(bot))
