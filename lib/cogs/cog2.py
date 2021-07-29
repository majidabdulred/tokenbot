from discord.ext import tasks
from random import choice
from discord import Embed, Colour
from discord.ext.commands import Cog, command
from aiohttp import request
from discord_slash import ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.cog_ext import cog_component, cog_slash
from discord.ext.commands.context import Context

buttons = [create_button(style=ButtonStyle.green, label="Previous", custom_id='prev'),
           create_button(style=ButtonStyle.green, label="Next", custom_id='next')]
actionrow = create_actionrow(*buttons)
lc_cache = dict()
owner = {}
warn_channel_ids = [854215344075440138, 866666604092063754, 854418136890474576, 854418163122307142]
percent = {'Alien': 0.91, 'Amethyst': 10, 'Angry': 9, 'Anvil': 7, 'Autumn': 10, 'Bald Chicken': 13, 'Beauty': 9,
           'Black': 10, 'Black Hole': 0.51, 'Bloodshot': 9, 'Blue': 15, 'Blue Egg': 3, 'Blue Rooster': 7, 'Bulging': 9,
           'CK-47': 7, 'Candy': 2, 'Cherry Dusk': 0.54, 'Chicken': 24, 'Chickenapult': 8, 'Classic': 0.83,
           'Cockeyed': 9,
           'Cold Snap': 2, 'Coober': 8, 'Crosseyed': 9, 'Determined': 9, 'Devolution': 2, 'Dig': 4, 'Dorking': 45,
           'Eggshell': 13, 'English Mustard': 13, 'Exhausted': 9, 'Eyepatch': 0.85, 'Fan Group': 4, 'Flesh': 9,
           'Flight?': 7, 'Gold': 31, 'Green': 15, 'Growth': 8, 'Helicopter': 4, 'Hen': 50, 'Istanblue': 5, 'Jetpack': 4,
           "Joker's Jade": 10, 'Lakenvelder': 33, 'Lava': 10, 'Lilac': 10, 'Lizard': 0.88, 'Machete': 7,
           'Manic Mint': 10, 'Merah Red': 2, 'Moving Walkway': 2, 'Ocean': 9, 'Orange': "", 'Orange Will': 4,
           'Pink': 10,
           'Purple': 2, 'Purple Wine': 5, 'Red': 15, 'Ring': 0.77, 'Robot': '', 'Rollerblades': 8, 'Rooster': 50,
           'Rose': 2, 'Royal Procession': 0.55, 'Royal Violet': 2, 'Sad': 9, 'Sapphire': 5, 'Screamin Green': 10,
           'Serama': 6, 'Shocked': 9, 'Shocking Pink': 2, 'Sleepy': 9, 'Spicy': 100, 'Spring': 9, 'Stone': 10,
           'Striped Bald Chicken': '', 'Striped Eggshell': '', 'Striped English Mustard': '', 'Striped Istalblue': '',
           "Striped Joker's Jade": '', 'Striped Manic Mint': '', 'Striped Royal Violet': '',
           'Striped Screamin Green': '', 'Striped Shocking Pink': '', 'Striped Wild moss': '', 'Studs': '',
           'Sultan': 16,
           'Summer': 10, 'Teal': 0.27, 'Teleport': 7, 'Vampire': 0.86, 'White': "", 'Wild Moss': 3, 'Winter': 10,
           'Yellow': 31}
choices_egg = (
    'Not Dropped Yet', ':face_with_monocle: You think you are smarter than me. huh!',
    ':point_up: Its right there buddy',
    'Oops ! Got an egg instead')
choices_tip = (
    "You can get info of all chickens of somenone by typing.\n!owner <ADDRESS> ",
    "You can also use !t instead of !token.",
    "You can also use !o instead of !owner.",
    "We are always available to help you so clear your doubts in #questions channel.",
    "You can also use slash commands try now type \n/token",
    "The most valuable information can be found in pinned messages.",
    "Our first drop of 20000 chickens was sold within 10 minutes.",
    "While buying chickens from drop you dont have to pay gas fees . We take care of that.",
)


class Slash(Cog):
    def __init__(self, bot):

        self.bot = bot
        self.data = []
        self.warn_channels = []

    @tasks.loop(hours=4.0)
    async def printer(self):
        embed = Embed(colour=Colour.red(),
                      description="**ATTENTION**\nBe advised of scammers wanting to trade you. If you must trade, please message a mod to act as a middleman. Also keep an eye on anyone messaging you asking to trade, make sure their Discord ID's are authentic as there have been cases of impostors. Please stay safe")
        for ch in self.warn_channels:
            try:
                await ch.send(embed=embed)
                print(f"Send warning to {ch.name}")
            except AttributeError:
                raise ValueError("Channel not found", self.warn_channels)

    def cog_unload(self):
        print("Unloading")
        self.printer.cancel()

    @command(name="hi", aliases=["Hello", "Hi", "hello", "hola", "hey"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hi', 'Hiya', 'Hey', 'Hola', 'Hello', 'Yo'))} {ctx.author.mention}")

    @cog_slash(name="token", guild_ids=[632799582350475265,846537412058021888],
               description="Choose a token",
               options=[
                   create_option(
                       name="tokenid",
                       description="ID of the Token",
                       option_type=4,
                       required=True)])
    async def getslashtoken(self, ctx, tokenid: int):
        await self.gettoken(ctx, tokenid)

    @command(name="token", aliases=["t"], )
    async def gettoken(self, ctx, tokenid: int):
        if tokenid < 1 or tokenid > 20100:
            await ctx.send(":egg:")
            if isinstance(ctx, Context):
                await ctx.send(f"{choice(choices_egg)}")
            return
        data = await self.get_chicken_data(tokenid)
        embed = create_embed(data, tokenid)
        buttons2 = [create_button(style=ButtonStyle.URL, label="Opensea",
                                  url=f"https://opensea.io/assets/matic/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2/{tokenid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395"),
                    create_button(style=ButtonStyle.URL, label="Polygonscan",
                                  url=f"https://polygonscan.com/token/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2?a={tokenid}")]
        linkbuttons = create_actionrow(*buttons2)
        await ctx.send(embed=embed, components=[linkbuttons])

    @command(name="owner",aliases=["o"])
    async def owner_tokens(self, ctx, address):
        if len(address) != 42:
            raise ValueError("LenAddress", address)
        async with request(method="GET",
                           url=f"http://api.opensea.io/api/v2/assets/matic?asset_contract_address=0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2&owner={address}") as re:
            data = await re.json()
            if re.status != 200:
                raise ValueError("OpenseaApiError", address)
            if len(data["results"]) == 0:
                await ctx.send(f"Oops! Seems like {address} has no Chicken")
            tokens = process_owner(data["results"])
            chicken_data = await self.get_chicken_data(tokens[0])
            embed = create_embed(chicken_data, tokens[0])
            embed.set_author(name=f"1/{len(tokens)}")
            message_id = await ctx.send(embed=embed, components=[actionrow])
            owner[message_id.id] = tokens

    @cog_component()
    async def next(self, ctx: ComponentContext):
        await self.nextprev(ctx)

    @cog_component()
    async def prev(self, ctx: ComponentContext):
        await self.nextprev(ctx)
        await self.nextprev(ctx)

    @Cog.listener()
    async def on_ready(self):
        print("[+] Ready")
        for ids in warn_channel_ids:
            ch = self.bot.get_channel(ids)
            if ch is not None:
                self.warn_channels.append(self.bot.get_channel(ids))
            else:
                print(f"[!] Can't find {ids}")
        self.printer.start()

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
        await ctx.edit_origin(embed=embed, components=[actionrow])

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
                  url=f"https://opensea.io/assets/matic/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2/{tokenid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395")
    attributes = data["attributes"]
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
    embed.set_image(url=data["image_url"])

    return embed


def setup(bot):
    bot.add_cog(Slash(bot))
