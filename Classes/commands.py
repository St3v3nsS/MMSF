from enum import Enum
from colorama import Fore

class Commands(Enum):

    COMMAND_PACKAGEINFO={"cmd": f"run app.package.info -a ", "display": Fore.GREEN + "[+] Running package info ...", "fname": "package_info.txt"}
    COMMAND_ATTACKSURFACE={"cmd": f"run app.package.attacksurface ", "display": Fore.GREEN + "[+] Running attack surface ..", "fname": "attack_surface.txt"}
    COMMAND_ACTIVITYINFO={"cmd": f"run app.activity.info -u -a ", "display": Fore.GREEN + "[+] Running activity info ...", "fname": "activity_info.txt"}
    COMMAND_PROVIDERINFO={"cmd": f"run app.provider.info -a ", "display": Fore.GREEN + "[+] Running provider information ...", "fname": "content_providers.txt"}
    COMMAND_FINDURIS={"cmd": f"run scanner.provider.finduris -a ", "display": Fore.GREEN + "[+] Finding providers uris ...", "fname": "finduris.txt"}
    COMMAND_SQLTABLES={"cmd": f"run scanner.provider.sqltables -a ", "display": Fore.GREEN + "[+] Scanning for SQL Tables ...", "fname": "sql_tables.txt"}
    COMMAND_SQLINJECTION={"cmd": f"run scanner.provider.injection -a ", "display": Fore.GREEN + "[+] Scanning for injection...", "fname": "injection.txt"}
    COMMAND_PATHTRAVERSAL={"cmd": f"run scanner.provider.traversal -a ", "display": Fore.GREEN + "[+] Scanning for path traversal ...", "fname": "traversal.txt"}
    COMMAND_BROADCASTRECEIVERS={"cmd": f"run app.broadcast.info -a ", "display": Fore.GREEN + "[+] Finding broadcast receivers ...", "fname": "broadcast_receivers.txt"}
    COMMAND_SERVICES={"cmd": f"run app.service.info -a ", "display": Fore.GREEN + "[+] Running app.service.info ...", "fname": "service_info.txt"}
    COMMAND_BROWSABLE={"cmd": f"run scanner.activity.browsable -a ", "display": Fore.GREEN + "[+] Running scanner.activity.browsable ...", "fname": "browsable.txt"}
    COMMAND_MANIFEST={"cmd": f"run app.package.manifest ", "display": Fore.GREEN + "[+] Gathering manifest data ...", "fname": "AndroidManifest.xml"}    

    START_ACTIVITY={"cmd": f"run app.activity.start --component ", "display": Fore.YELLOW + "[+] Starting the activity ..."}
    SEND_BROADCAST={"cmd": f"run app.broadcast.send", "display": Fore.YELLOW + "[+] Sending the broadcast message ..."}
    QUERY_CONTENT={"cmd": f"run app.provider.query ", "display": Fore.YELLOW + "[+] Querying the content provider ..."}
    FIND_APP={"cmd": f"run app.package.list", "display": Fore.YELLOW + "[+] Finding the application details ..."}
    LAUNCH_DEEPLINK={"cmd": "run app.activity.start --action android.intent.action.VIEW --data-uri ", "display": Fore.YELLOW + "[+] Launching deeplink attack ..."}
    SNIFF_DATA={"cmd": "run app.broadcast.sniff", "display": Fore.YELLOW + "[+] Sniffing for data ..."}
    UPDATE_PROVIDER={"cmd": "run app.provider.update", "display": Fore.YELLOW + "[+] Updating Content Provider with data ..."}
    INSERT_PROVIDER={"cmd": "run app.provider.insert", "display": Fore.YELLOW + "[+] Inserting data in Content Provider ..."}
    READ_PROVIDER={"cmd": "run app.provider.read", "display": Fore.YELLOW + "[+] Read Files using Content Provider ..."}
