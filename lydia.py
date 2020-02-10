# -*- coding: future_fstrings -*-

#    Some parts are Copyright (C) Diederik Noordhuis (@AntiEngineer) 2019
#    All licensed under project license

#    Copyright (C) 2020 BLIBWT

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# The API is not yet public. To get a key, go to https://t.me/Intellivoid then ask Qián Zhào.

from .. import loader, utils
import logging
import asyncio
import time
import random
import coffeehouse
from telethon import functions, types

logger = logging.getLogger(__name__)


def register(cb):
    cb(LydiaMod())


class LydiaMod(loader.Module):
    """
    Lydia :
    -> Talk to an AI instead of a human.

    Commands :
     
    """
    strings = {"name": "Lydia",
               "chat_error": ("<b>The AI service can't be enabled or disabled in this chat.</b>\n\n"
                              "<b>Is this a group chat ?</b>"),
               "client_key_cfg_doc": "The API key for lydia, acquire from @IntellivoidDev",
               "ignore_no_common_cfg_doc": "Boolean to ignore users who have no chats in common with you",
               "lydia_enabled": "<b>AI enabled for this user.</b>",
               "lydia_enabled_force": "<b>AI enabled for this user in this chat only.</b>",
               "lydia_enable_error": ("<b>The AI service can't be enabled for this user.</b>\n\n"
                                      "<b>Perhaps it wasn't disabled ?</b>"),
               "lydia_disabled": "<b>AI disabled for this user.</b>",
               "lydia_db_cleaned__disabled_ids": "<b>Successfully cleaned up lydia-disabled IDs.</b>",
               "lydia_db_cleaned_id_sessions": "<b>Successfully cleaned up lydia sessions.</b>",
               "user_error": "<b>Can't find this user.</b>"}

    def __init__(self):
        self.config = loader.ModuleConfig("CLIENT_KEY", "", self.strings["client_key_cfg_doc"],
                                          "IGNORE_NO_COMMON", False, self.strings["ignore_no_common_cfg_doc"])
        self.name = self.strings["name"]
        self._ratelimit = []
        self._cleanup = None

    async def client_ready(self, client, db):
        self._db = db
        self._lydia = coffeehouse.API(self.config["CLIENT_KEY"])
        self._me = await client.get_me()
        # Schedule cleanups
        self._cleanup = asyncio.ensure_future(self.schedule_cleanups())

    async def schedule_cleanups(self):
        """Clean up dead sessions and reschedules itself to run when the next session expiry takes place."""
        sessions = self._db.get(__name__, "sessions", {})
        if len(sessions) == 0:
            return
        nsessions = {}
        t = time.time()
        for ident, session in sessions.items():
            if not session["expires"] < t:
                nsessions.update({ident: session})
            else:
                break  # workaround server bug
                session = await utils.run_sync(self._lydia.get_session, session["session_id"])
                if session.available:
                    nsessions.update({ident: session})
        if len(nsessions) > 1:
            next = min(*[v["expires"] for k, v in nsessions.items()])
        elif len(nsessions) == 1:
            [next] = [v["expires"] for k, v in nsessions.items()]
        else:
            next = t + 86399
        if nsessions != sessions:
            self._db.set(__name__, "sessions", nsessions)
        # Don't worry about the 1 day limit below 3.7.1, if it isn't expired we will just reschedule,
        # as nothing will be matched for deletion.
        await asyncio.sleep(min(next - t, 86399))

        await self.schedule_cleanups()

    async def enlydiacmd(self, message):
        """Enable Lydia for target user.\n """
        old = self._db.get(__name__, "allow", [])
        if message.is_reply:
            user = (await message.get_reply_message()).from_id
        else:
            user = getattr(message.to_id, "user_id", None)
        if user is None:
            await utils.answer(message, self.strings["chat_error"])
            return
        try:
            old.remove(user)
            self._db.set(__name__, "allow", old)
        except ValueError:
            await utils.answer(message, self.strings["lydia_enable_error"])
            return
        await utils.answer(message, self.strings["lydia_enabled"])

    async def forcelydiacmd(self, message):
        """Enable Lydia for user in specific chat."""
        if message.is_reply:
            user = (await message.get_reply_message()).from_id
        else:
            user = getattr(message.to_id, "user_id", None)
        if user is None:
            await utils.answer(message, self.strings["user_error"])
            return
        self._db.set(__name__, "force", self._db.get(__name__, "force", []) + [[utils.get_chat_id(message), user]])
        await utils.answer(message, self.strings["lydia_enabled_force"])

    async def dislydiacmd(self, message):
        """Disable Lydia for the target user.\n """
        if message.is_reply:
            user = (await message.get_reply_message()).from_id
        else:
            user = getattr(message.to_id, "user_id", None)
        if user is None:
            await utils.answer(message, self.strings["chat_error"])
            return

        old = self._db.get(__name__, "force")
        try:
            old.remove([utils.get_chat_id(message), user])
            self._db.set(__name__, "force", old)
        except (ValueError, TypeError, AttributeError):
            pass
        self._db.set(__name__, "allow", self._db.get(__name__, "allow", []) + [user])
        await utils.answer(message, self.strings["lydia_disabled"])

    async def cleanlydiadisabledcmd(self, message):
        """Remove all lydia-disabled users from DB.\n """
        self._db.set(__name__, "allow", [])
        return await utils.answer(message, self.strings["lydia_db_cleaned__disabled_ids"])

    async def cleanlydiasessionscmd(self, message):
        """Remove all active and not active lydia sessions from DB.\n """
        self._db.set(__name__, "sessions", {})
        return await utils.answer(message, self.strings["lydia_db_cleaned_sessions"])

    async def watcher(self, message):
        if self.config["CLIENT_KEY"] == "":
            logger.debug("no key set for lydia, returning")
            return
        if (isinstance(message.to_id, types.PeerUser) and not self.get_allowed(message.from_id)) or \
                (self.is_forced(utils.get_chat_id(message), message.from_id) \
                 and not isinstance(message.to_id, types.PeerUser)):
            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                logger.debug("User is self, bot or verified.")
                return
            else:
                if not isinstance(message.message, str):
                    return
                if len(message.message) == 0:
                    return
                if self.config["IGNORE_NO_COMMON"] and not self.is_forced(utils.get_chat_id(message), message.from_id):
                    fulluser = await message.client(functions.users.GetFullUserRequest(await utils.get_user(message)))
                    if fulluser.common_chats_count == 0:
                        return
                await message.client(functions.messages.SetTypingRequest(
                    peer=await utils.get_user(message),
                    action=types.SendMessageTypingAction()
                ))
                try:
                    # Get a session
                    sessions = self._db.get(__name__, "sessions", {})
                    session = sessions.get(utils.get_chat_id(message), None)
                    if session is None or session["expires"] < time.time():
                        session = await utils.run_sync(self._lydia.create_session)
                        session = {"session_id": session.id, "expires": session.expires}
                        logger.debug(session)
                        sessions[utils.get_chat_id(message)] = session
                        logger.debug(sessions)
                        self._db.set(__name__, "sessions", sessions)
                        if self._cleanup is not None:
                            self._cleanup.cancel()
                        self._cleanup = asyncio.ensure_future(self.schedule_cleanups())
                    logger.debug(session)
                    # AI Response method
                    msg = message.message
                    airesp = await utils.run_sync(self._lydia.think_thought, session["session_id"], str(msg))
                    logger.debug("AI says %s", airesp)
                    if random.randint(0, 1) and isinstance(message.to_id, types.PeerUser):
                        await message.respond(airesp)
                    else:
                        await message.reply(airesp)
                finally:
                    await message.client(functions.messages.SetTypingRequest(
                        peer=await utils.get_user(message),
                        action=types.SendMessageCancelAction()
                    ))

    def get_allowed(self, id):
        return id in self._db.get(__name__, "allow", [])

    def is_forced(self, chat, user_id):
        forced = self._db.get(__name__, "force", [])
        if [chat, user_id] in forced:
            return True
        else:
            return False
