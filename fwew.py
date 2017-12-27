# python3 fwew.py
# depends discord.py
import discord
import asyncio
import subprocess

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    # seen the trigger word. also don't allow interactive mode
    if message.content.startswith('!fwew') and message.content != "!fwew":
        # "fwew"
        prog = message.content[1:6]
        # remove all the sketchy chars from arguments
        nospec = message.content[6:]
        for c in "`~@#$%^&*()[]{}<>_/,;:!?|+\"\\":
            nospec = nospec.replace(c, '')
        argv = nospec.split()
        # build argument string putting quotes only where necessary
        argstr = ""
        for arg in argv:
            if arg.startswith('-'):
                argstr += arg + ' '
            else:
                argstr += '"' + arg + '"' + ' '
        # don't try to look up just a quote character
        if argstr == "" or argstr == "'":
            pass
        else:
            response = '```'
            response += subprocess.getoutput(prog + '-i -ipa ' + argstr)
            response += '```'
            await client.send_message(message.channel, response)

client.run('token')
