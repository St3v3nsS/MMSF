// Your Frida script logic here
if (ObjC.available) {
    var NSUserDefaults = ObjC.classes.NSUserDefaults;
    var NSDictionary = NSUserDefaults.alloc().init().dictionaryRepresentation();
    var plistContents = NSDictionary.toString();
    // Send a message back to Python with the plistContents
    console.log(plistContents);
    send(plistContents)
} else {
    send("Objective-C Runtime is not available!");
}