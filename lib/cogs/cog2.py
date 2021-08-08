from random import choice
import datetime as dt
from discord import Embed, Colour, DMChannel
from discord.ext.commands import Cog, command
from aiohttp import request
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.cog_ext import cog_component, cog_slash
from discord.ext.commands.context import Context
import lib.util.constants as C
from lib.util.utils import create_embed, process_owner, get_chicken_data, nextprev, random_verification
from apscheduler.triggers.cron import CronTrigger
from lib.mylogs.mylogger import getlogger
mylogs = getlogger()
df = C.df


class Slash(Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = []
        self.warn_channels = []

    @command(name="hi", aliases=["Hello", "Hi", "hello", "hola", "hey"])
    async def say_hello(self, ctx):
        await ctx.reply(f"{choice(('Hi', 'Hiya', 'Hey', 'Hola', 'Hello', 'Yo'))} {ctx.author.mention}")

    @cog_slash(name="token", guild_ids=C.guild_ids,
               description="Choose a token",
               options=C.options_token)
    async def getslashtoken(self, ctx, tokenid: int):
        await self.gettoken(ctx, tokenid)

    @cog_slash(name="find",
               guild_ids=C.guild_ids,
               description="This is just a test command, nothing more.",
               options=C.options_find)
    async def findchicks(self, ctx, **kwargs):
        cons = list(kwargs.items())
        toBeSorted = True
        k = C.filter_index
        prefix = "/find "
        for con in cons:
            prefix += f"{con[0]}:{con[1]} "
            if con[0] == "perfection":
                k = k & (df[con[0]] == int(con[1]))
                toBeSorted = False
            else:
                k = k & (df[con[0]].isin([con[1]]))
        tokens = list(df.loc[k].sort_values(by=["perfection"], ascending=False).index.tolist())
        no_of_results = len(tokens)
        postfix = ""
        if len(tokens) > 20:
            tokens = tokens[:20]
            postfix += " Top 20 results are shown below."
        elif len(tokens) == 0:
            await ctx.send("Oh that combination doesnt exist")
            return
        if toBeSorted:
            postfix += " Sorted by perfection."
        chicken_data = await get_chicken_data(tokens[0])
        embed = create_embed(chicken_data, tokens[0])
        embed.set_author(name=f"1/{len(tokens)}")
        message_id = await ctx.send(f"{prefix}\nFound {no_of_results} chickens.{postfix}", embed=embed,
                                    components=[C.actionrow])
        C.owner[message_id.id] = tokens
        await random_verification(self.bot.data_channel, ctx)

    @command(name="token", aliases=["t"], )
    async def gettoken(self, ctx, tokenid: int):
        if tokenid < 1 or tokenid > 20100:
            await ctx.send(":egg:")
            if isinstance(ctx, Context):
                await ctx.send(f"{choice(C.choices_egg)}")
            return
        data = await get_chicken_data(tokenid)
        embed = create_embed(data, tokenid)
        buttons2 = [create_button(style=ButtonStyle.URL, label="Opensea",
                                  url=f"{C.opensea_link}{tokenid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395"),
                    create_button(style=ButtonStyle.URL, label="Polygonscan",
                                  url=f"https://polygonscan.com/token/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2?a={tokenid}")]
        linkbuttons = create_actionrow(*buttons2)
        await ctx.send(f"{ctx.author.mention}", embed=embed, components=[linkbuttons])
        await random_verification(self.bot.data_channel, ctx)

    @command(name="owner", aliases=["o"])
    async def owner_tokens(self, ctx, address):
        if len(address) != 42:
            raise ValueError("LenAddress", address)
        async with request(method="GET",
                           url=f"http://api.opensea.io/api/v2/assets/matic?asset_contract_address=0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2&owner={address}") as re:
            data = await re.json()
            if re.status != 200:
                raise ValueError("OpenseaApiError", address)
            if len(data["results"]) == 0:
                await ctx.reply(f"Oops! Seems like {address} has no Chicken")
            tokens = process_owner(data["results"])
            embed = create_embed(await get_chicken_data(tokens[0]), tokens[0])
            embed.set_author(name=f"1/{len(tokens)}")
            message_id = await ctx.reply(embed=embed, components=[C.actionrow])
            C.owner[message_id.id] = tokens
            await random_verification(self.bot.data_channel, ctx)

    @cog_component()
    async def next(self, ctx):
        await nextprev(ctx)

    @cog_component()
    async def prev(self, ctx):
        await nextprev(ctx)

    @Cog.listener()
    async def on_ready(self):
        self.bot.scheduler.start()
        for ids in C.warn_channel_ids:
            ch = self.bot.get_channel(ids)
            if ch is not None:
                self.warn_channels.append(self.bot.get_channel(ids))
            else:
                mylogs.warning(f"[!] Can't find {ids}")
        self.bot.scheduler.add_job(self.printer, CronTrigger(hour="0,4,8,12,16,20"))

    async def printer(self):
        embed = Embed(colour=Colour.red(),
                      description=C.warning_message)
        for ch in self.warn_channels:
            await ch.purge(limit=20, check=self.warn_messages)
            await ch.send(embed=embed)
            mylogs.info(f"Send warning to {ch.name}")

    @staticmethod
    def warn_messages(mess):
        if len(mess.embeds) == 0:
            return False
        if mess.embeds[0].description == C.warning_message:
            return True
        return False

    @command(name="del")
    async def delall(self, ctx):
        yesterday = dt.datetime.utcnow() - dt.timedelta(days=1)
        if ctx.author.id != 510105779274121216:
            return
        if isinstance(ctx.channel, DMChannel):
            messages = [mess async for mess in ctx.channel.history(limit=100)]
            for i in messages:
                if i.author == self.bot.user:
                    await i.delete()
            return

        deleted = await ctx.channel.purge(limit=100)
        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))


def setup(bot):
    bot.add_cog(Slash(bot))
