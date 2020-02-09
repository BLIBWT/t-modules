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
logger = logging.getLogger(__name__)


def register(cb):
    cb(CleanerMod())


@loader.tds
class CleanerMod(loader.Module):
    """
    Cleaner :
    -> Delete messages in channels, group chats and private chats.\n
    Commands :
     
    """
    strings = {"name": "Cleaner",
               "del_arg" : "Argument must be 'all', 'me', 'one' or a number between 1 and 1000 !",
               "del_arg_number" : "Number must be between 1 and 1000 !",
               "what": "<i>What I will delete here ?</i>"}

    def __init__(self):
        self._me = None

    def config_complete(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._client = client
        self._me = await client.get_me(True)

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
        # Args
        if del_arg and not message.is_reply:
            # All
            if del_arg == "all":
                msgs = message.client.iter_messages(entity=message.to_id,
                                                    reverse=True)
                async for msg in msgs:
                    del_msgs.append(msg.id)
                    if len(del_msgs) >= 99:
                        await message.client.delete_messages(message.to_id, msgs)
                        del_msgs.clear()
            # Me
            elif del_arg == "me":
                msgs = message.client.iter_messages(entity=message.to_id,
                                                    from_user=self._me.user_id,
                                                    reverse=True)
                async for msg in msgs:
                    del_msgs.append(msg.id)
                    if len(del_msgs) >= 99:
                        await message.client.delete_messages(message.to_id, msgs)
                        del_msgs.clear()
            # Number
            else:
                try:
                    del_number = int(del_arg)
                    if del_number > 0 and del_number <= 1000:
                        del_number = del_number + 1
                        msgs = message.client.iter_messages(entity=message.to_id,
                                                            limit=del_number)
                        async for msg in msgs:
                            del_msgs.append(msg.id)
                            if len(del_msgs) >= 99:
                                await message.client.delete_messages(message.to_id, msgs)
                                del_msgs.clear()
                    else:
                        await utils.answer(message, self.strings["del_arg_number"])
                        return
                except ValueError:
                    await utils.answer(message, self.strings["del_arg"])
                    return
        # Reply
        else:
            if message.is_reply:
                # One
                if del_arg == "one":
                    msg = await message.get_reply_message()
                    del_msgs.append(msg.id)
                    del_msgs.append(message.id)
                # No arg
                else:
                    msgs = message.client.iter_messages(entity=message.to_id, 
                                                        min_id=message.reply_to_msg_id - 1,
                                                        reverse=True)
                    async for msg in msgs:
                        del_msgs.append(msg.id)
                        if len(del_msgs) >= 99:
                            await message.client.delete_messages(message.to_id, msgs)
                            del_msgs.clear()
            else:
                await message.edit(self.strings["what"])
                return
        # Delete
        if del_msgs:
            await message.client.delete_messages(message.to_id, del_msgs)