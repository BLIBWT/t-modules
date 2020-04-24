# -*- coding: future_fstrings -*-

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

from .. import loader, utils
import logging
from telethon.tl.types import PeerChannel

logger = logging.getLogger(__name__)


def register(cb):
    cb(AdminMod())


@loader.tds
class AdminMod(loader.Module):
    """
    -> Delete messages in channels, group chats and private chats.\n
    Commands :
     
    """
    strings = {"name": "Administration",
               "ban_group": "<b>You must use this command in supergroup !</b>",
               "ban_user_done": "<b><a href='tg://user?id={id}'>{arg}</a></b> banned !",
               "ban_user_done_username": "<b>@{}</b> banned !",
               "ban_user_error": "<b>Couldn't find this user.</b>",
               "ban_who": "<i>Who I will ban here ?</i>"}

    def config_complete(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client

    async def bancmd(self, message):
        """
        In reply :
        .ban : Ban replied message user.

        Not in reply :
        .ban [user] : Ban user by ID or username.
         
        """
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings["ban_group"])
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                await utils.answer(message, self.strings["ban_who"])
                return
            try:
                user = int(args[0])
            except ValueError:
                user = str(args[0])
            try:
                user = await self.client.get_entity(args[0])
            except ValueError:
                await utils.answer(message, self.strings["ban_user_error"])
                return
        if not isinstance(user.id, int):
            await utils.answer(message, self.strings["ban_user_error"])
            return
        await self.client.edit_permissions(message.to_id, user.id, view_messages=False)
        rep = ""
        if user.username is not None:
            rep = self.strings["ban_user_done_username"].format(utils.escape_html(user.username))
        else:
            arg = user.first_name
            if user.last_name is not None:
                arg += " "
                arg += user.last_name
            rep = self.strings["ban_user_done"].format(utils.escape_html(id=user.id, arg=arg))
        await utils.answer(message, rep)
