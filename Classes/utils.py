from colorama import Fore
from Classes.constants import Constants


def display(commands):
    print("Available data: " + " ".join(commands))

def back():
    print(Fore.YELLOW + "Returning to previous menu ..."+ Fore.RESET)

def quit():
    print(Fore.RED + "Quitting ..." + Fore.RESET)
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
        if type(data["value"]) == list:
            value = "[" + " ,".join(data["value"]) + "]"
        l1 = len(data["name"])
        l2 = len(value)
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
        
        print(data['name']  + " " * (max_len_param - len(data['name'])) + Constants.DELIM.value + required.upper() + " " * (max_len_required - len(required)) + Constants.DELIM.value + value  + " "* (max_len_value - len(value)) + Constants.DELIM.value + data["description"]+ " "*max_len_desc)
    print(dash * total_len)
