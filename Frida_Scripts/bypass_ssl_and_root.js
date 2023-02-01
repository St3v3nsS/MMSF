
Java.perform(function() {

    console.log("[*] Hooking calls to System.exit");
    var exitClass = Java.use("java.lang.System");
    exitClass.exit.implementation = function(){
        console.log("[*] System.exit called");
    }

    var RootPackages = ["com.noshufou.android.su", "com.noshufou.android.su.elite", "eu.chainfire.supersu",
        "com.koushikdutta.superuser", "com.thirdparty.superuser", "com.yellowes.su", "com.koushikdutta.rommanager",
        "com.koushikdutta.rommanager.license", "com.dimonvideo.luckypatcher", "com.chelpus.lackypatch",
        "com.ramdroid.appquarantine", "com.ramdroid.appquarantinepro", "com.devadvance.rootcloak", "com.devadvance.rootcloakplus",
        "de.robv.android.xposed.installer", "com.saurik.substrate", "com.zachspong.temprootremovejb", "com.amphoras.hidemyroot",
        "com.amphoras.hidemyrootadfree", "com.formyhm.hiderootPremium", "com.formyhm.hideroot", "me.phh.superuser",
        "eu.chainfire.supersu.pro", "com.kingouser.com", "com.topjohnwu.magisk"
    ];

    var RootBinaries = ["su", "busybox", "supersu", "Superuser.apk", "KingoUser.apk", "SuperSu.apk", "magisk"];

    var RootProperties = {
        "ro.build.selinux": "1",
        "ro.debuggable": "0",
        "service.adb.root": "0",
        "ro.secure": "1"
    };

    var RootPropertiesKeys = [];

    for (var k in RootProperties) RootPropertiesKeys.push(k);

    var PackageManager = Java.use("android.app.ApplicationPackageManager");

    var Runtime = Java.use('java.lang.Runtime');

    var NativeFile = Java.use('java.io.File');

    var String = Java.use('java.lang.String');

    var SystemProperties = Java.use('android.os.SystemProperties');

    var BufferedReader = Java.use('java.io.BufferedReader');

    var ProcessBuilder = Java.use('java.lang.ProcessBuilder');

    var StringBuffer = Java.use('java.lang.StringBuffer');

    var loaded_classes = Java.enumerateLoadedClassesSync();

    send("Loaded " + loaded_classes.length + " classes!");

    var useKeyInfo = false;

    var useProcessManager = false;

    send("loaded: " + loaded_classes.indexOf('java.lang.ProcessManager'));

    if (loaded_classes.indexOf('java.lang.ProcessManager') != -1) {
        try {
            //useProcessManager = true;
            //var ProcessManager = Java.use('java.lang.ProcessManager');
        } catch (err) {
            send("ProcessManager Hook failed: " + err);
        }
    } else {
        send("ProcessManager hook not loaded");
    }

    var KeyInfo = null;

    if (loaded_classes.indexOf('android.security.keystore.KeyInfo') != -1) {
        try {
            //useKeyInfo = true;
            //var KeyInfo = Java.use('android.security.keystore.KeyInfo');
        } catch (err) {
            send("KeyInfo Hook failed: " + err);
        }
    } else {
        send("KeyInfo hook not loaded");
    }

    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pname, flags) {
        var shouldFakePackage = (RootPackages.indexOf(pname) > -1);
        if (shouldFakePackage) {
            send("Bypass root check for package: " + pname);
            pname = "set.package.name.to.a.fake.one.so.we.can.bypass.it";
        }
        return this.getPackageInfo.overload('java.lang.String', 'int').call(this, pname, flags);
    };

    NativeFile.exists.implementation = function() {
        var name = NativeFile.getName.call(this);
        var shouldFakeReturn = (RootBinaries.indexOf(name) > -1);
        if (shouldFakeReturn) {
            send("Bypass return value for binary: " + name);
            return false;
        } else {
            return this.exists.call(this);
        }
    };

    var exec = Runtime.exec.overload('[Ljava.lang.String;');
    var exec1 = Runtime.exec.overload('java.lang.String');
    var exec2 = Runtime.exec.overload('java.lang.String', '[Ljava.lang.String;');
    var exec3 = Runtime.exec.overload('[Ljava.lang.String;', '[Ljava.lang.String;');
    var exec4 = Runtime.exec.overload('[Ljava.lang.String;', '[Ljava.lang.String;', 'java.io.File');
    var exec5 = Runtime.exec.overload('java.lang.String', '[Ljava.lang.String;', 'java.io.File');

    exec5.implementation = function(cmd, env, dir) {
        if (cmd.indexOf("getprop") != -1 || cmd == "mount" || cmd.indexOf("build.prop") != -1 || cmd == "id" || cmd == "sh") {
            var fakeCmd = "grep";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        if (cmd == "su") {
            var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        return exec5.call(this, cmd, env, dir);
    };

    exec4.implementation = function(cmdarr, env, file) {
        for (var i = 0; i < cmdarr.length; i = i + 1) {
            var tmp_cmd = cmdarr[i];
            if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd == "mount" || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd == "id" || tmp_cmd == "sh") {
                var fakeCmd = "grep";
                send("Bypass " + cmdarr + " command");
                return exec1.call(this, fakeCmd);
            }

            if (tmp_cmd == "su") {
                var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
                send("Bypass " + cmdarr + " command");
                return exec1.call(this, fakeCmd);
            }
        }
        return exec4.call(this, cmdarr, env, file);
    };

    exec3.implementation = function(cmdarr, envp) {
        for (var i = 0; i < cmdarr.length; i = i + 1) {
            var tmp_cmd = cmdarr[i];
            if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd == "mount" || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd == "id" || tmp_cmd == "sh") {
                var fakeCmd = "grep";
                send("Bypass " + cmdarr + " command");
                return exec1.call(this, fakeCmd);
            }

            if (tmp_cmd == "su") {
                var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
                send("Bypass " + cmdarr + " command");
                return exec1.call(this, fakeCmd);
            }
        }
        return exec3.call(this, cmdarr, envp);
    };

    exec2.implementation = function(cmd, env) {
        if (cmd.indexOf("getprop") != -1 || cmd == "mount" || cmd.indexOf("build.prop") != -1 || cmd == "id" || cmd == "sh") {
            var fakeCmd = "grep";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        if (cmd == "su") {
            var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        return exec2.call(this, cmd, env);
    };

    exec.implementation = function(cmd) {
        for (var i = 0; i < cmd.length; i = i + 1) {
            var tmp_cmd = cmd[i];
            if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd == "mount" || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd == "id" || tmp_cmd == "sh") {
                var fakeCmd = "grep";
                send("Bypass " + cmd + " command");
                return exec1.call(this, fakeCmd);
            }

            if (tmp_cmd == "su") {
                var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
                send("Bypass " + cmd + " command");
                return exec1.call(this, fakeCmd);
            }
        }

        return exec.call(this, cmd);
    };

    exec1.implementation = function(cmd) {
        if (cmd.indexOf("getprop") != -1 || cmd == "mount" || cmd.indexOf("build.prop") != -1 || cmd == "id" || cmd == "sh") {
            var fakeCmd = "grep";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        if (cmd == "su") {
            var fakeCmd = "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled";
            send("Bypass " + cmd + " command");
            return exec1.call(this, fakeCmd);
        }
        return exec1.call(this, cmd);
    };

    String.contains.implementation = function(name) {
        if (name == "test-keys") {
            send("Bypass test-keys check");
            return false;
        }
        return this.contains.call(this, name);
    };

    var get = SystemProperties.get.overload('java.lang.String');

    get.implementation = function(name) {
        if (RootPropertiesKeys.indexOf(name) != -1) {
            send("Bypass " + name);
            return RootProperties[name];
        }
        return this.get.call(this, name);
    };

    Interceptor.attach(Module.findExportByName("libc.so", "fopen"), {
        onEnter: function(args) {
            var path = Memory.readCString(args[0]);
            path = path.split("/");
            var executable = path[path.length - 1];
            var shouldFakeReturn = (RootBinaries.indexOf(executable) > -1)
            if (shouldFakeReturn) {
                Memory.writeUtf8String(args[0], "/notexists");
                send("Bypass native fopen");
            }
        },
        onLeave: function(retval) {

        }
    });

    Interceptor.attach(Module.findExportByName("libc.so", "system"), {
        onEnter: function(args) {
            var cmd = Memory.readCString(args[0]);
            send("SYSTEM CMD: " + cmd);
            if (cmd.indexOf("getprop") != -1 || cmd == "mount" || cmd.indexOf("build.prop") != -1 || cmd == "id") {
                send("Bypass native system: " + cmd);
                Memory.writeUtf8String(args[0], "grep");
            }
            if (cmd == "su") {
                send("Bypass native system: " + cmd);
                Memory.writeUtf8String(args[0], "justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled");
            }
        },
        onLeave: function(retval) {

        }
    });

    BufferedReader.readLine.overload('boolean').implementation = function() {
        var text = this.readLine.overload('boolean').call(this);
        if (text === null) {
            // just pass , i know it's ugly as hell but test != null won't work :(
        } else {
            var shouldFakeRead = (text.indexOf("ro.build.tags=test-keys") > -1);
            if (shouldFakeRead) {
                send("Bypass build.prop file read");
                text = text.replace("ro.build.tags=test-keys", "ro.build.tags=release-keys");
            }
        }
        return text;
    };

    var executeCommand = ProcessBuilder.command.overload('java.util.List');

    ProcessBuilder.start.implementation = function() {
        var cmd = this.command.call(this);
        var shouldModifyCommand = false;
        for (var i = 0; i < cmd.size(); i = i + 1) {
            var tmp_cmd = cmd.get(i).toString();
            if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd.indexOf("mount") != -1 || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd.indexOf("id") != -1) {
                shouldModifyCommand = true;
            }
        }
        if (shouldModifyCommand) {
            send("Bypass ProcessBuilder " + cmd);
            this.command.call(this, ["grep"]);
            return this.start.call(this);
        }
        if (cmd.indexOf("su") != -1) {
            send("Bypass ProcessBuilder " + cmd);
            this.command.call(this, ["justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled"]);
            return this.start.call(this);
        }

        return this.start.call(this);
    };

    if (useProcessManager) {
        var ProcManExec = ProcessManager.exec.overload('[Ljava.lang.String;', '[Ljava.lang.String;', 'java.io.File', 'boolean');
        var ProcManExecVariant = ProcessManager.exec.overload('[Ljava.lang.String;', '[Ljava.lang.String;', 'java.lang.String', 'java.io.FileDescriptor', 'java.io.FileDescriptor', 'java.io.FileDescriptor', 'boolean');

        ProcManExec.implementation = function(cmd, env, workdir, redirectstderr) {
            var fake_cmd = cmd;
            for (var i = 0; i < cmd.length; i = i + 1) {
                var tmp_cmd = cmd[i];
                if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd == "mount" || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd == "id") {
                    var fake_cmd = ["grep"];
                    send("Bypass " + cmdarr + " command");
                }

                if (tmp_cmd == "su") {
                    var fake_cmd = ["justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled"];
                    send("Bypass " + cmdarr + " command");
                }
            }
            return ProcManExec.call(this, fake_cmd, env, workdir, redirectstderr);
        };

        ProcManExecVariant.implementation = function(cmd, env, directory, stdin, stdout, stderr, redirect) {
            var fake_cmd = cmd;
            for (var i = 0; i < cmd.length; i = i + 1) {
                var tmp_cmd = cmd[i];
                if (tmp_cmd.indexOf("getprop") != -1 || tmp_cmd == "mount" || tmp_cmd.indexOf("build.prop") != -1 || tmp_cmd == "id") {
                    var fake_cmd = ["grep"];
                    send("Bypass " + cmdarr + " command");
                }

                if (tmp_cmd == "su") {
                    var fake_cmd = ["justafakecommandthatcannotexistsusingthisshouldthowanexceptionwheneversuiscalled"];
                    send("Bypass " + cmdarr + " command");
                }
            }
            return ProcManExecVariant.call(this, fake_cmd, env, directory, stdin, stdout, stderr, redirect);
        };
    }

    if (useKeyInfo) {
        KeyInfo.isInsideSecureHardware.implementation = function() {
            send("Bypass isInsideSecureHardware");
            return true;
        }
    }
        
});

/*  Android ssl certificate pinning bypass script for various methods
    by Maurizio Siddu
    
    Run with:
    frida -U -f [APP_ID] -l frida_multiple_unpinning.js --no-pause
*/

setTimeout(function() {
    Java.perform(function () {
        console.log('');
        console.log('======');
        console.log('[#] Android Bypass for various Certificate Pinning methods [#]');
        console.log('======');


        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
    
        
        // TrustManager (Android < 7)
        var TrustManager = Java.registerClass({
            // Implement a custom TrustManager
            name: 'dev.asd.test.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function (chain, authType) {},
                checkServerTrusted: function (chain, authType) {},
                getAcceptedIssuers: function () {return []; }
            }
        });
    
        // Prepare the TrustManager array to pass to SSLContext.init()
        var TrustManagers = [TrustManager.$new()];
        // Get a handle on the init() on the SSLContext class
        var SSLContext_init = SSLContext.init.overload(
            '[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom');
        try {
            // Override the init method, specifying the custom TrustManager
            SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
                console.log('[+] Bypassing Trustmanager (Android < 7) request');
                SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
            };
    
        } catch (err) {
            console.log('[-] TrustManager (Android < 7) pinner not found');
            //console.log(err);
        }

     
    
        // OkHTTPv3 (double bypass)
        try {
            var okhttp3_Activity = Java.use('okhttp3.CertificatePinner');
	    okhttp3_Activity.check$okhttp.overload('java.lang.String', 'kotlin.jvm.functions.Function0').implementation= function (str) {
	    	console.log('[+] Bypassing' + str);
		return; 
	    };
            okhttp3_Activity.check.overload('java.lang.String', 'java.util.List').implementation = function (str) {
                console.log('[+] Bypassing OkHTTPv3 {1}: ' + str);
                return true;
            };
            // This method of CertificatePinner.check could be found in some old Android app
            okhttp3_Activity.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (str) {
                console.log('[+] Bypassing OkHTTPv3 {2}: ' + str);
                return true;
            };
	   var app_smali = Java.use('com.app.romcard.App');
	   app_smali.isSSLPinningActive.overload().implementation = function () {
		console.log('dadada');		
		return false;	 
	}
    
        } catch (err) {
            console.log('[-] OkHTTPv3 pinner not found');
            //console.log(err);
        }
	

    
    
        // Trustkit (triple bypass)
        try {
            var trustkit_Activity = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
            trustkit_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str) {
                console.log('[+] Bypassing Trustkit {1}: ' + str);
                return true;
            };
            trustkit_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str) {
                console.log('[+] Bypassing Trustkit {2}: ' + str);
                return true;
            };
            var trustkit_PinningTrustManager = Java.use('com.datatheorem.android.trustkit.pinning.PinningTrustManager');
            trustkit_PinningTrustManager.checkServerTrusted.implementation = function () {
                console.log('[+] Bypassing Trustkit {3}');
            };
    
        } catch (err) {
            console.log('[-] Trustkit pinner not found');
            //console.log(err);
        }
    
    
  
        // TrustManagerImpl (Android > 7)
        try {
            var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
            TrustManagerImpl.verifyChain.implementation = function (untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
                console.log('[+] Bypassing TrustManagerImpl (Android > 7): ' + host);
                return untrustedChain;
            };
            
        } catch (err) {
            console.log('[-] TrustManagerImpl (Android > 7) pinner not found');
            //console.log(err);
        }   
  
  
        
        // Appcelerator Titanium
        try {
            var appcelerator_PinningTrustManager = Java.use('appcelerator.https.PinningTrustManager');
            appcelerator_PinningTrustManager.checkServerTrusted.implementation = function () {
                console.log('[+] Bypassing Appcelerator PinningTrustManager');
            };

        } catch (err) {
            console.log('[-] Appcelerator PinningTrustManager pinner not found');
            //console.log(err);
        }



        // OpenSSLSocketImpl Conscrypt
        try {
            var OpenSSLSocketImpl = Java.use('com.android.org.conscrypt.OpenSSLSocketImpl');
            OpenSSLSocketImpl.verifyCertificateChain.implementation = function (certRefs, JavaObject, authMethod) {
                console.log('[+] Bypassing OpenSSLSocketImpl Conscrypt');
            };
        
        } catch (err) {
            console.log('[-] OpenSSLSocketImpl Conscrypt pinner not found');
            //console.log(err);        
        }


        // OpenSSLEngineSocketImpl Conscrypt
        try {
            var OpenSSLEngineSocketImpl_Activity = Java.use('com.android.org.conscrypt.OpenSSLEngineSocketImpl');
            OpenSSLSocketImpl_Activity.verifyCertificateChain.overload('[Ljava.lang.Long;', 'java.lang.String').implementation = function (str1, str2) {
                console.log('[+] Bypassing OpenSSLEngineSocketImpl Conscrypt: ' + str2);
            };
        
        } catch (err) {
            console.log('[-] OpenSSLEngineSocketImpl Conscrypt pinner not found');
            //console.log(err);
        }



        // OpenSSLSocketImpl Apache Harmony
        try {
            var OpenSSLSocketImpl_Harmony = Java.use('org.apache.harmony.xnet.provider.jsse.OpenSSLSocketImpl');
            OpenSSLSocketImpl_Harmony.verifyCertificateChain.implementation = function (asn1DerEncodedCertificateChain, authMethod) {
                console.log('[+] Bypassing OpenSSLSocketImpl Apache Harmony');
            };

        } catch (err) {
            console.log('[-] OpenSSLSocketImpl Apache Harmony pinner not found');
            //console.log(err);      
        }



        // PhoneGap sslCertificateChecker (https://github.com/EddyVerbruggen/SSLCertificateChecker-PhoneGap-Plugin)
        try {
            var phonegap_Activity = Java.use('nl.xservices.plugins.sslCertificateChecker');
            phonegap_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (str) {
                console.log('[+] Bypassing PhoneGap sslCertificateChecker: ' + str);
                return true;
            };
    
        } catch (err) {
            console.log('[-] PhoneGap sslCertificateChecker pinner not found');
            //console.log(err);
        }



        // IBM MobileFirst pinTrustedCertificatePublicKey (double bypass)
        try {
            var WLClient_Activity = Java.use('com.worklight.wlclient.api.WLClient');
            WLClient_Activity.getInstance().pinTrustedCertificatePublicKey.overload('java.lang.String').implementation = function (cert) {
                console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {1}: ' + cert);
                return;
            };
            WLClient_Activity.getInstance().pinTrustedCertificatePublicKey.overload('[Ljava.lang.String;').implementation = function (cert) {
                console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {2}: ' + cert);
                return;
            };

        } catch (err) {
            console.log('[-] IBM MobileFirst pinTrustedCertificatePublicKey pinner not found');
            //console.log(err);
        }



        // IBM WorkLight (ancestor of MobileFirst) HostNameVerifierWithCertificatePinning (quadruple bypass)
        try {
            var worklight_Activity = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
            worklight_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSocket').implementation = function (str) {
                console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {1}: ' + str);                
                return;
            };
            worklight_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str) {
                console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {2}: ' + str);
                return;
            };
            worklight_Activity.verify.overload('java.lang.String', '[Ljava.lang.String;', '[Ljava.lang.String;').implementation = function (str) {
                console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {3}: ' + str);
                return;
            };
            worklight_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str) {
                console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {4}: ' + str);
                return true;
            };

        } catch (err) {
            console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning pinner not found');
            //console.log(err);
        }



        // Conscrypt CertPinManager
        try {
            var conscrypt_CertPinManager_Activity = Java.use('com.android.org.conscrypt.CertPinManager');
            conscrypt_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (str) {
                console.log('[+] Bypassing Conscrypt CertPinManager: ' + str);
                return true;
            };
    
        } catch (err) {
            console.log('[-] Conscrypt CertPinManager pinner not found');
            //console.log(err);
        }



        // CWAC-Netsecurity (unofficial back-port pinner for Android < 4.2) CertPinManager
        try {
            var cwac_CertPinManager_Activity = Java.use('com.commonsware.cwac.netsecurity.conscrypt.CertPinManager');
            cwac_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (str) {
                console.log('[+] Bypassing CWAC-Netsecurity CertPinManager: ' + str);
                return true;
            };
    
        } catch (err) {
            console.log('[-] CWAC-Netsecurity CertPinManager pinner not found');
            //console.log(err);
        }



        // Worklight Androidgap WLCertificatePinningPlugin
        try {
            var androidgap_WLCertificatePinningPlugin_Activity = Java.use('com.worklight.androidgap.plugin.WLCertificatePinningPlugin');
            androidgap_WLCertificatePinningPlugin_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (str) {
                console.log('[+] Bypassing Worklight Androidgap WLCertificatePinningPlugin: ' + str);
                return true;
            };
    
        } catch (err) {
            console.log('[-] Worklight Androidgap WLCertificatePinningPlugin pinner not found');
            //console.log(err);
        }



        // Netty FingerprintTrustManagerFactory
        try {
            var netty_FingerprintTrustManagerFactory = Java.use('io.netty.handler.ssl.util.FingerprintTrustManagerFactory');
            //NOTE: sometimes this below implementation could be useful 
            //var netty_FingerprintTrustManagerFactory = Java.use('org.jboss.netty.handler.ssl.util.FingerprintTrustManagerFactory');
            netty_FingerprintTrustManagerFactory.checkTrusted.implementation = function (type, chain) {
                console.log('[+] Bypassing Netty FingerprintTrustManagerFactory');
            };

        } catch (err) {
            console.log('[-] Netty FingerprintTrustManagerFactory pinner not found');
            //console.log(err);
        }



        // Squareup CertificatePinner [OkHTTP < v3] (double bypass)
        try {
            var Squareup_CertificatePinner_Activity = Java.use('com.squareup.okhttp.CertificatePinner');
            Squareup_CertificatePinner_Activity.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (str1, str2) {
                console.log('[+] Bypassing Squareup CertificatePinner {1}: ' + str1);
                return;
            };

            Squareup_CertificatePinner_Activity.check.overload('java.lang.String', 'java.util.List').implementation = function (str1, str2) {
                console.log('[+] Bypassing Squareup CertificatePinner {2}: ' + str1);
                return;
            };
        
        } catch (err) {
            console.log('[-] Squareup CertificatePinner pinner not found');
            //console.log(err);
        }



        // Squareup OkHostnameVerifier [OkHTTP v3] (double bypass)
        try {
            var Squareup_OkHostnameVerifier_Activity = Java.use('com.squareup.okhttp.internal.tls.OkHostnameVerifier');
            Squareup_OkHostnameVerifier_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str1, str2) {
                console.log('[+] Bypassing Squareup OkHostnameVerifier {1}: ' + str1);
                return true;
            };
            
            Squareup_OkHostnameVerifier_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str1, str2) {
                console.log('[+] Bypassing Squareup OkHostnameVerifier {2}: ' + str1);
                return true;
            };
            
        } catch (err) {
            console.log('[-] Squareup OkHostnameVerifier pinner not found');
            //console.log(err);
        }


        
        // Android WebViewClient
        try {
            var AndroidWebViewClient_Activity = Java.use('android.webkit.WebViewClient');
            AndroidWebViewClient_Activity.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
                console.log('[+] Bypassing Android WebViewClient');
            };
            
        } catch (err) {
            console.log('[-] Android WebViewClient pinner not found');
            //console.log(err);
        }



        // Apache Cordova WebViewClient
        try {
            var CordovaWebViewClient_Activity = Java.use('org.apache.cordova.CordovaWebViewClient');
            CordovaWebViewClient_Activity.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
                console.log('[+] Bypassing Apache Cordova WebViewClient');
                obj3.proceed();
            };
            
        } catch (err) {
            console.log('[-] Apache Cordova WebViewClient pinner not found');
            //console.log(err):
        }



        // Boye AbstractVerifier
        try {
            var boye_AbstractVerifier = Java.use('ch.boye.httpclientandroidlib.conn.ssl.AbstractVerifier');
            boye_AbstractVerifier.verify.implementation = function (host, ssl) {
                console.log('[+] Bypassing Boye AbstractVerifier: ' + host);
            };
            
        } catch (err) {
            console.log('[-] Boye AbstractVerifier pinner not found');
            //console.log(err):
        }

     
    });
    
}, 0);
