# python3 fwew.py
# depends discord.py
import discord
import subprocess
from datetime import datetime
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
logfile = cfg["logfile"]
eywa_url = cfg["eywa_url"]
tuna_url = cfg["tuna_url"]
bad_chars = cfg["bad_chars"]
queryfile = cfg["queryfile"]
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


def has_words(args):
    arglist = args.split()
    if len(arglist) == 0:
        return False
    # precondition: list is not empty.
    if arglist[-1].startswith("-") and arglist[-1] != "-h":
        return False
    # precondition: list is not empty and last item doesn't start with "-"
    if len(arglist) == 1:
        return True
    # precondition: list size > 1 and last item doesn't start with "-"
    if arglist[-2] in ["-p", "-l"]:
        return False
    # preconditions:
    # list size > 1
    # last item doesn't start with "-"
    # second-to-last item isn't -p or -l
    return True


def valid(query, dm):
    # query cannot be just a quote character
    if query == sngl_quote or query == dbl_quote:
        return False
    qs = query.split(" ")
    # do not allow config or debug
    if "-c" in qs or "-d" in qs:
        return False
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
    if has_words(query):
        return True
    return False


def cleanup(query):
    # remove all the sketchy chars from arguments
    nospec = query
    for c in bad_chars:
        nospec = nospec.replace(c, "")
    # convert quotes
    for qc in quote_chars:
        nospec = nospec.replace(qc, "\"")
    for sqc in squote_chars:
        nospec = nospec.replace(sqc, "'")
    return nospec


def add_quotes(query):
    # add quotes around slash-command
    argv_arr = query.split(",")
    for i in range(len(argv_arr)):
        # but not if they're already there
        if ('/"' in argv_arr[i] or '"/' in argv_arr[i]) and argv_arr[i].endswith('"'):
            pass
        else:
            if "/" in argv_arr[i]:
                argv_arr[i] = argv_arr[i].replace('/', '"/') + '"'
            elif argv_arr[i].startswith(" /"):
                argv_arr[i] = space + argv_arr[i][1:].replace('/', '"/') + '"'
    return ','.join(argv_arr)


def localize(chan_id):
    id_map = {
    "#lerngruppe": 398213699552411648,
    "#deutsch": 298701183898484737,
    "#nederlands": 466721683496239105,
    "#polski": 649363324143665192,
    "#русский": 507306946190114846,
    "#français": 365987412163297284,
    "#custom_0": 652214951225589760}
    s = ""
    # international channel default language flags
    if chan_id == id_map["#lerngruppe"]:
        s += "-l=de" + space
    elif chan_id == id_map["#deutsch"]:
        s += "-l=de" + space
    elif chan_id == id_map["#nederlands"]:
        s += "-l=nl" + space
    elif chan_id == id_map["#polski"]:
        s += "-l=pl" + space
    elif chan_id == id_map["#русский"]:
        s += "-l=ru" + space
    elif chan_id == id_map["#français"]:
        s += "-l=fr" + space
    # custom defaults
    elif chan_id == id_map["#custom_0"]:
        s += "-i -s" + space
    return s


@fwew.event
async def on_ready():
    with open(logfile, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        log.write(timestamp)
        log.write(" | ")
        log.write("login: ")
        log.write(fwew.user.name)
        log.write(space)
        log.write(str(fwew.user.id))
        log.write("\n")


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
        nospec = cleanup(nospec)

        # add quotes around slash-command
        nospec = add_quotes(nospec)

        # build argument string putting quotes only where necessary
        # localize based on current channel
        argstr = localize(message.channel.id)

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

        # 2>&1 redirects stderr to stdout so that fwew -h output is captured
        command = prog + space + default_flags + space + argstr + "2>&1"

        # anonymous logging of entire actual system command to run in shell
        with open(queryfile, "a") as qf:
            qf.write(command + "\n")

        # prevent go-prompt interactive hijacking / freezing
        if len(argstr) != 0:
            # run the fwew program from shell and capture stdout in response
            response = subprocess.getoutput(command)
        else:
            response = "no results"

        # prepare an array for splitting the message just in case
        response_fragments = []
        embeds = []
        char_limit = 2000
        # Discord Character limit is 2000
        if len(response) > char_limit:
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
                argstr = argstr[:title_limit-3] + "..."
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
                # WHO'S EYWA?!
                em.set_image(url=eywa_url)
            elif message.content.lower() == trigger + space + "hrh":
                # KP "HRH" video
                em.description = hrh_url
                em.description += "\n"
                em.description += "> What would LOL be?\n"
                em.description += "> It would have to do with the word herangham... maybe HRH"
            elif message.content.lower() == trigger + space + "tunayayo":
                # TunaYayo pfp
                em.description = ""
                em.set_image(url=tuna_url)
            elif message.content.lower().startswith(trigger + space + "-lmftfy"):
                # Let me Fwew that for you...
                lmftfy_cmd = message.content.lower().split(' ')
                if len(lmftfy_cmd) >= 3:
                    lmftfy_args = lmftfy_cmd[2:]
                    recipient = lmftfy_args[0]
                    lmftfy_query = trigger + space + space.join(lmftfy_args[1:])
                    fwew_query = prog + space + default_flags + space + space.join(lmftfy_args[1:])
                    lmftfy_op = subprocess.getoutput(fwew_query)
                    em.title = "Let me fwew that for you..."
                    em.set_author(name=recipient, icon_url="")
                    em.description = ""
                    em.description += "\n\n"
                    em.description += lmftfy_query
                    em.description += "\n\n"
                    em.description += lmftfy_op[0:char_limit]
            elif len(argv) > 1 and argv[0] == "-tp":
                # Toki Pona -> Nävis Translator
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
