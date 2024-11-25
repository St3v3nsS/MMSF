const module_name = "libsystem_kernel.dylib";
const exp_name = "task_threads";

function prettyExportDetail(message) {
    return '[*]' + message + '\t' + exp_name + '()\tinside: ' + module_name;
}

if (ObjC.available) {
    console.log("[*]Frida running. ObjC API available!");
    try {
        const ptrToExport = Module.findExportByName(module_name, exp_name);
        if (!ptrToExport) {
            throw new Error(prettyExportDetail('Cannot find Export:'));
        }
        console.log(prettyExportDetail('Pointer to'));

        Interceptor.attach(ptrToExport, {
            onEnter: function (args) {
                console.log(prettyExportDetail('onEnter() interceptor ->'));
                this._threadCountPointer = new NativePointer(args[2]);
                console.log('[*]Address of Thread Count:' + this._threadCountPointer );
            },

            onLeave: function (retValue) {
                this._patchInt = 4
                console.log(JSON.stringify({
                    return_value: retValue,
                    patched_return_value: this._patchInt,
                    function: exp_name,
                }));
                retValue.replace(this._patchInt)
            }
        });
        
    }
    catch(err){
        console.error(err.message);
    }
}
else {
    console.log("[!]Objective-C Runtime is not available!");
}