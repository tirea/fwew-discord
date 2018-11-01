# python3 fwew.py
# depends discord.py
import discord
import asyncio
import subprocess
from config import cfg as config

# config
name = config["name"]
prog = config["prog"]
token = config["token"]
space = config["space"]
ver_num = config["ver_num"]
ver_chn = config["ver_chn"]
ver_cod = config["ver_cod"]
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


def valid(query):
    # only get version is valid query
    if query == trigger + " -v":
        return True
    qs = query.split(" ")
    # first part of query must be trigger
    if qs[0] != trigger:
        return False
    # query must contain trigger and something to look up
    if len(qs) < 2:
        return False
    # make sure that after the flag args there is at least one word
    for q in qs[1:]:
        if not q.startswith("-"):
            return True
    return False


@client.event
async def on_message(message):
    send_pm = False
    # validate user's query
    if valid(message.content):
        # remove all the sketchy chars from arguments
        nospec = message.content[6:]  # len('!fwew ') == 6
        for c in bad_chars:
            nospec = nospec.replace(c, "")

        # convert quotes
        argv = nospec.split()
        for i in range(len(argv)):
            for qc in quote_chars:
                argv[i] = argv[i].replace(qc, "\"")
            for sqc in squote_chars:
                argv[i] = argv[i].replace(sqc, "'")

        # build argument string putting quotes only where necessary
        argstr = ""
        # automatically use German if in a German channel
        if message.channel.id == "398213699552411648": # #lerngruppe
            argstr += "-l=de" + space
        elif message.channel.id == "298701183898484737": # #deutsch
            argstr += "-l=de" + space
        # automatically use Dutch in the Dutch channel
        elif message.channel.id == "466721683496239105": # #nederlands
            argstr += "-l=nl" + space
        # automatically use Russian in the Russian channel
        elif message.channel.id == "507306946190114846": # #русский
            argstr += "-l=ru" + space
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
        if argstr == "" or argstr == sngl_quote or argstr == dbl_quote:
            pass
        else:
            # anonymous logging of entire actual system command to run in shell
            print(prog + space + default_flags + space + argstr)
            # run the fwew program from shell and capture stdout in response
            response = subprocess.getoutput(prog + space + default_flags + space + argstr)
            # prepare an array for splitting the message just in case
            response_fragments = []
            embeds = []
            char_limit = 2000
            if len(response) > char_limit:  # Discord Character limit is 2000
                send_pm = True
                fragment = ""
                char_count = 0
                response_lines = response.split('\n')
                for line in response_lines:
                    if char_count + len(line) + 1 <= char_limit:
                        fragment += line + '\n'
                        char_count += len(line) + 1
                    else:
                        response_fragments.append(fragment)
                        fragment = line + '\n'
                        char_count = len(line) + 1
                response_fragments.append(fragment)
            else:
                response_fragments.append(response)
            for r in response_fragments:
                em = discord.Embed(
                    title=argstr, description=r, colour=0x607CA3)
                em.set_author(name=message.author.display_name,
                              icon_url=message.author.avatar_url)
                if message.content.lower() == trigger + " -v":
                    em.description += "\n%s version %s-%s %s" % (
                        name, ver_num, ver_chn, ver_cod)
                # some hardcoded eastereggs
                elif message.content.lower() == "!fwew eywa":
                    em.set_image(
                        url="https://cdn.discordapp.com/attachments/154318499722952704/401596598624321536/image.png")
                elif message.content.lower() == "!fwew hrh":
                    em.description = "https://youtu.be/-AgnLH7Dw3w?t=4m14s"
                    em.description += "\n> What would LOL be?\n> It would have to do with the word herangham... maybe HRH"
                elif message.content.lower() == "!fwew tunayayo":
                    em.description = ""
                    em.set_image(
                        url="https://cdn.discordapp.com/avatars/277818358655877125/42371a0df717f9d079ba1ff7beaa8a93.png?")
                embeds.append(em)

            if send_pm:
                # sends PM if len(response) > char_limit
                for e in embeds:
                    await client.send_message(message.author, embed=e)
            else:
                for e in embeds:
                    await client.send_message(message.channel, embed=e)

client.run(token)
