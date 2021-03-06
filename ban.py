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
from telethon import errors

logger = logging.getLogger(__name__)


def register(cb):
    cb(BanMod())


@loader.tds
class BanMod(loader.Module):
    """
    -> Ban & Unban people in group where you're admin.\n
    Commands :
     
    """
    strings = {"name": "Ban",
               "ban_user_done": "<b><a href='tg://user?id={id}'>{arg}</a></b> banned !",
               "ban_user_done_username": "<b>@{}</b> banned !",
               "ban_who": "<i>Who I will ban here ?</i>",
               "banrm_user_done": "<b><a href='tg://user?id={id}'>{arg}</a></b> banned and messages deleted !",
               "banrm_user_done_username": "<b>@{}</b> banned and messages deleted !",
               "command_error": ("<b>You must be admin of the group to use this command, "
                                 "and you can't use it on you or admins not promoted by you !</b>"),
               "group_error": "<b>You must use this command in supergroup !</b>",
               "unban_user_done": "<b><a href='tg://user?id={id}'>{arg}</a></b> unbanned !",
               "unban_user_done_username": "<b>@{}</b> unbanned !",
               "unban_who": "<i>Who I will unban here ?</i>",
               "user_error": "<b>Couldn't find this user.</b>"}

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
            return await utils.answer(message, self.strings["group_error"])
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
                user = await self.client.get_entity(user)
            except ValueError:
                await utils.answer(message, self.strings["user_error"])
                return
        if not isinstance(user.id, int):
            await utils.answer(message, self.strings["user_error"])
            return
        try:
            await self.client.edit_permissions(message.to_id, user.id, view_messages=False)
        except (errors.ChatAdminRequiredError, errors.UserAdminInvalidError, ValueError):
            await utils.answer(message, self.strings["command_error"])
            return
        rep = ""
        if user.username is not None:
            rep = self.strings["ban_user_done_username"].format(utils.escape_html(user.username))
        else:
            arg = user.first_name
            if user.last_name is not None:
                arg += " "
                arg += user.last_name
            rep = self.strings["ban_user_done"].format(id=user.id, arg=utils.escape_html(arg))
        await utils.answer(message, rep)

    async def banrmcmd(self, message):
        """
        banrm : Ban & Remove Messages.

        In reply :
        .banrm : Ban replied message user and delete all messages from this user.

        Not in reply :
        .banrm [user] : Ban user by ID or username and delete all messages from this user.
         
        """
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings["group_error"])
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
                user = await self.client.get_entity(user)
            except ValueError:
                await utils.answer(message, self.strings["user_error"])
                return
        if not isinstance(user.id, int):
            await utils.answer(message, self.strings["user_error"])
            return
        try:
            await self.client.edit_permissions(message.to_id, user.id, view_messages=False)
        except (errors.ChatAdminRequiredError, errors.UserAdminInvalidError, ValueError):
            await utils.answer(message, self.strings["command_error"])
            return
        await self.del_messages(message, user)
        rep = ""
        if user.username is not None:
            rep = self.strings["banrm_user_done_username"].format(utils.escape_html(user.username))
        else:
            arg = user.first_name
            if user.last_name is not None:
                arg += " "
                arg += user.last_name
            rep = self.strings["banrm_user_done"].format(id=user.id, arg=utils.escape_html(arg))
        await utils.answer(message, rep)

    async def unbancmd(self, message):
        """
        In reply :
        .unban : Unban replied message user.

        Not in reply :
        .unban [user] : Unban user by ID or username.
         
        """
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings["group_error"])
        if message.is_reply:
            user = await utils.get_user(await message.get_reply_message())
        else:
            args = utils.get_args(message)
            if not args:
                await utils.answer(message, self.strings["unban_who"])
                return
            try:
                user = int(args[0])
            except ValueError:
                user = str(args[0])
            try:
                user = await self.client.get_entity(user)
            except ValueError:
                await utils.answer(message, self.strings["user_error"])
                return
        if not isinstance(user.id, int):
            await utils.answer(message, self.strings["user_error"])
            return
        try:
            await self.client.edit_permissions(message.to_id, user.id, view_messages=True)
        except (errors.ChatAdminRequiredError, errors.UserAdminInvalidError, ValueError):
            await utils.answer(message, self.strings["command_error"])
            return
        rep = ""
        if user.username is not None:
            rep = self.strings["unban_user_done_username"].format(utils.escape_html(user.username))
        else:
            arg = user.first_name
            if user.last_name is not None:
                arg += " "
                arg += user.last_name
            rep = self.strings["unban_user_done"].format(id=user.id, arg=utils.escape_html(arg))
        await utils.answer(message, rep)

    async def del_messages(self, message, user):
        del_msgs = []
        async for msg in message.client.iter_messages(entity=message.to_id,
                                                      from_user=user.id,
                                                      reverse=True):
            del_msgs.append(msg.id)
            if len(del_msgs) >= 99:
                await message.client.delete_messages(message.to_id, del_msgs)
                del_msgs.clear()
        if del_msgs:
            await message.client.delete_messages(message.to_id, del_msgs)
