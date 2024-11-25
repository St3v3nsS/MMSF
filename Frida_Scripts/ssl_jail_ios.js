//Path list for fileExistsAtPath and fopen
const jailbreakPaths = [
    "/Applications/Cydia.app",
    "/Applications/FakeCarrier.app",
    "/Applications/Icy.app",
    "/Applications/IntelliScreen.app",
    "/Applications/MxTube.app",
    "/Applications/RockApp.app",
    "/Applications/SBSetttings.app",
    "/Applications/WinterBoard.app",
    "/Applications/blackra1n.app",
    "/Applications/Terminal.app",
    "/Applications/Pirni.app",
    "/Applications/iFile.app",
    "/Applications/iProtect.app",
    "/Applications/Backgrounder.app",
    "/Applications/biteSMS.app",
    "/Library/MobileSubstrate/DynamicLibraries/LiveClock.plist",
    "/Library/MobileSubstrate/DynamicLibraries/Veency.plist",
    "/Library/MobileSubstrate/DynamicLibraries/SBSettings.dylib",
    "/Library/MobileSubstrate/DynamicLibraries/SBSettings.plist",
    "/Library/MobileSubstrate/MobileSubstrate.dylib",
    "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
    "/System/Library/LaunchDaemons/com.saurik.Cy@dia.Startup.plist",
    "/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist",
    "/System/Library/LaunchDaemons/com.bigboss.sbsettingsd.plist",
    "/System/Library/PreferenceBundles/CydiaSettings.bundle",
    "/bin/bash",
    "/bin/sh",
    "/etc/apt",
    "/etc/ssh/sshd_config",
    "/etc/profile.d/terminal.sh",
    "/private/var/stash",
    "/private/var/tmp/cydia.log",
    "/private/var/lib/apt",
    "/private/var/root/Media/Cydia",
    "/private/var/lib/cydia",
    "/private/var/mobile/Library/SBSettings/Themes",
    "/private/var/lib/dpkg/info/cydia-sources.list",
    "/private/var/lib/dpkg/info/cydia.list",
    "/private/etc/profile.d/terminal.sh",
    "/usr/lib/libsubstitute.dylib",
    "/usr/lib/substrate",
    "/usr/lib/libhooker.dylib",
    "/usr/bin/cycript",
    "/usr/bin/ssh",
    "/usr/bin/sshd",
    "/usr/sbin/sshd",
    "/usr/libexec/sftp-server",
    "/usr/libexec/ssh-keysign",
    "/usr/libexec/cydia",
    "/usr/sbin/sshd",
    "/var/cache/apt",
    "/var/lib/cydia",
    "/var/log/syslog",
    "/var/tmp/cydia.log",
    "/var/lib/dpkg/info/cydia-sources.list",
    "/var/lib/dpkg/info/cydia.list",
    "/var/lib/dpkg/info/mobileterminal.list",
    "/var/lib/dpkg/info/mobileterminal.postinst",
    "/User/Library/SBSettings",
    "/usr/bin/sbsettingsd",
    "/var/mobile/Library/SBSettings",
    "/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitFishhookModule.bundle",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitFishhookModule.bundle",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitFishhookModule.bundle",
    "/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitSubstrateModule.bundle",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitSubstrateModule.bundle",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitSubstrateModule.bundle",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitSubstrateModule.bundle/HookKitSubstrateModule",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Modulous/HookKit/HookKitFishhookModule.bundle/HookKitFishhookModule",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/usr/lib/TweakInject/Choicy.dylib",
    "/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64",
    "/var/jb/var/mobile/Library/Preferences/com.level3tjg.bfdecrypt.plist",
    "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Frameworks/Shadow.framework",
   "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Frameworks/HookKit.framework",
  "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Frameworks/RootBridge.framework",
  "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/Library/Frameworks/Modulous.framework",
  "/var/mobile/Library/iGameGod/config.plist",
  "/var/jb",
  "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/var/mobile",
  "/var/jb/var/mobile/Library/iGameGod/config.plist",
  "/var/jb/usr/lib/sandyd_global.plist",
  "/var/jb/var/mobile/Library/iGameGod/sp_settings.plist",
  "/var/jb//var/mobile/Library/iGameGod/config.plist",
  "/var/jb//Library/Frameworks",
  "/var/jb//var/jb//Library/Frameworks/iGameGod.framework",
  "/var/jb//Library/Frameworks/iGameGod.framework",
  "/var/mobile/Library/iGameGod/bfdecrypt_queue",
  "/Applications/Sileo.app",
  "/Applications/AppValley.app",
  "/Applications/Emus4U.app",
  "/Applications/TutuApp.app",
  "/Applications/TweakBox.app",
  "/Applications/CokerNutX.app",
  "/Applications/iOSEmus.app",
  "/Applications/AppCake.app",
  "/Applications/iPA4iOS.app",
  "/Applications/Aptoide.app",
  "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/usr/lib/TweakInject/   Choicy.dylib",
  "/private/var/containers/Bundle/Application/40CB84E4-F958-457F-ACC4-6CDB444D5FA7/Marygold&Co..app/Frameworks/ZDetection.framework",
  "/private/var/containers/Bundle/Application/40CB84E4-F958-457F-ACC4-6CDB444D5FA7/Marygold&Co..app/Frameworks/MobileIntelligence.framework",
  "/private/preboot/CF3B81CA2803A4CA1CDD2279E4DADEBCA897370A/jb-acpLPvTI/procursus/var/mobile",
  "/var/mobile/Containers/Data/Application/C21F23E5-AF3F-4AD9-9EFD-A5224C584486/"
];

//App URL list in lower case for canOpenURL
const canOpenURL = [
    "cydia", "sileo"
]

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
        // var f = Module.findExportByName("libSystem.B.dylib", "stat");
        // Interceptor.attach(f, {
        //     onEnter: function(args) {
        //         this.is_common_path = false;
        //         var arg = Memory.readUtf8String(args[0]);
        //         for (var path in jailbreakPaths) {
        //             if (arg.indexOf(jailbreakPaths[path]) > -1) {
        //                 console.log("Hooking native function stat: " + arg);
        //                 this.is_common_path = true;
        //                 //return -1;
        //             }
        //         }
        //     },
        //     onLeave: function(retval) {
        //         if (this.is_common_path) {
        //             console.log("stat Bypass!!!");
        //             retval.replace(-1);
        //         }
        //     }});

        send("Attached")
        // Hooking fileExistsAtPath:
        // Interceptor.attach(ObjC.classes.NSFileManager["- fileExistsAtPath:"].implementation, {
        //     onEnter(args) {
        //         // Use a marker to check onExit if we need to manipulate
        //         // the response.
        //         this.is_common_path = false;
        //         // Extract the path
        //         this.path = new ObjC.Object(args[2]).toString();
        //         // check if the looked up path is in the list of common_paths
        //         if (jailbreakPaths.indexOf(this.path) >= 0) {
        //             // Mark this path as one that should have its response
        //             // modified if needed.
        //             this.is_common_path = true;
        //         }
        //     },
        //     onLeave(retval) {
        //         // stop if we dont care about the path
        //         if (!this.is_common_path) {
        //             return;
        //         }

        //         // ignore failed lookups
        //         if (retval.isNull()) {
        //             send(`fileExistsAtPath: try to check for ` + this.path + ' was failed');
        //             return;
        //         }
        //         send(`fileExistsAtPath: check for ` + this.path + ` was successful with: ` + retval.toString() + `, marking it as failed.`);
        //         retval.replace(new NativePointer(0x00));
        //     },
        // });

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
    }
    catch (err) {
        send("Exception : " + err.message);
    }
}
else {
    send("Objective-C Runtime is not available!");
}

/* Description: iOS 13 SSL Bypass based on https://codeshare.frida.re/@machoreverser/ios12-ssl-bypass/ and https://github.com/nabla-c0d3/ssl-kill-switch2
 *  Author: 	@apps3c
 */

try {
	Module.ensureInitialized("libboringssl.dylib");
} catch(err) {
	console.log("libboringssl.dylib module not loaded. Trying to manually load it.")
	Module.load("libboringssl.dylib");	
}

var SSL_VERIFY_NONE = 0;
var ssl_set_custom_verify;
var ssl_get_psk_identity;	

ssl_set_custom_verify = new NativeFunction(
	Module.findExportByName("libboringssl.dylib", "SSL_set_custom_verify"),
	'void', ['pointer', 'int', 'pointer']
);

/* Create SSL_get_psk_identity NativeFunction 
* Function signature https://commondatastorage.googleapis.com/chromium-boringssl-docs/ssl.h.html#SSL_get_psk_identity
*/
ssl_get_psk_identity = new NativeFunction(
	Module.findExportByName("libboringssl.dylib", "SSL_get_psk_identity"),
	'pointer', ['pointer']
);

/** Custom callback passed to SSL_CTX_set_custom_verify */
function custom_verify_callback_that_does_not_validate(ssl, out_alert){
	return SSL_VERIFY_NONE;
}

/** Wrap callback in NativeCallback for frida */
var ssl_verify_result_t = new NativeCallback(function (ssl, out_alert){
	custom_verify_callback_that_does_not_validate(ssl, out_alert);
},'int',['pointer','pointer']);

Interceptor.replace(ssl_set_custom_verify, new NativeCallback(function(ssl, mode, callback) {
	//  |callback| performs the certificate verification. Replace this with our custom callback
	ssl_set_custom_verify(ssl, mode, ssl_verify_result_t);
}, 'void', ['pointer', 'int', 'pointer']));

Interceptor.replace(ssl_get_psk_identity, new NativeCallback(function(ssl) {
	return "notarealPSKidentity";
}, 'pointer', ['pointer']));
	
console.log("[+] Bypass successfully loaded ");	