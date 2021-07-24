from random import choice
from discord import Embed
from discord.ext.commands import Cog, command
from aiohttp import request

lc_cache = dict()
percen = {'Alien': 0.91, 'Amethyst': 10, 'Angry': 9, 'Anvil': 7, 'Autumn': 10, 'Bald Chicken': 13, 'Beauty': 9,
          'Black': 10, 'Black Hole': 0.51, 'Bloodshot': 9, 'Blue': 15, 'Blue Egg': 3, 'Blue Rooster': 7, 'Bulging': 9,
          'CK-47': 7, 'Candy': 2, 'Cherry Dusk': 0.54, 'Chicken': 24, 'Chickenapult': 8, 'Classic': 0.83, 'Cockeyed': 9,
          'Cold Snap': 2, 'Coober': 8, 'Crosseyed': 9, 'Determined': 9, 'Devolution': 2, 'Dig': 4, 'Dorking': 45,
          'Eggshell': 13, 'English Mustard': 13, 'Exhausted': 9, 'Eyepatch': 0.85, 'Fan Group': 4, 'Flesh': 9,
          'Flight?': 7, 'Gold': 31, 'Green': 15, 'Growth': 8, 'Helicopter': 4, 'Hen': 50, 'Istanblue': 5, 'Jetpack': 4,
          "Joker's Jade": 10, 'Lakenvelder': 33, 'Lava': 10, 'Lilac': 10, 'Lizard': 0.88, 'Machete': 7,
          'Manic Mint': 10, 'Merah Red': 2, 'Moving Walkway': 2, 'Ocean': 9, 'Orange': "", 'Orange Will': 4, 'Pink': 10,
          'Purple': 2, 'Purple Wine': 5, 'Red': 15, 'Ring': 0.77, 'Robot': '', 'Rollerblades': 8, 'Rooster': 50,
          'Rose': 2, 'Royal Procession': 0.55, 'Royal Violet': 2, 'Sad': 9, 'Sapphire': 5, 'Screamin Green': 10,
          'Serama': 6, 'Shocked': 9, 'Shocking Pink': 2, 'Sleepy': 9, 'Spicy': 100, 'Spring': 9, 'Stone': 10,
          'Striped Bald Chicken': '', 'Striped Eggshell': '', 'Striped English Mustard': '', 'Striped Istalblue': '',
          "Striped Joker's Jade": '', 'Striped Manic Mint': '', 'Striped Royal Violet': '',
          'Striped Screamin Green': '', 'Striped Shocking Pink': '', 'Striped Wild moss': '', 'Studs': '', 'Sultan': 16,
          'Summer': 10, 'Teal': 0.27, 'Teleport': 7, 'Vampire': 0.86, 'White': "", 'Wild Moss': 3, 'Winter': 10,
          'Yellow': 31}


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
    opensea = f"https://opensea.io/assets/matic/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2/{tid}?ref=0xc96b13e952e77d2f9accb33597c216d96ed91395"
    polygonscan = f"https://polygonscan.com/token/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2?a={tid}"
    embed = Embed(title=acc["name"],
                  description=f"**Opensea** = [Visit]({opensea})\n**Polygonscan** = [Visit]({polygonscan})")
    attributes = acc["attributes"]
    embed.set_author(name=f"Token {tid}")
    for att in attributes:
        if att["value"] is None:
            continue
        kttr = ""
        try:
            if percen[att['value']] == "":
                raise KeyError
            kttr = f" ({percen[att['value']]}%)"
        except:
            pass
        embed.add_field(name=att["trait_type"].capitalize(), value=f'{att["value"]}{kttr}')
    embed.set_image(url=acc["image_url"])
    return embed


def setup(bot):
    bot.add_cog(Slash(bot))
