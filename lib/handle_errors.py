from discord.errors import HTTPException, Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, BadBoolArgument


async def handle_errors(exc, ctx):
    print(f"[!] {exc}")
    if any([isinstance(exc, error) for error in (MissingRequiredArgument,  BadBoolArgument,BadArgument)]):
        await ctx.send("Command not used properly.")

    elif isinstance(exc, CommandNotFound):
        print("Command not found")
        pass

    elif isinstance(exc.original, HTTPException):
        await ctx.send("Wrong Address")

    elif isinstance(exc.original, Forbidden):
        await ctx.send("Don't have permissions")

    elif hasattr(exc, "original"):
        raise exc.original

    else:
        raise exc
