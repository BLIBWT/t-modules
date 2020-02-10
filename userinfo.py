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

from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger(__name__)


def register(cb):
    cb(UserInfoMod())


class UserInfoMod(loader.Module):
    """
    User Info :
    -> Get information about users.
    
    Commands :
     
    """
    strings = {"name": "User Info",
               "user_error": "<b>Couldn't find this user.</b>",
               "user_info_arg" : "<b>You must use this command in reply or specify a user !</b>",
               "user_info_bio": "\n• <b>Bio :</b> <code>{}</code>.",
               "user_info_bot": "\n\n• <b>Bot :</b> <code>{}</code>.",
               "user_info_deleted": "\n• <b>Deleted :</b> <code>{}</code>.",
               "user_info_first_name": "\n\n• <b>First name :</b> <code>{}</code>.",
               "user_info_id": "\n• <b>User ID :</b> <code>{}</code>.",
               "user_info_last_name": "\n• <b>Last name :</b> <code>{}</code>.",
               "user_info_picture_id": "\n• <b>Picture ID :</b> <code>{}</code>.",
               "user_info_restricted": "\n• <b>Restricted :</b> <code>{}</code>.",
               "user_info_verified": "\n• <b>Verified :</b> <code>{}</code>.",
               "user_link_id": "<a href='tg://user?id={uid}'>{uid}</a>",
               "user_link_id_custom": "<a href='tg://user?id={uid}'>{arg}</a>",
               "user_link_arg": "<b>You must specify a user !</b>",
               "user_link_searching": "<b>Searching user...</b>"}

    def __init__(self):
        self.name = None

    def config_complete(self):
        self.name = self.strings["name"]

    async def userinfocmd(self, message):
        """
        .userinfo : Get replied message user information.
        .userinfo [user] : Get user information.
         
        """
        if message.is_reply:
            information = await self.client(GetFullUserRequest((await message.get_reply_message()).from_id))
        else:
            args = utils.get_args(message)
            if not args:
                await utils.answer(message, self.strings["user_info_arg"])
                return
            try:
                information = await self.client(GetFullUserRequest(args[0]))
            except ValueError:
                await utils.answer(message, self.strings["user_error"])
                return
        reply = self.strings["user_info_id"].format(utils.escape_html(str(information.user.id)))
        reply += self.strings["user_info_first_name"].format(utils.escape_html(ascii(information.user.first_name)))
        if information.user.last_name is not None:
            reply += self.strings["user_info_last_name"].format(utils.escape_html(ascii(information.user.last_name)))
        reply += self.strings["user_info_bio"].format(utils.escape_html(ascii(information.about)))
        if information.user.photo:
            reply += self.strings["user_info_picture_id"].format(utils.escape_html(str(information.user.photo.dc_id)))
        reply += self.strings["user_info_bot"].format(utils.escape_html(str(information.user.bot)))
        reply += self.strings["user_info_deleted"].format(utils.escape_html(str(information.user.deleted)))
        reply += self.strings["user_info_restricted"].format(utils.escape_html(str(information.user.restricted)))
        reply += self.strings["user_info_verified"].format(utils.escape_html(str(information.user.verified)))
        await utils.answer(message, reply)

    async def userlinkcmd(self, message):
        """
        .userlink [user] : Get user link based on ID or username.
        .userlink [user] [text] : Get user link based on ID or username with custom link text.
        """
        args = utils.get_args(message)
        if len(args) < 1:
            await utils.answer(message, self.strings["user_link_arg"])
            return
        try:
            user = int(args[0])
        except ValueError:
            user = args[0]
        try:
            user = await self.client.get_entity(user)
        except ValueError as e:
            logger.debug(e)
            # look for the user
            await utils.answer(message, self.strings["user_link_searching"])
            await self.client.get_dialogs()
            try:
                user = await self.client.get_entity(user)
            except ValueError:
                await utils.answer(message, self.strings["user_error"])
                return
        if len(args) > 1:
            await utils.answer(message, self.strings["user_link_id_custom"].format(uid=user.id, arg=args[1]))
        else:
            await utils.answer(message, self.strings["user_link_id"].format(uid=user.id))

    async def client_ready(self, client, db):
        self.client = client
