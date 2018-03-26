# python3 fwew.py
# depends discord.py
import discord
import asyncio
import subprocess
from config import cfg as config

# config
token = config["token"]
space = config["space"]
trigger = config["trigger"]
bad_chars = config["bad_chars"]
dbl_quote = config["dbl_quote"]
sngl_quote = config["sngl_quote"]
quote_chars = config["quote_chars"]
squote_chars = config["squote_chars"]
md_codeblock = config["md_codeblock"]
default_flags = config["default_flags"]

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


@client.event
async def on_message(message):
    # seen the trigger word. also don't allow interactive mode
    if message.content.startswith(trigger) and message.content != trigger:
        # "fwew"
        prog = message.content[1:5]
        # remove all the sketchy chars from arguments
        nospec = message.content[6:]
        for c in bad_chars:
            nospec = nospec.replace(c, "")
        argv = nospec.split()
        # convert quotes
        for i in range(len(argv)):
            for qc in quote_chars:
                argv[i] = argv[i].replace(qc, "\"")
            for sqc in squote_chars:
                argv[i] = argv[i].replace(sqc, "'")
        # build argument string putting quotes only where necessary
        argstr = ""
        for arg in argv:
            if arg.startswith("-"):
                argstr += arg + space
            else:
                # only surround the word with quotes, if it contains single-quote
                if ("'" in arg) and '"' not in arg:
                    argstr += dbl_quote + arg + dbl_quote + space
                else:
                    argstr += arg + space

        # don't try to look up just a quote character
        if argstr == "" or argstr == sngl_quote:
            pass
        else:
            print(prog + space + default_flags + space + argstr)
            response = subprocess.getoutput(prog + space + default_flags + space + argstr)
            em = discord.Embed(title=argstr, description=response, colour=0x607CA3)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            if message.content == "!fwew Eywa" or message.content == "!fwew eywa":
                em.set_image(url="https://cdn.discordapp.com/attachments/154318499722952704/401596598624321536/image.png")
            if message.content == "!fwew TunaYayo":
                em.description = ""
                em.set_image(url="https://cdn.discordapp.com/avatars/277818358655877125/42371a0df717f9d079ba1ff7beaa8a93.png?")
            await client.send_message(message.channel, embed=em)

client.run(token)
