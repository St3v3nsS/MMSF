//Path list for fileExistsAtPath and fopen
const tpLibs = [
    "Substrate",
    "cycript",
    "frida",
    "SSLKillSwitch2",
    "SSLKillSwitch",
    "SubstrateLoader"
]

var jailbreakPaths = [
    "dropbear_rsa_host_key",
    "Library/LaunchDaemons/dropbear.plist",
    "/Applications/Cydia.app",
    "/Applications/FakeCarrier.app",
    "/Applications/Icy.app",
    "/Applications/IntelliScreen.app",
    "/Applications/MxTube.app",
    "/Applications/RockApp.app",
    "/Applications/SBSettings.app",
    "/Applications/WinterBoard.app",
    "/Applications/blackra1n.app",
    "/Library/MobileSubstrate/DynamicLibraries/LiveClock.plist",
    "/Library/MobileSubstrate/DynamicLibraries/Veency.plist",
    "/Library/MobileSubstrate/MobileSubstrate.dylib",
    "/Library/dpkg/info/kjc.checkra1n.mobilesubstraterepo.list",
    "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
    "/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist",
    "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
    "/bin/bash",
    "/bin/sh",
    "/bin/su",
    "/etc/apt",
    "/etc/apt/preferences.d/checkra1n",
    "/etc/ssh/sshd_config",
    "/pguntether",
    "/private/var/lib/apt",
    "/private/var/lib/apt/",
    "/private/var/lib/cydia",
    "/private/var/mobile/Library/SBSettings/Themes",
    "/private/var/stash",
    "/private/var/tmp/cydia.log",
    "/usr/bin/cycript",
    "/usr/bin/ssh",
    "/usr/bin/sshd",
    "/usr/binsshd", // Note: Original typo "usr/binsshd" retained.
    "/usr/lib/frida",
    "/usr/lib/frida/frida-agent.dylib",
    "/usr/libexec/cydia/firmware.sh",
    "/usr/libexec/sftp-server",
    "/usr/libexec/ssh-keysign",
    "/usr/sbin/frida-server",
    "/usr/sbin/sshd",
    "/var/cache/apt",
    "/var/lib/cydia",
    "/var/log/syslog",
    "/var/mobile/Media/.evasi0n7_installed",
    "/var/root/.bash_history",
    "/var/tmp/cydia.log",
    "/Applications/Backgrounder.app",
    "/Applications/Pirni.app",
    "/Applications/Terminal.app",
    "/Applications/biteSMS.app",
    "/Applications/iFile.app",
    "/Applications/iProtect.app",
    "/Library/MobileSubstrate/DynamicLibraries/SBSettings.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/SBSettings.plist",
    "/System/Library/LaunchDaemons/com.bigboss.sbsettingsd.plist",
    "/System/Library/PreferenceBundles/CydiaSettings.bundle",
    "/User/Library/SBSettings",
    "/etc/profile.d/terminal.sh",
    "/private/etc/profile.d/terminal.sh",
    "/private/var/lib/dpkg/info/cydia-sources.list",
    "/private/var/lib/dpkg/info/cydia.list",
    "/private/var/root/Media/Cydia",
    "/usr/bin/sbsettingsd",
    "/usr/lib/libhooker.dylib",
    "/private/etc/apt/trusted.gpg.d/*",
    "/usr/lib/libsubstitute.dylib",
    "/usr/lib/substrate",
    "/usr/libexec/cydia",
    "/private/etc/apt/sources.list.d/procursus.sources",
    "/private/etc/apt/sources.list.d/sileo.sources",
    "/var/lib/dpkg/info/cydia-sources.list",
    "/var/lib/dpkg/info/cydia.list",
    "/var/lib/dpkg/info/mobileterminal.list",
    "/var/lib/dpkg/info/mobileterminal.postinst",
    "/var/mobile/Library/SBSettings",
    "/usr/lib/libcycript.dylib",
    "/usr/local/bin/cycript",
    "/var/lib/apt",
    "/Applications/crackerxi.app",
    "/etc/alternatives/sh",
    "/etc/apt/",
    "/etc/apt/sources.list.d/cydia.list",
    "/etc/apt/sources.list.d/electra.list",
    "/etc/apt/sources.list.d/sileo.sourcs", // Note: Original typo "sileo.sourcs" retained.
    "/etc/apt/undecimus/undecimus.list",
    "/jb/amfid_payload.dylib",
    "/jb/jailbreakd.plist",
    "/jb/libjailbreak.dylib",
    "/jb/lzma",
    "/jb/offsets.plists", // Note: Original typo "offsets.plists" retained.
    "/Library/MobileSubstrate/CydiaSubstrate.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/*",
    "/private/var/cache/apt",
    "/private/var/log/syslog",
    "/private/var/tmp/frida-*.dylib",
    "/private/var/Users",
    "/usr/lib/libjailbreak.dylib",
    "/usr/libexec/sshd-keygen-wrapper",
    "/usr/share/jailbreak/injectme.plist",
    "/var/lib/dpkg/info/mobilesubstrate.dylib",
    "/var/log/apt",
    "/var/mobile/Library/Caches/com.saurik.Cydia/sources.list",
    "/.bootstrapped_electra",
    "/.cydia_no_stash",
    "/.installed_unc0ver",
    "/Library/MobileSubstrate/DynamicLibraries/Choicy.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/0Shadow.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/afc2dService.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/AppSyncUnified-FrontBoard.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/AppSyncUnified-installd.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/ChoicySB.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/dygz.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/LiveClock.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/MobileSafety.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/PreferenceLoader.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/RocketBootstrap.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/Veency.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/xCon.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/zorro.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/zzzzHeiBaoLib.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/",
    "/usr/lib/libsubstrate.dylib/SSLKillSwitch2.dylib",
    "/usr/lib/libsubstrate.dylib/SSLKillSwitch2.plist",
    "/usr/lib/CepheiUI.framework/CepheiUI",
    "/usr/lib/substrate/SubstrateInserter.dylib",
    "/usr/lib/substrate/SubstrateLoader.dylib",
    "/usr/lib/substrate/SubstrateBootstrap.dylib",
    "/Library/MobileSubstrate/",
    "/Library/PreferenceBundles/SubstitutePrefs.bundle/",
    "/Library/PreferenceBundles/SubstitutePrefs.bundle/Info.plist",
    "/Library/PreferenceBundles/SubstitutePrefs.bundle/SubstitutePrefs",
    "/Library/PreferenceLoader/Preferences/SubstituteSettings.plist",
    "/private/etc/alternatives/sh",
    "/private/etc/apt",
    "/private/etc/apt/preferences.d/cydia",
    "/private/etc/clutch.conf",
    "/private/etc/clutch_cracked.plist",
    "/private/etc/dpkg/origins/debian",
    "/private/etc/rc.d/substitute-launcher",
    "/private/etc/ssh/sshd_config",
    "/private/var/cache/apt/",
    "/private/var/cache/clutch.plist",
    "/private/var/cache/clutch_cracked.plist",
    "/private/var/db/stash",
    "/private/var/evasi0n",
    "/private/var/lib/dpkg/",
    "/private/var/mobile/Library/Filza/",
    "/private/var/mobile/Library/Filza/pasteboard.plist",
    "/private/var/mobile/Library/Cydia/",
    "/private/var/mobile/Library/Preferences/com.ex.substitute.plist",
    "/private/var/mobile/Library/SBSettingsThemes/",
    "/private/var/MobileSoftwareUpdate/mnt1/System/Library/PrivateFrameworks/DictionaryServices.framework/SubstituteCharacters.plist",
    "/private/var/root/Documents/Cracked/",
    "/System/Library/PrivateFrameworks/DictionaryServices.framework/SubstituteCharacters.plist",
    "/usr/bin/scp",
    "/usr/bin/sftp",
    "/usr/bin/ssh-add",
    "/usr/bin/ssh-agent",
    "/usr/bin/ssh-keygen",
    "/usr/bin/ssh-keyscan",
    "/usr/bin/sinject",
    "/usr/include/substrate.h",
    "/usr/lib/cycript0.9/",
    "/usr/lib/cycript0.9/com/",
    "/usr/lib/cycript0.9/com/saurik/",
    "/usr/lib/cycript0.9/com/saurik/substrate/",
    "/usr/lib/cycript0.9/com/saurik/substrate/MS.cy",
    "/usr/libexec/filza/Filza",
    "/usr/libexec/substituted",
    "/usr/libexec/sinject-vpa",
    "/usr/libexec/substrated",
    "/var/cache/apt/",
    "/var/cache/clutch.plist",
    "/var/cache/clutch_cracked.plist",
    "/var/db/stash",
    "/var/evasi0n",
    "/var/lib/apt/",
    "/var/lib/cydia/",
    "/var/lib/dpkg/",
    "/var/mobile/Library/Filza/",
    "/var/mobile/Library/Filza/pasteboard.plist",
    "/var/mobile/Library/Cydia/",
    "/var/mobile/Library/Preferences/com.ex.substitute.plist",
    "/var/mobile/Library/SBSettingsThemes/",
    "/var/MobileSoftwareUpdate/mnt1/System/Library/PrivateFrameworks/DictionaryServices.framework/SubstituteCharacters.plist",
    "/var/root/Documents/Cracked/",
    "/var/stash",
    "/Library/Activator",
    "/Library/Flipswitch",
    "/Library/dpkg/",
    "/Library/Frameworks/CydiaSubstrate.framework/",
    "/Library/Frameworks/CydiaSubstrate.framework/Headers/",
    "/Library/Frameworks/CydiaSubstrate.framework/Headers/CydiaSubstrate.h",
    "/Library/Frameworks/CydiaSubstrate.framework/Info.plist",
    "/Library/LaunchDaemons/ai.akemi.asu_inject.plist",
    "/Library/LaunchDaemons/com.openssh.sshd.plist",
    "/Library/LaunchDaemons/com.rpetrich.rocketbootstrapd.plist",
    "/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist",
    "/Library/LaunchDaemons/com.tigisoftware.filza.helper.plist",
    "/Library/LaunchDaemons/dhpdaemon.plist",
    "/Library/LaunchDaemons/re.frida.server.plist",
    "/Library/MobileSubstrate/DynamicLibraries/Choicy.plist",
    "/var/jb/",
    "/etc/passwd",
    "libinjector.dylib",
    // Paths from your previous list (duplicates removed)
    "/var/jb/usr/lib/sandyd_global.plist",
    "/var/jb/Library/PreferenceBundles/checkl0cksettings.bundle/Root.strings",
    "/Applications/checkl0ck.app",
    "/Applications/Snoop-itConfig.app",
    "/Applications/IntelliScreenX.app",
    "/Applications/MewSeek.app",
    "/Applications/OmniStat.app",
    "/Applications/Poof.app",
    "/Applications/Activator.app",
    "/Applications/checkra1n.app",
    "/var/checkra1n.dmg",
    "/Library/MobileSubstrate/DynamicLibraries/Activator.dylib",
    "/System/Library/Caches/apticket.der",
    "/usr/lib/ABDYLD.dylib",
    "/usr/lib/ABSubLoader.dylib",
    "/jb/offsets.plist",
    "/var/lib/dpkg/info/mobilesubstrate.md5sums",
    "/private/var/Users/",
    "/Applications/Sileo.app",
    "/var/binpack",
    "/Library/PreferenceBundles/LibertyPref.bundle",
    "/Library/PreferenceBundles/ShadowPreferences.bundle",
    "/Library/PreferenceBundles/ABypassPrefs.bundle",
    "/Library/PreferenceBundles/FlyJBPrefs.bundle",
    "/Library/PreferenceBundles/Cephei.bundle",
    "/Library/PreferenceBundles/SubstitutePrefs.bundle",
    "/Library/PreferenceBundles/libhbangprefs.bundle",
    "/usr/lib/TweakInject",
    "/var/binpack/Applications/loader.app",
    "/Applications/FlyJB.app",
    "/Applications/Zebra.app",
    "/Library/BawAppie/ABypass",
    "/Library/MobileSubstrate/DynamicLibraries/SSLKillSwitch2.plist",
    "/Library/MobileSubstrate/DynamicLibraries/PreferenceLoader.plist",
    "/Library/MobileSubstrate/DynamicLibraries",
    "/var/mobile/Library/Preferences/me.jjolano.shadow.plist",
    "/var/jb/usr/lib/TweakInject/iGameGodLoader.dylib",
    // New unique paths from the fopen log
    "/var/mobile/Library/Preferences/ABPattern",
    "/.bootstrapped_electra",
    "/.cydia_no_stash",
    "/.installed_unc0ver",
    "/usr/share/jailbreak/injectme.plist",
    "/etc/apt/undecimus/undecimus.list",
    "/jb/amfid_payload.dylib",
    "/jb/jailbreakd.plist",
    "/jb/libjailbreak.dylib",
    "/jb/lzma",
    "/private/var/cache/apt/",
    "/private/var/tmp/cydia.log",
    "/usr/lib/libjailbreak.dylib",
    "/usr/libexec/cydia/firmware.sh",
    "/var/jb/usr/lib/TweakInject/iGameGodLoader.plist",
    "/var/mobile/Library/iGameGod/sp_settings.plist",
    "/var/jb/usr/lib/TweakInject/iGSpoof.dylib",
    "/private/preboot/153531C24E58830CEBDEEDD0DE11598185D136C555DB604D38FF248EE67B07DF853620902F0C68AB50B9197CAD0FD270/jb-aS12k17g/procursus/Library/PreferenceBundles/checkl0cksettings.bundle",
    "/var/jb/Library/PreferenceBundles/checkl0cksettings.bundle/Root.plist",
    "/var/jb/usr/lib/TweakInject/iGSpoof.plist",
    "/var/jb/usr/lib/TweakInject/checkl0ck_managed_conf.dylib",
    "/var/jb/Library/PreferenceBundles/checkl0cksettings.bundle/my_tweaks.plist",
    "/var/jb/usr/lib/TweakInject/checkl0ck.plist",
    "/var/jb/usr/lib/TweakInject/checkl0ck.dylib",
    "/var/jb/usr/lib/TweakInject/bfdecrypttweak.dylib",
    "/private/preboot/153531C24E58830CEBDEEDD0DE11598185D136C555DB604D38FF248EE67B07DF853620902F0C68AB50B9197CAD0FD270/jb-aS12k17g/procursus/Library/Frameworks/AltList.framework/AltList",
    "/private/preboot/153531C24E58830CEBDEEDD0DE11598185D136C555DB604D38FF248EE67B07DF853620902F0C68AB50B9197CAD0FD270/jb-aS12k17g/procursus/Library/Frameworks/AltList.framework/Info.plist",
    "/private/preboot/153531C24E58830CEBDEEDD0DE11598185D136C555DB604D38FF248EE67B07DF853620902F0C68AB50B9197CAD0FD270/jb-aS12k17g/procursus/Library/Frameworks/AltList.framework",
    "/private/preboot/153531C24E58830CEBDEEDD0DE11598185D136C555DB604D38FF248EE67B07DF853620902F0C68AB50B9197CAD0FD270/jb-aS12k17g/procursus/Library/Frameworks/Modulous.framework/Modulous",
    "/var/jb/var/mobile/Library/Preferences/alias20.bfdecryptor.plis",
    "/var/jb/usr/lib/TweakInject/bfdecryptor.dylib",
    "/var/jb/var/mobile/Library/Preferences/com.level3tjg.bfdecrypt.plist",
    "/var/jb/usr/lib/TweakInject/bfdecryptor.plist",
    "/var/jb/usr/lib/TweakInject/bfdecrypt.dylib",
    "/var/jb/usr/lib/TweakInject/bfdecrypt.plist",
    "/var/jb/usr/lib/TweakLoader.dylib",
    "/var/jb/usr/lib/TweakInject/AppSyncUnified-FrontBoard.dylib",
    "/var/jb/usr/lib/TweakInject/SSLKillSwitch3.dylib",
    "/var/jb/usr/lib/TweakInject/Shadow.dylib"
];


//App URL list in lower case for canOpenURL
const canOpenURL = [
    "cydia", "sileo", "undecimus", "zbra", "filza", "activator"
]

setTimeout(function() {
if (ObjC.available) {
    try {
        var f = Module.findExportByName("libSystem.B.dylib", "stat64");
        Interceptor.attach(f, {
            onEnter: function(args) {
                this.is_common_path = false;
                var arg = Memory.readUtf8String(args[0]);
                for (var path in jailbreakPaths) {
                    if (arg.indexOf(jailbreakPaths[path]) > -1) {
                        console.log("Hooking native function stat64: " + arg);
                        this.is_common_path = true;
                        //return -1;
                    }
                }
            },
            onLeave: function(retval) {
                if (this.is_common_path) {
                    console.log("stat64 Bypass!!!");
                    retval.replace(-1);
                }
            }
        });
        var f = Module.findExportByName("libSystem.B.dylib", "stat");
        Interceptor.attach(f, {
            onEnter: function(args) {
                this.is_common_path = false;
                var arg = Memory.readUtf8String(args[0]);
                for (var path in jailbreakPaths) {
                    if (arg.indexOf(jailbreakPaths[path]) > -1) {
                        console.log("Hooking native function stat: " + arg);
                        this.is_common_path = true;
                        //return -1;
                    }
                }
            },
            onLeave: function(retval) {
                if (this.is_common_path) {
                    console.log("stat Bypass!!!");
                    retval.replace(-1);
                }
            }});

        send("Attached")
        // Hooking fileExistsAtPath:
        Interceptor.attach(ObjC.classes.NSFileManager["- fileExistsAtPath:"].implementation, {
            onEnter(args) {
                // Use a marker to check onExit if we need to manipulate
                // the response.
                this.is_common_path = false;
                // Extract the path
                this.path = new ObjC.Object(args[2]).toString();
                // check if the looked up path is in the list of common_paths
                if (jailbreakPaths.indexOf(this.path) >= 0) {
                    // Mark this path as one that should have its response
                    // modified if needed.
                    this.is_common_path = true;
                }
            },
            onLeave(retval) {
                // stop if we dont care about the path
                if (!this.is_common_path) {
                    return;
                }

                // ignore failed lookups
                if (retval.isNull()) {
                    send(`fileExistsAtPath: try to check for ` + this.path + ' was failed');
                    return;
                }
                send(`fileExistsAtPath: check for ` + this.path + ` was successful with: ` + retval.toString() + `, marking it as failed.`);
                retval.replace(new NativePointer(0x00));
            },
        });

        //Hooking fopen
        Interceptor.attach(Module.findExportByName(null, "fopen"), {
            onEnter(args) {
                this.is_common_path = false;
                // Extract the path
                this.path = args[0].readCString();
                // check if the looked up path is in the list of common_paths
                if (jailbreakPaths.indexOf(this.path) >= 0) {
                    // Mark this path as one that should have its response
                    // modified if needed.
                    this.is_common_path = true;
                }
            },
            onLeave(retval) {
                // stop if we dont care about the path
                if (!this.is_common_path) {
                    return;
                }

                // ignore failed lookups
                if (retval.isNull()) {
                    send(`fopen: try to check for ` + this.path + ' was failed');
                    return;
                }
                send(`fopen: check for ` + this.path + ` was successful with: ` + retval.toString() + `, marking it as failed.`);
                retval.replace(new NativePointer(0x00));
            },
        });

        //Hooking fopen
        Interceptor.attach(Module.findExportByName(null, "getfsstat64"), {
            onEnter(args) {
            },
            onLeave(retval) {
                // stop if we dont care about the path
                if (!this.is_common_path) {
                    return;
                }

                // ignore failed lookups
                if (retval.isNull()) {
                    send(`getfsstat64: try to check for ` + this.path + ' was failed');
                    return;
                }
                send(`getffstat64: check for ` + this.path + ` was successful with: ` + retval.toString() + `, marking it as failed.`);
                retval.replace(new NativePointer(0x00));
            },
        });

        //Hooking canOpenURL for Cydia
        Interceptor.attach(ObjC.classes.UIApplication["- canOpenURL:"].implementation, {
            onEnter(args) {
                this.is_flagged = false;
                // Extract the path
                this.path = new ObjC.Object(args[2]).toString();
                let app = this.path.split(":")[0].toLowerCase();
                if (canOpenURL.indexOf(app) >= 0) {
                    this.is_flagged = true;
                }
            },
            onLeave(retval) {
                if (!this.is_flagged) {
                    return;
                }

                // ignore failed
                if (retval.isNull()) {
                    return;
                }
                send(`canOpenURL: check for ` +
                    this.path + ` was successful with: ` +
                    retval.toString() + `, marking it as failed.`);
                retval.replace(new NativePointer(0x00));
            }
        });

        //Hooking libSystemBFork
        const libSystemBdylibFork = Module.findExportByName("libSystem.B.dylib", "fork");
        if (libSystemBdylibFork) {
            Interceptor.attach(libSystemBdylibFork, {
                onLeave(retval) {
                    // already failed forks are ok
                    if (retval.isNull()) {
                        return;
                    }
                    send(`Call to libSystem.B.dylib::fork() was successful with ` +
                    retval.toString() + ` marking it as failed.`);
                    retval.replace(new NativePointer(0x0));
                },
            });
        }

        const ptrStrStr = Module.findExportByName(null, 'strstr');
        Interceptor.attach(ptrStrStr, {
            onEnter: function(args) {
                let index = tpLibs.length;
                this.libIsTampared = false;
                while (index--) {
                    var lib = args[1].readUtf8String();
                    if (lib == tpLibs[index]) {
                        console.log("[*] strstr called: " + lib + " overwrite return");
                        this.libIsTampared = true;
                    }
                }
            },
            onLeave: function(retval) {
                if (this.libIsTampared) {
                    retval.replace(0x00);
                }
            }
        });
    }
    catch (err) {
        send("Exception : " + err.message);
    }
}
else {
    send("Objective-C Runtime is not available!");
}
}, 2);

