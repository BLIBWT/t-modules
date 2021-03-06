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

import logging
import platform
import asyncio
import shutil
import sys

import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(InfoMod())


@loader.tds
class InfoMod(loader.Module):
    """
    -> Provides system information about the system hosting this bot.\n
    Command :
     
    """
    strings = {"name": "System Info",
               "android_patch": "<b>Android Security Patch:</b> <code>{}</code>.",
               "android_sdk": "<b>Android SDK:</b> <code>{}</code>.",
               "android_ver": "<b>Android Version:</b> <code>{}</code>.",
               "arch": "<b>Arch:</b> <code>{}</code>.",
               "distro": "<b>Linux Distribution:</b> <code>{}</code>.",
               "info_title": "<b>System Info</b>",
               "kernel": "<b>Kernel:</b> <code>{}</code>.",
               "os": "<b>OS:</b> <code>{}</code>.",
               "python_version": "<b>Python version:</b> <code>{}</code>.",
               "telethon_version": "<b>Telethon version:</b> <code>{}</code>.",
               "unknown_distro": "<b>Could not determine Linux distribution.</b>"}

    def __init__(self):
        self.name = self.strings["name"]

    async def infocmd(self, message):
        """Shows system information."""
        reply = self.strings["info_title"]
        reply += "\n" + self.strings["kernel"].format(utils.escape_html(platform.release()))
        reply += "\n" + self.strings["arch"].format(utils.escape_html(platform.architecture()[0]))
        reply += "\n" + self.strings["os"].format(utils.escape_html(platform.system()))

        if platform.system() == "Linux":
            done = False
            try:
                a = open("/etc/os-release").readlines()
                b = {}
                for line in a:
                    b[line.split("=")[0]] = line.split("=")[1].strip().strip("\"")
                reply += "\n" + self.strings["distro"].format(utils.escape_html(b["PRETTY_NAME"]))
                done = True
            except FileNotFoundError:
                getprop = shutil.which("getprop")
                if getprop is not None:
                    sdk = await asyncio.create_subprocess_exec(getprop, "ro.build.version.sdk",
                                                               stdout=asyncio.subprocess.PIPE)
                    ver = await asyncio.create_subprocess_exec(getprop, "ro.build.version.release",
                                                               stdout=asyncio.subprocess.PIPE)
                    sec = await asyncio.create_subprocess_exec(getprop, "ro.build.version.security_patch",
                                                               stdout=asyncio.subprocess.PIPE)
                    sdks, unused = await sdk.communicate()
                    vers, unused = await ver.communicate()
                    secs, unused = await sec.communicate()
                    if sdk.returncode == 0 and ver.returncode == 0 and sec.returncode == 0:
                        reply += "\n" + self.strings["android_sdk"].format(sdks.decode("utf-8").strip())
                        reply += "\n" + self.strings["android_ver"].format(vers.decode("utf-8").strip())
                        reply += "\n" + self.strings["android_patch"].format(secs.decode("utf-8").strip())
                        done = True
            if not done:
                reply += "\n" + self.strings["unknown_distro"]
        reply += "\n" + self.strings["python_version"].format(utils.escape_html(sys.version))
        reply += "\n" + self.strings["telethon_version"].format(utils.escape_html(telethon.__version__))
        await utils.answer(message, reply)
