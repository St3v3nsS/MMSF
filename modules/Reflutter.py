#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ReFlutter Module for MMSF
This is the main module file that integrates with the MMSF framework
"""

import os
import sys
import readline
import shlex
from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, print_show_table, unknown_cmd, quit_app

class Reflutter:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Bypass SSL pinning in Flutter apps and route traffic through Burp Suite"
        self._name = "reflutter"
        self.config = {
            'app': '',
            'apk_path': '',
            'burp_host': '127.0.0.1'
        }
    
    def execute(self, mmsf):
        """Execute the ReFlutter module"""
        def handle_reflutter():
            """Handle ReFlutter module interaction"""
            while True:
                def data_completer(text, state):
                    options = ['app', 'apk_path', 'burp_host']
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None
                
                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.reflutter_sslpinning(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (reflutter/sslpinning)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                
                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (reflutter/sslpinning/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        
                        if cmd.lower() == "app" and args:
                            self.config["app"] = args[0]
                        elif cmd.lower() == "apk_path" and args:
                            self.config["apk_path"] = args[0]
                        elif cmd.lower() == "burp_host" and args:
                            self.config["burp_host"] = args[0]
                        else:
                            if execute(cmd.lower(), self.config):
                                break
                else:
                    if execute(value, self.config) == 2:
                        return 1

        # Main execution loop
        modules = ["sslpinning"]
        descriptions = [
            "Run ReFlutter SSL pinning bypass"
        ]

        if mmsf.is_ios():
            print(Fore.YELLOW + "[!] ReFlutter is currently only supported for Android. Please use the frida submodule for iOS testing." + Fore.RESET)
            back()
            return 1

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (reflutter)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                unknown_cmd()
            elif input_val[0].lower() == "exit":
                quit_app()
            elif input_val[0].lower() == "listmodules":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "sslpinning":
                    handle_reflutter()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()
