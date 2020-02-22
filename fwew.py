# python3 fwew.py
# depends discord.py
import discord
import subprocess
from config import cfg
from tokiponavi import lukin

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


def valid(query, dm):
    # query cannot be just a quote character
    if query == sngl_quote or query == dbl_quote:
        return False
    qs = query.split(" ")
    # query is in a Direct Message channel
    if dm:
        # only get version is valid query
        if query == "-v" or query == trigger + space + "-v":
            return True
        # query must contain something to look up
        if len(qs) < 1:
            return False
        # still putting the trigger should work
        if qs[0] == trigger:
            start = 1
        else:
            start = 0
    else:
        # only get version is valid query
        if query == trigger + space + "-v":
            return True
        # query must contain trigger and something to look up
        if len(qs) < 2:
            return False
        # first part of query must be trigger
        if qs[0] != trigger:
            return False
        start = 1
    # make sure that after the flag args there is at least one word
    for q in qs[start:]:
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
    # my own messages are not to be considered HRH
    if message.author == fwew.user:
        return False

    send_pm = False
    # validate user's query
    is_pm = isinstance(message.channel, discord.channel.DMChannel)
    if valid(message.content, is_pm):
        tlen = len(trigger) + 1  # add one for space-character
        # remove all the sketchy chars from arguments
        if is_pm:
            if message.content.startswith(trigger):
                nospec = message.content[tlen:]
            else:
                nospec = message.content[:]
        else:
            nospec = message.content[tlen:]
        for c in bad_chars:
            nospec = nospec.replace(c, "")
        # convert quotes
        for qc in quote_chars:
            nospec = nospec.replace(qc, "\"")
        for sqc in squote_chars:
            nospec = nospec.replace(sqc, "'")

        # add quotes around slash-command
        argv_arr = nospec.split(",")
        for i in range(len(argv_arr)):
            # but not if they're already there
            if (argv_arr[i].startswith('/"') or argv_arr[i].startswith('"/')) and argv_arr[i].endswith('"'):
                pass
            else:
                if argv_arr[i].startswith("/"):
                    argv_arr[i] = '"' + argv_arr[i] + '"'
                elif argv_arr[i].startswith(" /"):
                    argv_arr[i] = space + '"' + argv_arr[i][1:] + '"'
        nospec = ','.join(argv_arr)

        # build argument string putting quotes only where necessary
        argstr = ""

        # international channel default language flags
        # automatically use German if in a German channel
        if message.channel.id == 398213699552411648:  # #lerngruppe
            argstr += "-l=de" + space
        elif message.channel.id == 298701183898484737:  # #deutsch
            argstr += "-l=de" + space
        # automatically use Dutch in the Dutch channel
        elif message.channel.id == 466721683496239105:  # #nederlands
            argstr += "-l=nl" + space
        # automatically use Polish in the Polish channel
        elif message.channel.id == 649363324143665192:  # #polski
            argstr += "-l=pl" + space
        # automatically use Russian in the Russian channel
        elif message.channel.id == 507306946190114846:  # #русский
            argstr += "-l=ru" + space
        elif message.channel.id == 365987412163297284:  # #français
            argstr += "-l=fr" + space
        # custom defaults
        elif message.channel.id == 652214951225589760:  # #???
            argstr += "-i -s" + space

        # arguments
        argv = nospec.split()
        for arg in argv:
            if arg.startswith("-"):
                argstr += arg + space
            else:
                # only surround the word with quotes, if it contains single-quote
                if ("'" in arg) and ('"' not in arg):
                    argstr += dbl_quote + arg + dbl_quote + space
                else:
                    argstr += arg + space

        # anonymous logging of entire actual system command to run in shell
        print(prog + space + default_flags + space + argstr)

        # run the fwew program from shell and capture stdout in response
        response = subprocess.getoutput(
            prog + space + default_flags + space + argstr)

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

        title_limit = 256
        for r in response_fragments:
            if len(argstr) > title_limit:
                argstr = argstr[:title_limit] + "..."
            em = discord.Embed(title=argstr, description=r, colour=0x607CA3)
            em.set_author(name=message.author.display_name,
                          icon_url=message.author.avatar_url)
            if message.content.lower() == trigger + " -v":
                em.description += "\n%s version %s-%s %s" % (
                    name, ver_num, ver_chn, ver_cod)
            elif is_pm and message.content.lower() == "-v":
                em.description += "\n%s version %s-%s %s" % (
                    name, ver_num, ver_chn, ver_cod)
            # some hardcoded Easter eggs
            elif message.content.lower() == trigger + space + "eywa":
                em.set_image(url=eywa_url)
            elif message.content.lower() == trigger + space + "hrh":
                em.description = hrh_url
                em.description += "\n"
                em.description += "> What would LOL be?\n"
                em.description += "> It would have to do with the word herangham... maybe HRH"
            elif message.content.lower() == trigger + space + "tunayayo":
                em.description = ""
                em.set_image(url=tuna_url)
            elif message.content.lower().startswith(trigger + space + "-lmftfy"):
                lmftfy_cmd = message.content.lower().split(' ')
                if len(lmftfy_cmd) >= 3:
                    lmftfy_args = lmftfy_cmd[1:]
                    # recipient = lmftfy_args[0]
                    lmftfy_query = trigger + space + \
                        space.join(lmftfy_args[1:])
                    lmftfy_op = subprocess.getoutput(
                        prog + space + default_flags + space + space.join(lmftfy_args[1:]))
                    em.title = "Let me fwew that for you..."
                    # em.set_author(name=recipient, icon_url="")
                    # em.description = "Let me fwew that for you..."
                    # em.description += "\n\n"
                    em.description += lmftfy_query
                    em.description += "\n\n"
                    em.description += lmftfy_op[0:char_limit]
            elif len(argv) > 1 and argv[0] == "-tp":
                em.description = lukin(argv)
            embeds.append(em)

        if send_pm:
            # sends PM if len(response) > char_limit
            for e in embeds:
                if message.author.dm_channel is None:
                    await message.author.create_dm()
                await message.author.dm_channel.send(embed=e)
        else:
            for e in embeds:
                await message.channel.send(embed=e)

fwew.run(token)
