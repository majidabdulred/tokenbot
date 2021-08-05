from discord.ext.commands import Cog, command
from discord.ext.commands.context import Context
from lib.mydb import find_list, insertdata
from random import randint
from discord import Embed

from lib.constants import cache_data


class Dbupdate(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="verifytiti", aliases=["join"])
    async def verify(self, ctx: Context):
        uid = randint(111111111111, 999999999999)
        await ctx.reply("Check your DM")
        await ctx.author.send(embed=Embed(title="Verify you address",
                                          description=f" [Click Here](https://majidabdulred.github.io/getaddress/?{uid})"))
        cache_data[uid] = {"user": ctx.author, "address": ""}

    @command(name="verify", aliases=["join"])
    async def verify(self, ctx: Context):
        await ctx.message.delete()
        to_delete = await ctx.reply("Sorry this service is currently unavailable.")
        await to_delete.delete(delay=60)

    @command(name="submitdata")
    async def submitdata(self, ctx: Context, link: str, address: str):
        # cache_data[12345678] = {"user": 510105779274121216, "address": ""}
        if ctx.channel.id != 868331067894013992:
            return
        uid = link.lstrip("https://majidabdulred.github.io/getaddress/?")
        if uid == "" or not uid.isdigit():
            return
        elif int(uid) not in cache_data.keys():
            return
        user = cache_data[int(uid)]["user"]
        previousdata = await find_list({"_id": user.id})
        if len(previousdata) > 0:
            await user.send(f"You are already registered with {previousdata[0]['accounts'][0]['address']}")
            await ctx.reply(f"Already registered with {previousdata[0]['accounts'][0]['address']}")
            print("Data already found")
            return
        data = {"_id": user.id,
                "discord":
                    {"username": "",
                     "roles": []},
                "accounts": [{
                    "address": address,
                    "chicks": 0}],
                "achievemnts": []}
        await insertdata(data)
        del cache_data[int(uid)]
        print("Successfully inserted the data")
        await user.send(f"Successfully verified your address {address}")
        await ctx.reply("Done and dusted.")


def setup(bot):
    bot.add_cog(Dbupdate(bot))
