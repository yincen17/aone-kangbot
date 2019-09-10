# flake8: noqa: I didnt finish coding it lol

from .util import get_cmd_name, MarkdownBotPassthrough
from .. import loader

from functools import wraps
from inspect import signature, Parameter

import logging
import telethon
import sys
import re
import datetime
import tempfile
import asyncio

logger = logging.getLogger(__name__)

class UniborgClient:
    instance_count = 0

    class __UniborgShimMod__Base(loader.Module):
        def __init__(self, borg):
            self._borg = borg
            self.commands = borg._commands
            print(self.commands)
            self.name = "UniborgShim__" + borg._module

        async def watcher(self, message):
            for w in self._borg._watchers:
                w(message)
    def registerfunc(self, cb):
        cb(type("__UniborgShimMod__" + self._module, (self.__UniborgShimMod__Base,), dict())(self))

    def __init__(self):
        self.instance_count += 1
        self.instance_id = self.instance_count
        self._storage = None  # TODO
        self._commands = {}
        self._watchers = []
        self._unknowns = []
        self._wrapper = None  # Set in registerfunc

    def _ensure_unknowns(self):
        self._commands["borgcmd" + str(self.instance_id)] = self._unknown_command

    def _unknown_command(self, message):
        message.message = "." + message.message[len("borgcmd" + str(self.instance_id)) + 1:]
        return asyncio.gather(*[uk(message, "") for uk in self._unknowns])

    def on(self, event):
        def subreg(func):
            logger.debug(event)
            sig = signature(func)
            newsig = sig.replace(parameters=list(sig.parameters.values()) + [Parameter("borg", Parameter.KEYWORD_ONLY),
                                                                     Parameter("logger", Parameter.KEYWORD_ONLY),
                                                                     Parameter("storage", Parameter.KEYWORD_ONLY)])
            logger.debug(newsig)
            func.__signature__ = newsig
            logger.debug(signature(func))
            self._module = func.__module__

            sys.modules[self._module].__dict__["register"] = self.registerfunc

            if event.outgoing:
                # Command based thing
                if not event.pattern:
                    self._ensure_unknowns()
                    use_unknown = True
                cmd = get_cmd_name(event.pattern.__self__.pattern)
                if not cmd:
                    self._ensure_unknowns()
                    use_unknown = True

                @wraps(func)
                def commandhandler(message, pre="."):
                    """Closure to execute command when handler activated and regex matched"""
                    logger.debug("Command triggered")
                    match = re.match(event.pattern.__self__.pattern, pre + message.message, re.I)
                    if match:
                        logger.debug("and matched")
                        message.message = pre + message.message  # Framework strips prefix, give them a generic one
                        event2 = MarkdownBotPassthrough(message)
                        # Try to emulate the expected format for an event
                        event2.text = list(str(message.message))
                        event2.pattern_match = match
                        event2.message = MarkdownBotPassthrough(message)
                        # Put it off as long as possible so event handlers register
                        sys.modules[self._module].__dict__["borg"] = self._wrapper._client

                        return func(event2)
                        # Return a coroutine
                    else:
                        logger.debug("but not matched cmd " + message.message
                                     + " regex " + event.pattern.__self__.pattern)
                if use_unknown:
                    self._unknowns += [commandhandler]
                else:
                    self._commands[cmd] = commandhandler
            elif event.incoming:
                @wraps(func)
                def watcherhandler(message):
                    """Closure to execute watcher when handler activated and regex matched"""
                    match = re.match(message.message, kwargs.get("pattern", ".*"), re.I)
                    if match:
                        event = message
                        # Try to emulate the expected format for an event
                        event = MarkdownBotPassthrough(message)
                        # Try to emulate the expected format for an event
                        event.text = list(str(message.message))
                        event.pattern_match = match
                        event.message = MarkdownBotPassthrough(message)
                        return func(event)  # Return a coroutine
                self._watchers += [subwatcher]  # Add to list of watchers so we can call later.
            else:
                logger.error("event not incoming or outgoing")
                return func
            return func
        return subreg


class Uniborg:
    def __init__(self, clients):
        self.__all__ = "util"

class UniborgUtil:
    def __init__(self, clients):
        pass

    def admin_cmd(self, **kwargs):
        """Uniborg uses this for sudo users but we don't have that concept."""
        return telethon.events.NewMessage(**kwargs)
