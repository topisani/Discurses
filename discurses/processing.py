import re
from typing import Dict, List

import discord

import logging
logger = logging.getLogger(__name__)

def format_incomming(text: str) -> str:
    return text


def format_outgoing(text: str) -> str:
    return text


def shorten_channel_names(channels: List[discord.Channel], length) -> Dict[discord.Channel, str]:
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
