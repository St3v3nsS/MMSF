if (!ObjC.available) {
  console.log("ObjC not available");
} else {
  console.log("[*] Starting RN biometric trace");
}

function hookExport(name) {
  const p = Module.findExportByName(null, name) || Module.findExportByName("Security", name);
  if (!p) {
    console.log("[-] Missing export: " + name);
    return;
  }

  Interceptor.attach(p, {
    onEnter(args) {
      this.name = name;
      console.log("[SEC] " + name + " called");
      if (name === "SecItemCopyMatching" || name === "SecItemAdd" || name === "SecItemUpdate") {
        try {
          const dict = new ObjC.Object(args[0]);
          console.log("      query: " + dict.toString());
        } catch (e) {}
      }
    },
    onLeave(retval) {
      console.log("[SEC] " + this.name + " -> " + retval.toInt32());
    }
  });

  console.log("[+] Hooked " + name);
}

[
  "SecItemCopyMatching",
  "SecItemAdd",
  "SecItemUpdate",
  "SecItemDelete",
  "SecAccessControlCreateWithFlags",
  "SecAccessControlGetConstraints"
].forEach(hookExport);

// Keep the old LA hooks too
const LAContext = ObjC.classes.LAContext;
if (LAContext) {
  try {
    const m1 = LAContext["- evaluatePolicy:localizedReason:reply:"];
    Interceptor.attach(m1.implementation, {
      onEnter(args) {
        console.log("[LA] evaluatePolicy async called, policy=" + args[2]);
      }
    });
    console.log("[+] Hooked LAContext async");
  } catch (e) {}

  try {
    const m2 = LAContext["- canEvaluatePolicy:error:"];
    Interceptor.attach(m2.implementation, {
      onEnter(args) {
        console.log("[LA] canEvaluatePolicy called, policy=" + args[2]);
      }
    });
    console.log("[+] Hooked LAContext canEvaluatePolicy");
  } catch (e) {}
}

console.log("[*] Ready. Trigger biometric flow now.");
