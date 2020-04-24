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

logger = logging.getLogger(__name__)


def register(cb):
    cb(CleanerMod())


@loader.tds
class CleanerMod(loader.Module):
    """
    -> Delete messages in channels, group chats and private chats.\n
    Commands :
     
    """
    strings = {"name": "Cleaner",
               "del_arg": "Argument must be 'all', 'me', 'one' or a number between 1 and 1000 !",
               "del_arg_number": "Number must be between 1 and 1000 !",
               "del_what": "<i>What I will delete here ?</i>",
               "unknow": "An unknow problem as occured."}

    def __init__(self):
        self.me = None

    def config_complete(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.me = await client.get_me(True)

    async def delcmd(self, message):
        """
        In reply :
        .del : Delete all messages since message in reply.
        .del one : Delete the message in reply.

        Not in reply :
        .del all : Delete all messages (require be admin for channels and group chats, else same effect than ".del me").
        .del me : Delete all my messages.
         
        """
        del_arg = utils.get_args_raw(message)
        del_msgs = []
        msgs = []
        # Args
        if del_arg and not message.is_reply:
            # All or Me
            if del_arg == "all" or del_arg == "me":
                msgs = await self.del_no_reply_arg(message, del_arg)
            # Number
            else:
                try:
                    del_number = int(del_arg)
                    if del_number > 0 and del_number <= 1000:
                        del_number = del_number + 1
                        msgs = await self.del_no_reply_number(message, del_number)
                    else:
                        await utils.answer(message, self.strings["del_arg_number"])
                        return
                except ValueError:
                    await utils.answer(message, self.strings["del_arg"])
                    return
        # Reply
        else:
            if message.is_reply:
                if del_arg and del_arg == "one":
                    del_msgs.append(message.id)
                    del_msgs.append(message.reply_to_msg_id)
                    await message.client.delete_messages(message.to_id, del_msgs)
                    return
                msgs = await self.del_reply(message)
            else:
                await utils.answer(message, self.strings["del_what"])
                return
        # Delete
        if msgs:
            async for msg in msgs:
                del_msgs.append(msg.id)
                if len(del_msgs) >= 99:
                    await message.client.delete_messages(message.to_id, del_msgs)
                    del_msgs.clear()
            if del_msgs:
                await message.client.delete_messages(message.to_id, del_msgs)
        else:
            await utils.answer(message, self.strings["unknow"])

    async def del_no_reply_arg(self, message, arg):
        user_id = None
        if arg == "me":
            user_id = self.me.user_id
        msgs = message.client.iter_messages(entity=message.to_id,
                                            from_user=user_id,
                                            reverse=True)
        return msgs

    async def del_no_reply_number(self, message, number):
        msgs = message.client.iter_messages(entity=message.to_id,
                                            limit=number)
        return msgs

    async def del_reply(self, message):
        msgs = message.client.iter_messages(entity=message.to_id,
                                            min_id=message.reply_to_msg_id - 1,
                                            reverse=True)
        return msgs
