import re

import logging
logger = logging.getLogger(__name__)

def format_incomming(message, chat_widget):
    text = message.content
    newtxt = []
    for m in re.split("(<(?:@|@!|#|@&)[0-9]+>)", text):
        match = re.match("<(@|@!|#|@&)([0-9]+)>", m)
        if match:
            typ = match.group(1)
            snflk = match.group(2)
            if typ == "@":
                logger.debug("Mention (User) found")
                member = next((memb for memb in message.mentions if memb.id == snflk), None)
                if member:
                    if member.id == chat_widget.discord.user.id:
                        newtxt.append(("message_mention_self", "@"+member.name))
                    else:
                        newtxt.append(("message_mention", "@"+member.name))
                    continue
            elif typ == "@!":
                logger.debug("Mention (Nickname) found")
                member = next((memb for memb in message.mentions if memb.id == snflk), None)
                if member:
                    if member.id == chat_widget.discord.user.id:
                        newtxt.append(("message_mention_self", "@"+member.display_name))
                    else:
                        newtxt.append(("message_mention", "@"+member.display_name))
                    continue
            elif typ == "#":
                logger.debug("Mention (Channel) found")
                channel = next((chan for chan in message.channel_mentions if chan.id == snflk), None)
                if channel:
                    newtxt.append(("message_mention", "#"+channel.name))
                    continue
            elif typ == "@&":
                logger.debug("Mention (Role) found")
                role = next((role for role in message.role_mentions if role.id == snflk), None)
                if role:
                    newtxt.append(("message_mention", "@"+role.name))
                    continue
        newtxt.append(m)
    #logger.debug("Processed: " + str(newtxt))
    return newtxt


def format_outgoing(text):
    return text


def shorten_channel_names(channels, length):
    if len(channels) == 0:
        return {}
    same_server = True
    server = channels[0].server
    result = {}
    for ch in channels:
        if not ch.server.id == server.id:
            same_server = False
            break
    if same_server:
        for ch in channels:
            if len(ch.name) <= length:
                result[ch] = ch.name
            else:
                exceeds = len(ch.name.replace("-", "").replace("_", "")) - length
                words = re.split("[-_]", ch.name)
                chars_per_word = exceeds // len(words)
                ch_name = []
                exceeds2 = 0
                for word in words:
                    if len(word) > chars_per_word + 1:
                        ch_name.append(word[:-(chars_per_word+1)])
                    else:
                        exceeds2 += len(word)
                result[ch] = str.join("-", ch_name)
    else:
        for ch in channels:
            result[ch] = "{0}#{1}".format(ch.server.name, ch.name)
    return result
