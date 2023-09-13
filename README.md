# MMSF
Massive Mobile Security Framework or MMSF is a mobile framework that combines functionalities from frida, objection, drozer and many more. 

# Installation

```bash
git clone https://github.com/St3v3nsS/MMSF.git
cd MMSF
python3 -m pip install -r requirements.txt
python3 mmsfupdate.py
```

![Usage](https://github.com/St3v3nsS/MMSF/blob/main/images/usage.gif)

# Usage

Short example of how you can interact with the tool. 

```bash
$ python3 mmsf.py 
mmsf> listmodules
mmsf> usemodule rootdetection
mmsf (rootdetection)> usemodule frida
mmsf (rootdetection/frida)> set
mmsf (rootdetection/frida/set)> app com.st3v3nss.TestRMS
mmsf (rootdetection/frida/set)> run 
```

# Available modules

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE                      |  DESCRIPTION
----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------
biometrics                  |  Bypass Biometrics authentication on both iOS/Android
broadcast                   |  Send a broadcast intent
provider                    |  Exploit the exported content provider to extract data
deeplink                    |  Launch a deeplink with supplied value or generate malicious files to steal sensitive data
backup                      |  Extract or restore backup from Android Application
find                        |  Find the package name of an application and/or its details by supplying a filter keyword
handleapk                   |  Generate, sign, pull and install an APK
intent                      |  Start an intent using supplied values like: extra values, action, mimetype or data
jailbreakdetection          |  Bypass the ios Jailbreak detection mechanisms through different methods
patchobjection              |  Patch IPA or APK
rootdetection               |  Bypass the Android root detection mechanisms through different methods
sslpinning                  |  Bypass the SSL Pinning mechanism through different methods
scan                        |  Scan the application to retrieve crucial information such as exported activities, path traversal, SQL injections, attack vector and so on
sniff                       |  Sniffing a broadcast intent
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Useful commands

Here is a list of commands that you can use

| COMMAND | DESCRIPTION|
|---------|------------|
|listmodules| List all the available modules or submodules|
|usemodule | Use the specific module|
|show| Display parameters|
|set| Set parameters|
|run | Execute module |
|back | Return to previous menu |
|exit | Quit the mssf|

# Support me

<a href="https://www.buymeacoffee.com/st3v3nss" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" height="41" width="174"></a>

# To-do

- [ ] Implement Autocomplete
- [ ] Objection android bypass
- [ ] Implement global module change like usemodule rootdetection/frida
- [ ] Modify the signing method to ubersign
- [ ] Add keystore checks
- [x] Search command
- [ ] Extract important strings from the app
- [ ] Add Nuclei checks
- [ ] RMS Integration
- [ ] Install Burp Certificate
- [ ] Clipboard manager
- [ ] Patch IPA 
- [ ] Emulator Bypass
- [ ] Split apk install