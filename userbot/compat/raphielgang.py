from .. import loader

from .util import get_cmd_name, MarkdownBotPassthrough

import logging
import re
import sys
import asyncio

from functools import wraps


logger = logging.getLogger(__name__)


class RaphielgangConfig():
    def __init__(self, clients):
        self.__all__ = ["bot", "API_KEY", "API_HASH", "CONSOLE_LOGGER_VERBOSE", "LOGS", "BOTLOG_CHATID",
                        "BOTLOG", "PM_AUTO_BAN", "DB_URI", "OCR_SPACE_API_KEY", "REM_BG_API_KEY", "CHROME_DRIVER",
                        "GOOGLE_CHROME_BIN", "OPEN_WEATHER_MAP_APPID", "ANTI_SPAMBOT", "ANTI_SPAMBOT_SHOUT",
                        "YOUTUBE_API_KEY", "CLEAN_WELCOME", "BIO_PREFIX", "DEFAULT_BIO", "LASTFM_API",
                        "LASTFM_SECRET", "LASTFM_USERNAME", "LASTFM_PASSWORD_PLAIN", "LASTFM_PASS", "lastfm",
                        "G_DRIVE_CLIENT_ID", "G_DRIVE_CLIENT_SECRET", "G_DRIVE_AUTH_TOKEN_DATA", "GDRIVE_FOLDER_ID",
                        "TEMP_DOWNLOAD_DIRECTORY", "COUNT_MSG", "USERS", "COUNT_PM", "LASTMSG", "ENABLE_KILLME",
                        "CMD_HELP"]

        self.bots = clients

        # Static 'cos I cba
        self.API_KEY = 12345
        self.API_HASH = "0123456789abcdef0123456789abcdef"
        self.CONSOLE_LOGGER_VERBOSE = False
        self.LOGS = logging.getLogger("raphielgang-compat")
        self.BOTLOG_CHATID = 0
        self.BOTLOG = False
        self.PM_AUTO_BAN = False
        self.DB_URI = None
        self.OCR_SPACE_API_KEY = None
        self.REM_BG_API_KEY = None
        self.CHROME_DRIVER = None
        self.GOOGLE_CHROME_BIN = None
        self.OPEN_WEATHER_MAP_APPID = None
        self.ANTI_SPAMBOT = False
        self.ANTI_SPAMBOT_SHOUT = False
        self.YOUTUBE_API_KEY = None
        self.CLEAN_WELCOME = None
        self.BIO_PREFIX = None
        self.DEFAULT_BIO = None
        self.LASTFM_API = None
        self.LASTFM_SECRET = None
        self.LASTFM_USERNAME = None
        self.LASTFM_PASSWORD_PLAIN = None
        self.LASTFM_PASS = None
        self.lastfm = None
        self.G_DRIVE_CLIENT_ID = None
        self.G_DRIVE_CLIENT_SECRET = None
        self.G_DRIVE_AUTH_TOKEN_DATA = None
        self.GDRIVE_FOLDER_ID = None
        self.TEMP_DOWNLOAD_DIRECTORY = "./downloads"
        self.COUNT_MSG = 0
        self.USERS = {}
        self.COUNT_PM = {}
        self.LASTMSG = {}
        self.ENABLE_KILLME = False
        self.CMD_HELP = {}
        self.AFKREASON = "no reason"
        self.ZALG_LIST = [[
            "̖",
            " ̗",
            " ̘",
            " ̙",
            " ̜",
            " ̝",
            " ̞",
            " ̟",
            " ̠",
            " ̤",
            " ̥",
            " ̦",
            " ̩",
            " ̪",
            " ̫",
            " ̬",
            " ̭",
            " ̮",
            " ̯",
            " ̰",
            " ̱",
            " ̲",
            " ̳",
            " ̹",
            " ̺",
            " ̻",
            " ̼",
            " ͅ",
            " ͇",
            " ͈",
            " ͉",
            " ͍",
            " ͎",
            " ͓",
            " ͔",
            " ͕",
            " ͖",
            " ͙",
            " ͚",
            " ",
        ], [
            " ̍",
            " ̎",
            " ̄",
            " ̅",
            " ̿",
            " ̑",
            " ̆",
            " ̐",
            " ͒",
            " ͗",
            " ͑",
            " ̇",
            " ̈",
            " ̊",
            " ͂",
            " ̓",
            " ̈́",
            " ͊",
            " ͋",
            " ͌",
            " ̃",
            " ̂",
            " ̌",
            " ͐",
            " ́",
            " ̋",
            " ̏",
            " ̽",
            " ̉",
            " ͣ",
            " ͤ",
            " ͥ",
            " ͦ",
            " ͧ",
            " ͨ",
            " ͩ",
            " ͪ",
            " ͫ",
            " ͬ",
            " ͭ",
            " ͮ",
            " ͯ",
            " ̾",
            " ͛",
            " ͆",
            " ̚",
        ], [
            " ̕",
            " ̛",
            " ̀",
            " ́",
            " ͘",
            " ̡",
            " ̢",
            " ̧",
            " ̨",
            " ̴",
            " ̵",
            " ̶",
            " ͜",
            " ͝",
            " ͞",
            " ͟",
            " ͠",
            " ͢",
            " ̸",
            " ̷",
            " ͡",
        ]]

    @property
    def bot(self):
        return self.bots[0]  # TODO return the right one

    async def client_ready(self, client):
        self.bots += [MarkdownBotPassthrough(client)]

# The core machinery will fail to identify any register() function in the module.
# So we need to introspect the module and add register(), and a shimmed class to store state

# Please don't refactor this class. Even while writing it only God knew how it worked.


__hours_wasted_here = 4


# // don't touch
class RaphielgangEvents():
    def __init__(self, clients):
        self.instances = {}

    class RaphielgangEventsSub():
        class __RaphielgangShimMod__Base(loader.Modules):
            def __init__(self, events_instance):
                self._events = events_instance
                self.commands = events_instance._commands
                self.name = type(self).__name__
                self.unknowns = events_instance._unknowns

            async def watcher(self, message):
                for watcher in self._events._watchers:
                    watcher(message)

        def __init__(self):
            self._module = None
            self._setup_complete = False
            self._watchers = []
            self._commands = {}
            self._unknowns = []

        def _ensure_unknowns(self):
            self.commands["raphcmd" + str(self.instance_id)] = self._unknown_command

        def _unknown_command(self, message):
            message.message = message.message[len("raphcmd" + str(self.instance_id)) + 1:]
            return asyncio.gather(*[uk(message, "") for uk in self._unknowns])

        def register(self, *args, **kwargs):
            if len(args) >= 1:
                # This is the register() function in normal ftg modules
                # Create a fake type, instantiate it with our own self
                args[0](type("__RaphielgangShimMod__" + self._module, (self.__RaphielgangShimMod__Base,), dict())(self))
                return

            def subreg(func):  # ALWAYS return func.
                logger.debug(kwargs)
                sys.modules[func.__module__].__dict__["registration"] = self.register
                if not self._setup_complete:
                    self._module = func.__module__
                    self._setup_complete = True
                if kwargs.get("outgoing", False):
                    # Command-based thing
                    use_unknown = False
                    if "pattern" not in kwargs.keys():
                        self._ensure_unknowns()
                        use_unknown = True
                    cmd = get_cmd_name(kwargs["pattern"])
                    if not cmd:
                        self._ensure_unknowns()
                        use_unknown = True

                    @wraps(func)
                    def commandhandler(message, pre="."):
                        """Closure to execute command when handler activated and regex matched"""
                        logger.debug("Command triggered")
                        # Framework strips prefix, give them a generic one
                        message.message = pre + message.message
                        match = re.match(kwargs["pattern"], message.message, re.I)
                        if match:
                            logger.debug("and matched")
                            event = MarkdownBotPassthrough(message)
                            # Try to emulate the expected format for an event
                            event.text = list(str(message.message))
                            event.pattern_match = match
                            event.message = MarkdownBotPassthrough(message)
                            return func(event)  # Return a coroutine
                        else:
                            logger.debug("but not matched cmd " + message.message + " regex " + kwargs["pattern"])
                    if use_unknown:
                        self._unknowns += [commandhandler]
                    else:
                        self._commands[cmd] = commandhandler  # Add to list of commands so we can call later
                elif kwargs.get("incoming", False):
                    # Watcher-based thing

                    @wraps(func)
                    def subwatcher(message):
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
            self.instance_id = kwargs["__instance_number"]
            return subreg

    def register(self, *args, **kwargs):
        if len(args) == 2:
            logger.debug("Regiser2 for " + args[1])
            self.instances[args[1]].register(args[0])  # Passthrough if we have enough info
        elif len(args) != 0:
            raise TypeError("Takes exactly 2 or 0 params")

        def subreg(func):
            if func.__module__ not in self.instances:
                self.instances[func.__module__] = self.RaphielgangEventsSub()
            kwargs["__instance_number"] = list(self.instances.keys()).index(func.__module__)
            return self.instances[func.__module__].register(**kwargs)(func)
        return subreg

    def errors_handler(self, func):
            """Do nothing as this is handled by ftg framework by default"""
            return func

    async def client_ready(self, client):
            pass

# I just finished writing this. Please, someone, help me!
