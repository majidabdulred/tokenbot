from random import choice
from discord import Embed
from discord.ext.commands import Cog, command
from aiohttp import request

lc_cache = dict()
guilds = [632799582350475265, 840234539762843698]


class Slash(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hi", aliases=["Hello", "Hi", "hello", "hola", "hey"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hi', 'Hiya', 'Hey', 'Hola', 'Hello', 'Yo'))} {ctx.author.mention}")

    @command(name="token")
    async def gettoken(self, ctx, tid: int):
        if tid < 1 or tid > 20000:
            await ctx.send("Wrong token ID")
            return
        if tid in lc_cache.keys():
            print("cache")
            data = lc_cache[tid]
            embed = create_embed(data, tid)
            await ctx.send(embed=embed)
        else:
            async with request(method="GET",
                           url=f"https://crun-minter.herokuapp.com/tokens/{tid}") as re:
                data = await re.json()
                embed = create_embed(data, tid)
                lc_cache[tid] = data
                await ctx.send(embed=embed)


def create_embed(acc, tid):
    opensea = f"https://opensea.io/assets/matic/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2/{tid}"
    polygonscan = f"https://polygonscan.com/token/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2?a={tid}"
    embed = Embed(title=acc["name"],
                  description=f"**Opensea** = [Visit]({opensea})\n**Polygonscan** = [Visit]({polygonscan})")
    attributes = acc["attributes"]
    embed.set_author(name=f"Token {tid}")
    for att in attributes:
        if att["value"] is None:
            continue
        embed.add_field(name=att["trait_type"].capitalize(), value=att["value"])
    embed.set_image(url=acc["image_url"])
    return embed


def setup(bot):
    bot.add_cog(Slash(bot))
