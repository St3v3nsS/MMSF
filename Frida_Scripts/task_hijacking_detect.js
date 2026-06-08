// task_hijack_check.js
// Enumerates live activities and prints task-hijacking relevant metadata

setImmediate(function () {
  console.log("[*] task_hijack_check loaded, pid=" + Process.id);

  if (!Java.available) {
    console.log("[-] Java runtime not available");
    return;
  }

  Java.perform(function () {
    try {
      var ActivityThread = Java.use("android.app.ActivityThread");
      var currentThread = ActivityThread.currentActivityThread();

      if (!currentThread) {
        console.log("[-] currentActivityThread() returned null");
        return;
      }

      var mActivities = currentThread.mActivities.value;
      if (!mActivities) {
        console.log("[-] mActivities is null");
        return;
      }

      var PackageManager = Java.use("android.content.pm.PackageManager");
      var activities = mActivities.values().toArray();

      console.log("[*] Live activity count: " + activities.length);

      activities.forEach(function (rec, idx) {
        try {
          var activity = rec.activity.value;
          if (!activity) return;

          var comp = activity.getComponentName();
          var pm = activity.getPackageManager();
          var ai = pm.getActivityInfo(comp, 0);

          var name = comp.getClassName();
          var pkg = comp.getPackageName();

          var affinity = ai.taskAffinity ? ai.taskAffinity.value : "(null)";
          var exported = ai.exported.value;
          var allowTaskReparenting = ai.allowTaskReparenting.value;
          var launchMode = ai.launchMode.value;
          var permission = ai.permission ? ai.permission.value : "(none)";
          var excludeFromRecents = ai.excludeFromRecents.value;
          var noHistory = ai.flags.value;

          var taskId = -1;
          try {
            taskId = activity.getTaskId();
          } catch (e) {}

          console.log("==================================================");
          console.log("[Activity #" + idx + "] " + name);
          console.log("  package                : " + pkg);
          console.log("  taskId                 : " + taskId);
          console.log("  taskAffinity           : " + affinity);
          console.log("  exported               : " + exported);
          console.log("  allowTaskReparenting   : " + allowTaskReparenting);
          console.log("  launchMode             : " + launchMode + "  (0=standard,1=singleTop,2=singleTask,3=singleInstance)");
          console.log("  permission             : " + permission);
          console.log("  excludeFromRecents     : " + excludeFromRecents);
          console.log("  flags                  : " + noHistory);

          var risky = false;
          var reasons = [];

          if (exported) {
            risky = true;
            reasons.push("exported=true");
          }

          if (allowTaskReparenting) {
            risky = true;
            reasons.push("allowTaskReparenting=true");
          }

          if (affinity && affinity !== pkg && affinity !== "") {
            risky = true;
            reasons.push("custom taskAffinity=" + affinity);
          }

          if (launchMode === 0 || launchMode === 1) {
            reasons.push("launchMode is standard/singleTop");
          }

          if (risky) {
            console.log("  [!] RISK INDICATORS: " + reasons.join(" | "));
          } else {
            console.log("  [+] No obvious task-hijacking indicators on this activity");
          }

        } catch (e) {
          console.log("[-] Error while inspecting activity: " + e);
        }
      });

      console.log("==================================================");
      console.log("[*] Done.");

    } catch (e) {
      console.log("[-] Fatal error: " + e);
    }
  });
});
