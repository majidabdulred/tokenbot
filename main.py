import signal
from discord import Message
from discord_slash import SlashCommand
from lib.handle_errors import handle_errors
from discord.ext.commands import Bot as BotBase
from os import getenv
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lib.constants import PREFIX

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.conn = 0
        self.scheduler = AsyncIOScheduler()

        super().__init__(command_prefix=PREFIX)

    def setup(self):
        # self.load_extension(f"lib.cogs.testcog")
        self.load_extension(f"lib.cogs.cog2")
        print("[+] Cog2 loaded.")
        self.load_extension(f"lib.cogs.cog3")
        print("[+] Cog3 loaded.")

    def run(self):
        print("[+] Running setup")
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
        print("[+] Ready")
        self.data_channel = self.get_channel(868331067894013992)
        self.error_channel = self.get_channel(870636269603000360)
        if not self.ready:
            try:
                self.loop.add_signal_handler(getattr(signal, 'SIGINT'),
                                             lambda: self.loop.create_task(self.signal_handler()))
                self.loop.add_signal_handler(getattr(signal, 'SIGTERM'),
                                             lambda: self.loop.create_task(self.signal_handler()))
            except NotImplementedError:
                print("[!] Signal handlers not added")
            self.ready = True

        else:
            print("Bot reconnecting....")

    async def signal_handler(self):
        print("Time to say good bye")
        await self.close()

    async def on_connect(self):
        print("[+] Bot Connected")

    async def on_disconnect(self):
        print("[!] Bot Disconnected")


bot = Bot()
slash = SlashCommand(bot, sync_commands=True)
bot.run()
