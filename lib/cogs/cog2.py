from random import choice
from discord import Embed, Colour
from discord.ext.commands import Cog, command
from aiohttp import request
from discord_slash import ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.cog_ext import cog_component, cog_slash
from discord.ext.commands.context import Context
import lib.constants as C
from pickle import load as pkload
from pandas import DataFrame
from apscheduler.triggers.cron import CronTrigger

lc_cache = dict()
df: DataFrame = pkload(open("lib/df", "rb"))
df.rename(columns=C.cols_to_rename, inplace=True)
owner = {}


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
               options=[
                   create_option(
                       name="tokenid",
                       description="ID of the Token",
                       option_type=4,
                       required=True)])
    async def getslashtoken(self, ctx, tokenid: int):
        await self.gettoken(ctx, tokenid)

    @cog_slash(name="find",
               guild_ids=C.guild_ids,
               description="This is just a test command, nothing more.",
               options=[
                   create_option(
                       name=category,
                       description="Choose one of the options",
                       option_type=3,
                       required=False,
                       choices=[
                           create_choice(name=trait, value=trait) for trait in C.trait_list[category]])
                   for category in C.trait_list.keys()])
    async def findchicks(self, ctx, **kwargs):
        cons = list(kwargs.items())
        toBeSorted = True
        k = C.filter_index
        prefix = ""
        for con in cons:
            prefix += f"{con[0].capitalize()}-{con[1]} , "
            if con[0] == "perfection":
                k = k & (df[con[0]] == int(con[1]))
                toBeSorted = False
            else:
                k = k & (df[con[0]].isin([con[1]]))
        tokens = list(df.loc[k].sort_values(by=["perfection"], ascending=False).index.tolist())
        no_of_results = len(tokens)
        postfix = ""
        prefix.rstrip(" , ")
        if len(tokens) > 20:
            tokens = tokens[:20]
            postfix += " Top 20 results are shown below."
        elif len(tokens) == 0:
            await ctx.send("Oh that combination doesnt exist")
            return
        if toBeSorted:
            postfix += " Sorted by perfection."
        chicken_data = await self.get_chicken_data(tokens[0])
        embed = create_embed(chicken_data, tokens[0])
        embed.set_author(name=f"1/{len(tokens)}")
        message_id = await ctx.send(f"{prefix}\nFound {no_of_results} chickens.{postfix}", embed=embed,
                                    components=[C.actionrow])
        owner[message_id.id] = tokens

    @command(name="token", aliases=["t"], )
    async def gettoken(self, ctx, tokenid: int):
        if tokenid < 1 or tokenid > 20100:
            await ctx.send(":egg:")
            if isinstance(ctx, Context):
                await ctx.reply(f"{choice(C.choices_egg)}")
            return
        data = await self.get_chicken_data(tokenid)
        embed = create_embed(data, tokenid)
        buttons2 = [create_button(style=ButtonStyle.URL, label="Opensea",
                                  url=f"{C.opensea_link}{tokenid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395"),
                    create_button(style=ButtonStyle.URL, label="Polygonscan",
                                  url=f"https://polygonscan.com/token/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2?a={tokenid}")]
        linkbuttons = create_actionrow(*buttons2)
        await ctx.send(embed=embed, components=[linkbuttons])

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
            chicken_data = await self.get_chicken_data(tokens[0])
            embed = create_embed(chicken_data, tokens[0])
            embed.set_author(name=f"1/{len(tokens)}")
            message_id = await ctx.reply(embed=embed, components=[C.actionrow])
            owner[message_id.id] = tokens

    @cog_component()
    async def next(self, ctx: ComponentContext):
        await self.nextprev(ctx)

    @cog_component()
    async def prev(self, ctx: ComponentContext):
        await self.nextprev(ctx)

    @Cog.listener()
    async def on_ready(self):
        self.bot.scheduler.start()
        print("[+] Ready")
        for ids in C.warn_channel_ids:
            ch = self.bot.get_channel(ids)
            if ch is not None:
                self.warn_channels.append(self.bot.get_channel(ids))
            else:
                print(f"[!] Can't find {ids}")
        self.bot.scheduler.add_job(self.printer, CronTrigger(hour="0,4,8,12,16,20"))

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

    @command(name="del")
    async def delall(self, ctx: Context,all:str):
        if ctx.author.id != 510105779274121216:
            return

        def is_me(m):
            if all == "all":
                return True
            return m.author == self.bot.user

        deleted = await ctx.channel.purge(limit=100, check=is_me)
        await ctx.channel.send('Deleted {} message(s)'.format(len(deleted)))

    async def nextprev(self, ctx: ComponentContext):
        if ctx.origin_message_id not in owner.keys():
            raise ValueError("Message address not in cached database")
        index = int(ctx.origin_message.embeds[0].author.name.split("/")[0]) - 1
        tokens = owner[ctx.origin_message_id]
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
        data = await self.get_chicken_data(token)
        embed = create_embed(data, token)
        embed.set_author(name=f"{index + 1}/{len(tokens)}")
        await ctx.edit_origin(embed=embed, components=[C.actionrow])

    async def get_chicken_data(self, tokenid):
        if tokenid in lc_cache.keys():
            return lc_cache[tokenid]
        async with request(method="GET",
                           url=f"https://crun-minter.herokuapp.com/tokens/{tokenid}") as re:
            if re.status != 200:
                raise ValueError(f"Token address {tokenid} not found")
            data = (await re.json())
            lc_cache[tokenid] = data
            return data


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


def setup(bot):
    bot.add_cog(Slash(bot))
