setTimeout(function() {
    if (ObjC.available) {

        var NSUserDefaults = ObjC.classes.NSUserDefaults;
        var standardUserDefaults = NSUserDefaults.standardUserDefaults();

        var dictionary = standardUserDefaults.dictionaryRepresentation();
        console.log(dictionary)
        send(dictionary)
    }  

    else {
        send("Objective-C Runtime is not available!");
    }
}, 2);