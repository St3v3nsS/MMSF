from colorama import Fore
from Classes.constants import Constants
import subprocess
import psutil
import socket


def display(commands):
    print("Available data: " + " ".join(commands))

def back():
    print(Fore.YELLOW + "Returning to previous menu ..."+ Fore.RESET)

def quit():
    print(Fore.RED + "Quitting ..." + Fore.RESET)
    for proc in psutil.process_iter():
        try:
            if proc.name() == "systemd":
                pid = proc.pid
            if proc.ppid() == pid and ("frida" in proc.name() or "objection" in proc.name()):
                proc.kill()
            if proc.name() == "objection":
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(Fore.RED + '[-] Done cleaning ... ')
    exit(0)

def unknown_cmd():
    print(Fore.RED + "[-] Unknown command" + Fore.RESET)

def listmodules(modules, descriptions):
    # Pretty print the available modules using string lengths 
    print("Available modules: ")

    max_value = len(max(modules + ["MODULE"], key=len))
    total = max_value + len(max(descriptions + ["DESCRIPTION"], key=len)) + len(Constants.DELIM.value) + 1
    
    header = "MODULE" + " " * (max_value - len("MODULE")) + Constants.DELIM.value + "DESCRIPTION"
    
    # print the header
    print("-"*total)
    print(header)
    print("-"*total)
    
    # print the values
    for i, data in enumerate(modules):
        print(data + " " * (max_value - len(data)) + Constants.DELIM.value + descriptions[i])
    
    # end the printing function
    print("-"*total)

def print_show_table(params):
    # Pretty print the show table by using the max value

    max_len_param = len("Param")
    max_len_required = len("REQUIRED")
    max_len_value = len("VALUE")
    max_len_desc = len("DESCRIPTION")
    
    # get the max values
    for data in params:
        value = data["value"]
        if type(data["value"]) == list and len(data["value"]) > 0 and type(data["value"][0]) == dict:
            vals = []
            for itm in data["value"]:
                val = ""
                for key in itm.keys():
                    val += f'{itm[key]} '
                vals.append(val)
            data["value"] = vals
            print(data["value"])
        if type(data["value"]) == list:
            value = "[" + " ,".join(data["value"]) + "]"
        l1 = len(data["name"])
        l2 = len(str(value))
        l3 = len(data["description"])
        if  l1 > max_len_param:
            max_len_param = l1
        if l2 > max_len_value:
            max_len_value = l2
        if l3 > max_len_desc:
            max_len_desc = l3

    total_len = max_len_param + max_len_required + max_len_value + len(Constants.DELIM.value)*3 + max_len_desc + 1
    
    header = "PARAM" + " " * (max_len_param - len("PARAM")) + Constants.DELIM.value + "REQUIRED" + " " * (max_len_required-len("REQUIRED")) + Constants.DELIM.value + "VALUE" + " "* (max_len_value - len("VALUE")) + Constants.DELIM.value + "DESCRIPTION" + " "*max_len_desc
    dash = "-"

    # printing the data
    print(dash*total_len)
    print(header)
    print(dash*total_len)

    for data in params:
        # handle the required field
        required = "True"
        if "required" in data.keys():
            required = "False"  
        # value + " " * max - len(value) so it looks nice
        value = data["value"]
        if type(data["value"]) == list:
            value = "[" + ", ".join(data["value"]) + "]"
        
        print(data['name']  + " " * (max_len_param - len(data['name'])) + Constants.DELIM.value + required.upper() + " " * (max_len_required - len(required)) + Constants.DELIM.value + str(value)  + " "* (max_len_value - len(str(value))) + Constants.DELIM.value + data["description"]+ " "*max_len_desc)
    print(dash * total_len)

def check_alive_devices():
    return alive_android_devices() or alive_ios_devices()

def alive_android_devices():
    cmd = f'{Constants.ADB.value} devices -l'
    p = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().splitlines()
    return len(p)>2

def alive_ios_devices():
    cmd = "frida-ps -U"
    p = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().splitlines()
    return len(p) > 1

def is_port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',port))
    sock.close()
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    result2 = sock.connect_ex(('::1',port, 0, 0))
    sock.close()
    if result == 0 or result2 == 0:
        return True
    return False

def execute_command(cmd, stdout, tool):
    print(Fore.YELLOW + "Command used: " + cmd + Fore.RESET)
    with open(stdout, "a") as out:
        subprocess.Popen(cmd, stdout=out, stderr=out, shell=True)
    
    found = False
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            if tool in proc.name():
                if any(x in cmd for x in proc.cmdline()):
                    print(Fore.GREEN + '[+] Command executed successfully' + Fore.RESET)
                    found = True
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
    if not found:
        print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
        return False
    
def find_command(cmd, search_word):
    found = False
    for proc in psutil.process_iter():
        try:
            if cmd in proc.name():
                if search_word in proc.cmdline():
                    found = True
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
    if not found:
        return False
    
def nice_print(data):
    print(data)

def search(cmd, data):
    for key in data.keys():
        if cmd in key:
            nice_print(data[key])
    
    