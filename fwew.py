# python3 fwew.py
# depends discord.py
import discord
import asyncio
import subprocess

# config
token = "placeDiscordTokenHere"
trigger = "!fwew"
bad_chars = "`~@#$%^&*()[]{}<>_/,;:!?|+\"\\"
default_flags = "-i -ipa"
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
    print("------)


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
                argstr += dbl_quote + arg + dbl_quote + space
        # don't try to look up just a quote character
        if argstr == "" or argstr == sngl_quote:
            pass
        else:
            response = md_codeblock
            response += subprocess.getoutput(prog + default_flags + space + argstr)
            response += md_codeblock
            await client.send_message(message.channel, response)

client.run(token)
