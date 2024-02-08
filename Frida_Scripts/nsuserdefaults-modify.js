recv('start', function onMessage(msg) {
    console.log("[*] Received 'start' message from Python.");

    // Your Frida script logic here
    if (ObjC.available) {
        var NSUserDefaults = ObjC.classes.NSUserDefaults;
        var NSDictionary = NSUserDefaults.alloc().init();
        NSDictionary.setObject_forKey_(msg.value, msg.key);
        var plistContents = NSDictionary.dictionaryRepresentation().toString();

        // Send a message back to Python with the plistContents
        send(plistContents);
    } else {
        send("Objective-C Runtime is not available!");
    }
});