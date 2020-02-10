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

from telethon import functions, types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, ChannelParticipantsAdmins
logger = logging.getLogger(__name__)


def register(cb):
    cb(TagMod())


@loader.tds
class TagMod(loader.Module):
    """
    Tag :
    -> Tag all admins (fast way to report).
    -> Tag all bots (why not ?).
    -> Tag all members (why not ?).

    Commands :
     
    """
    strings = {"name": "Tag",
               "error_chat": "<b>This command can be used in channels and group chats only.</b>",
               "unknow": "An unknow problem as occured.",
               "no_admin": "\n<b>No admin here !</b>",
               "no_bot": "\n<b>No bot here !</b>",
               "no_member": "\n<b>No member here !</b>",
               "user_link": "\n• <a href='tg://user?id={id}'>{name}</a>",
               "user_list_link": ", <a href='tg://user?id={id}'>{name}</a>",
               "user_list_link_first": "<a href='tg://user?id={id}'>{name}</a>"}

    def config_complete(self):
        self.name = self.strings["name"]

    async def admincmd(self, message):
        """
        .admin : Tag all admins (excepted bots).
        .admin [message] : Tag all admins (excepted bots) with message before tags.
         
        """
        if isinstance(message.to_id, PeerUser):
            await utils.answer(message, self.strings["error_chat"])
            return
        count = 0
        rep = ""
        if utils.get_args_raw(message):
            rep = utils.get_args_raw(message)
        if isinstance(message.to_id, PeerChat) or isinstance(message.to_id, PeerChannel):
            users = message.client.iter_participants(message.to_id, filter=ChannelParticipantsAdmins)
            if users:
                async for user in users:
                    if not user.bot and not user.deleted:
                        user_name = user.first_name
                        if user.last_name is not None:
                            user_name += " " + user.last_name
                        rep += self.strings["user_link"].format(id=user.id, name=user_name)
                        count += 1
            if count == 0:
                rep += self.strings["no_admin"]
            await utils.answer(message, rep)
        else:
            await utils.answer(message, self.strings["unknow"])

    async def adminlistcmd(self, message):
        """
        .adminlist : Tag all admins (excepted bots).
        .adminlist [message] : Tag all admins (excepted bots) with message before tags.
         
        """
        if isinstance(message.to_id, PeerUser):
            await utils.answer(message, self.strings["error_chat"])
            return
        count = 0
        rep = ""
        if utils.get_args_raw(message):
            rep = utils.get_args_raw(message)
        if isinstance(message.to_id, PeerChat) or isinstance(message.to_id, PeerChannel):
            users = message.client.iter_participants(message.to_id, filter=ChannelParticipantsAdmins)
            if users:
                first = True
                async for user in users:
                    if not user.bot and not user.deleted:
                        user_name = user.first_name
                        if user.last_name is not None:
                            user_name += " " + user.last_name
                        if first is True:
                            first = False
                            rep += self.strings["user_list_link_first"].format(id=user.id, name=user_name)
                        else:
                            rep += self.strings["user_list_link"].format(id=user.id, name=user_name)
                        count += 1
            if count == 0:
                rep += self.strings["no_admin"]
            await utils.answer(message, rep)
        else:
            await utils.answer(message, self.strings["unknow"])

    async def allcmd(self, message):
        """
        .all : Tag all members.
        .all [message] : Tag all members with message before tags.
         
        """
        if isinstance(message.to_id, PeerUser):
            await utils.answer(message, self.strings["error_chat"])
            return
        rep = ""
        if utils.get_args_raw(message):
            rep = utils.get_args_raw(message)
        if isinstance(message.to_id, PeerChat) or isinstance(message.to_id, PeerChannel):
            users = message.client.iter_participants(message.to_id)
            if users:
                async for user in users:
                    user_name = user.first_name
                    if user.last_name is not None:
                        user_name += " " + user.last_name
                    rep += self.strings["user_link"].format(id=user.id, name=user_name)
            else:
                rep += self.strings["no_member"]
            await utils.answer(message, rep)
        else:
            await utils.answer(message, self.strings["unknow"])

    async def botcmd(self, message):
        """
        .bot : Tag all bots.
        .bot [message] : Tag all bots with message before tags.
         
        """
        if isinstance(message.to_id, PeerUser):
            await utils.answer(message, self.strings["error_chat"])
            return
        count = 0
        rep = ""
        if utils.get_args_raw(message):
            rep = utils.get_args_raw(message)
        if isinstance(message.to_id, PeerChat) or isinstance(message.to_id, PeerChannel):
            users = message.client.iter_participants(message.to_id)
            if users:
                async for user in users:
                    if user.bot:
                        user_name = user.first_name
                        if user.last_name is not None:
                            user_name += " " + user.last_name
                        rep += self.strings["user_link"].format(id=user.id, name=user_name)
                        count += 1
            if count == 0:
                rep += self.strings["no_bot"]
            await utils.answer(message, rep)
        else:
            await utils.answer(message, self.strings["unknow"])
