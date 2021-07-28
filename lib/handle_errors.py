from discord.errors import HTTPException, Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, BadBoolArgument


async def handle_errors(exc, ctx):
    print(f"[!] {exc}")
    if any([isinstance(exc, error) for error in (MissingRequiredArgument, BadBoolArgument, BadArgument)]):
        await ctx.send("Command not used properly.")

    elif isinstance(exc, CommandNotFound):
        pass

    elif isinstance(exc.original, HTTPException):
        await ctx.send("Wrong Address")

    elif isinstance(exc.original, Forbidden):
        await ctx.send("Don't have permissions")
    elif isinstance(exc.original, ValueError):
        if exc.original.args[0] == "OpenseaApiError":
            await ctx.send("Wrong Address")
        elif exc.original.args[0] == "LenAddress":
            await ctx.send("Wrong address")
    elif hasattr(exc, "original"):
        raise exc.original


    else:
        raise exc
