# python3 fwew.py
# depends discord.py
import discord
import asyncio
import subprocess

# config
token = "placeDiscordTokenHere"
trigger = "!fwew"
bad_chars = "`~@#$%^&*(){}<>_/,.;:!?|+\\"
default_flags = ""  # "-i -ipa"
space = " "
dbl_quote = '"'
sngl_quote = "'"
md_codeblock = "```"

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
        prog = message.content[1:6]
        # remove all the sketchy chars from arguments
        nospec = message.content[6:]
        for c in bad_chars:
            nospec = nospec.replace(c, "")
        argv = nospec.split()
        # build argument string putting quotes only where necessary
        argstr = ""
        for arg in argv:
            if arg.startswith("-"):
                argstr += arg + space
            else:
                # only surround the word with quotes, if it contains single-quote
                if "'" in arg or "’" in arg:
                    argstr += dbl_quote + arg + dbl_quote + space
                else:
                    argstr += arg + space

        # don't try to look up just a quote character
        if argstr == "" or argstr == sngl_quote:
            pass
        else:
            print(prog + default_flags + space + argstr)
            response = subprocess.getoutput(prog + default_flags + space + argstr)
            em = discord.Embed(title=prog + default_flags + space + argstr, description=response, colour=0x607CA3)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            await client.send_message(message.channel, embed=em)

client.run(token)
