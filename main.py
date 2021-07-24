from discord import Message
from lib.handle_errors import handle_errors
from discord.ext.commands import Bot as BotBase
from os import getenv
from dotenv import load_dotenv

load_dotenv()
PREFIX = "!"
TOKEN = getenv("DISCORD_TOKEN")


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.conn = 0

        super().__init__(command_prefix=PREFIX)

    def setup(self):
        self.load_extension(f"lib.cogs.cog2")

    def run(self):
        print("[+] Running setup")
        self.setup()

        self.TOKEN = getenv("DISCORD_TOKEN")
        super().run(self.TOKEN, reconnect=True)

    async def on_command_error(self, context, exc):
        print("[!] Error occured")
        await handle_errors(exc, context)

    async def on_message(self, message: Message):
        print(message.content)
        if message.author != self.user:
            await self.process_commands(message)

    async def on_connect(self):
        print("[+] Bot Connected")

    async def on_disconnect(self):
        print("[!] Bot Disconnected")


bot = Bot()
bot.run()
