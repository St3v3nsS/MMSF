/**
 * MMSF – Task Hijacking (StrandHogg 1.0) Frida Hook
 * Monitors Activity lifecycle + startActivity to surface:
 *   - which task each activity lands in
 *   - the calling package (reveals reparenting)
 *   - intent flags (FLAG_ACTIVITY_NEW_TASK etc.)
 */

Java.perform(function () {

    var Activity = Java.use('android.app.Activity');
    var Log      = Java.use('android.util.Log');
    var TAG      = 'MMSF-TaskHijack';

    // ── onCreate ─────────────────────────────────────────────────────────────
    Activity.onCreate.overload('android.os.Bundle').implementation = function (bundle) {
        var pkg         = this.getPackageName();
        var cls         = this.getClass().getName();
        var taskId      = this.getTaskId();
        var callingPkg  = this.getCallingPackage();

        var msg = '[onCreate] class=' + cls
                + ' | pkg='          + pkg
                + ' | taskId='       + taskId
                + ' | calledBy='     + (callingPkg ? callingPkg : 'none');

        send(msg);
        Log.d(TAG, msg);
        return this.onCreate(bundle);
    };

    // ── onResume ─────────────────────────────────────────────────────────────
    Activity.onResume.implementation = function () {
        var pkg    = this.getPackageName();
        var cls    = this.getClass().getName();
        var taskId = this.getTaskId();

        var msg = '[onResume] class=' + cls
                + ' | pkg='          + pkg
                + ' | taskId='       + taskId;

        send(msg);
        Log.d(TAG, msg);
        return this.onResume();
    };

    // ── onNewIntent ──────────────────────────────────────────────────────────
    Activity.onNewIntent.implementation = function (intent) {
        var cls    = this.getClass().getName();
        var action = intent.getAction();
        var comp   = intent.getComponent();
        var flags  = intent.getFlags();

        var msg = '[onNewIntent] class=' + cls
                + ' | action='          + action
                + ' | component='       + comp
                + ' | flags=0x'         + flags.toString(16);

        send(msg);
        Log.d(TAG, msg);
        return this.onNewIntent(intent);
    };

    // ── startActivity (single Intent) ────────────────────────────────────────
    Activity.startActivity.overload('android.content.Intent').implementation = function (intent) {
        var cls    = this.getClass().getName();
        var action = intent.getAction();
        var comp   = intent.getComponent();
        var flags  = intent.getFlags();

        // FLAG_ACTIVITY_NEW_TASK = 0x10000000 → key indicator for hijack
        var flagNote = (flags & 0x10000000) ? '⚠ FLAG_ACTIVITY_NEW_TASK set' : '';

        var msg = '[startActivity] from='  + cls
                + ' | action='            + action
                + ' | component='         + comp
                + ' | flags=0x'           + flags.toString(16)
                + ' '                     + flagNote;

        send(msg);
        Log.d(TAG, msg);
        return this.startActivity(intent);
    };

    // ── getCallingPackage ────────────────────────────────────────────────────
    Activity.getCallingPackage.implementation = function () {
        var result = this.getCallingPackage();
        if (result) {
            var cls = this.getClass().getName();
            var msg = '[getCallingPackage] class=' + cls + ' → caller=' + result;
            send(msg);
            Log.d(TAG, msg);
        }
        return result;
    };

    send('[MMSF] Task Hijacking hooks loaded — monitoring activity lifecycle...');
});