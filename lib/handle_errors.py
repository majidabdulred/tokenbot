from discord.errors import HTTPException, Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, BadBoolArgument
from pandas.core.indexing import IndexingError
from discord_slash.error import IncorrectFormat
"pymongo.errors.DuplicateKeyError: E11000 duplicate key error collection: chick.users index: _id_ dup key: { _id: 1001 }, full error: {'index': 0, 'code': 11000, 'keyPattern': {'_id': 1}, 'keyValue': {'_id': 1001}, 'errmsg': 'E11000 duplicate key error collection: chick.users index: _id_ dup key: { _id: 1001 }'}"


async def handle_errors(exc, ctx):
    print(f"[!] {ctx.author.name} {exc}")
    if hasattr(exc, "original"):
        Error = exc.original
    else:
        Error = exc
    if any([isinstance(Error, error) for error in (MissingRequiredArgument, BadBoolArgument, BadArgument)]):
        await ctx.send("Command not used properly.")

    elif any([isinstance(Error, error) for error in (CommandNotFound, HTTPException, AttributeError)]):
        pass
    elif isinstance(Error, Forbidden):
        await ctx.send("Don't have permissions")
    elif isinstance(Error, ValueError):
        if Error.args[0] == "OpenseaApiError":
            await ctx.send("Wrong Address")
        elif Error.args[0] == "LenAddress":
            await ctx.send("Wrong address")
    elif isinstance(Error, IndexingError):
        await ctx.send("Please see pinned messages on how to use this command.")
    elif isinstance(Error, IncorrectFormat):
        pass
    else:
        raise Error
