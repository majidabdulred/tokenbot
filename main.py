import signal
from discord import Message, Intents
from discord_slash import SlashCommand
from lib.util.handle_errors import handle_errors
from discord.ext.commands import Bot as BotBase
from os import getenv
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lib.util.constants import PREFIX
from lib.mylogs.mylogger import getlogger
from lib.util import constants as C

mylogs = getlogger()

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.conn = 0
        self.scheduler = AsyncIOScheduler()
        self.leaderboard = {}
        self.message_board = None
        self.leader_raw = {401328409499664394: 570,
                           437808476106784770: 371,
                           235148962103951360: 194,
                           614109280508968980: 164,
                           704521096837464076: 139,
                           155149108183695360: 128,
                           294882584201003009: 124,
                           159985870458322944: 121,
                           716390085896962058: 119,
                           673918978178940951: 116,
                           458276816071950337: 111,
                           767971539567378432: 92,
                           617037497574359050: 56,
                           713026372142104687: 13}
        self.top30 = {}

        intents = Intents.all()
        super().__init__(command_prefix=PREFIX, intents=intents)

    def setup(self):
        # self.load_extension(f"lib.cogs.testcog")
        self.load_extension(f"lib.cogs.cog2")
        mylogs.info("Cog2 loaded.")
        self.load_extension(f"lib.cogs.cog3")
        self.load_extension(f"lib.cogs.cog1")
        mylogs.info("Cog3 loaded.")

    def run(self):
        mylogs.info("Running Setup")
        self.setup()

        self.TOKEN = getenv("DISCORD_TOKEN")
        super().run(self.TOKEN, reconnect=True)

    async def on_command_error(self, context, exc):
        await handle_errors(exc, context)

    async def on_slash_command_error(self, ctx, exc):
        await handle_errors(exc, ctx)

    async def on_component_callback_error(self, ctx, ex):
        await handle_errors(ex, ctx)

    async def on_message(self, message: Message):
        if message.author != self.user:
            ctx = await self.get_context(message)
            if ctx.valid:
                await self.invoke(ctx)

    async def on_ready(self):

        mylogs.info("Ready")
        self.data_channel = self.get_channel(868331067894013992)
        self.error_channel = self.get_channel(870636269603000360)
        if not self.ready:
            try:
                self.loop.add_signal_handler(getattr(signal, 'SIGINT'),
                                             lambda: self.loop.create_task(self.signal_handler()))
                self.loop.add_signal_handler(getattr(signal, 'SIGTERM'),
                                             lambda: self.loop.create_task(self.signal_handler()))
            except NotImplementedError:
                mylogs.warning("Signal handlers not added")
            self.ready = True

        else:
            mylogs.warning("Bot reconnecting....")

    async def signal_handler(self):
        mylogs.critical("Time to say good bye")
        await self.close()

    async def on_connect(self):
        mylogs.info("Bot Connected")

    async def on_disconnect(self):
        mylogs.warning("Bot Disconnected")


bot = Bot()
slash = SlashCommand(bot, sync_commands=True)
bot.run()
