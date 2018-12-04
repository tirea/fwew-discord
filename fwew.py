# python3 fwew.py
# depends discord.py
import discord
import subprocess
from config import cfg

# config
name = cfg["name"]
prog = cfg["prog"]
token = cfg["token"]
space = cfg["space"]
ver_num = cfg["ver_num"]
ver_chn = cfg["ver_chn"]
ver_cod = cfg["ver_cod"]
trigger = cfg["trigger"]
hrh_url = cfg["hrh_url"]
eywa_url = cfg["eywa_url"]
tuna_url = cfg["tuna_url"]
bad_chars = cfg["bad_chars"]
dbl_quote = cfg["dbl_quote"]
sngl_quote = cfg["sngl_quote"]
quote_chars = cfg["quote_chars"]
squote_chars = cfg["squote_chars"]
md_codeblock = cfg["md_codeblock"]
default_flags = cfg["default_flags"]

fwew = discord.Client()
# fwew = discord.ext.commands.Bot(command_prefix="!")
# @fwew.command(name='fwew')
# I've come to realize that fwew cannot use the discord bot commands convention because:
# after the trigger, it needs to use the rest of the user's message which has high variance
# I can't make a bot command for every possible input like this, so on_message is required in this case.


def valid(query):
    # only get version is valid query
    if query == trigger + " -v":
        return True
    # query cannot be just a quote character
    if query == sngl_quote or query == dbl_quote:
        return False
    qs = query.split(" ")
    # query must contain trigger and something to look up
    if len(qs) < 2:
        return False
    # first part of query must be trigger
    if qs[0] != trigger:
        return False
    # make sure that after the flag args there is at least one word
    for q in qs[1:]:
        if not q.startswith("-"):
            return True
    return False


@fwew.event
async def on_ready():
    print("Logged in as")
    print(fwew.user.name)
    print(fwew.user.id)
    print("------")


@fwew.event
async def on_message(message):
    send_pm = False
    # validate user's query
    if valid(message.content):
        tlen = len(trigger) + 1  # add one for space-character
        # remove all the sketchy chars from arguments
        nospec = message.content[tlen:]
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
        if message.channel.id == "398213699552411648":  # #lerngruppe
            argstr += "-l=de" + space
        elif message.channel.id == "298701183898484737":  # #deutsch
            argstr += "-l=de" + space
        # automatically use Dutch in the Dutch channel
        elif message.channel.id == "466721683496239105":  # #nederlands
            argstr += "-l=nl" + space
        # automatically use Russian in the Russian channel
        elif message.channel.id == "507306946190114846":  # #русский
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
            em = discord.Embed(title=argstr, description=r, colour=0x607CA3)
            em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            if message.content.lower() == trigger + " -v":
                em.description += "\n%s version %s-%s %s" % (
                    name, ver_num, ver_chn, ver_cod)
            # some hardcoded Easter eggs
            elif message.content.lower() == trigger + " eywa":
                em.set_image(url=eywa_url)
            elif message.content.lower() == trigger + " hrh":
                em.description = hrh_url
                em.description += "\n"
                em.description += "> What would LOL be?\n"
                em.description += "> It would have to do with the word herangham... maybe HRH"
            elif message.content.lower() == trigger + " tunayayo":
                em.description = ""
                em.set_image(url=tuna_url)
            embeds.append(em)

        if send_pm:
            # sends PM if len(response) > char_limit
            for e in embeds:
                await message.author.dm_channel.send(embed=e)
        else:
            for e in embeds:
                await message.channel.send(embed=e)

fwew.run(token)
