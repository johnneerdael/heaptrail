package shop;

/**
 * A tiny program with a deliberate leak, used to produce a real JVM heap dump for the user guide.
 * Run it, then take a dump with jmap or jcmd while it sleeps. See scripts/docs-make-jvm-dump.sh.
 */
public final class Main {
    public static void main(String[] args) throws Exception {
        int visitors = args.length > 0 ? Integer.parseInt(args[0]) : 2000;
        for (int i = 0; i < visitors; i++) {
            SessionCache.put(new Session("session-" + i));
        }
        System.out.println("pid " + ProcessHandle.current().pid() + " sessions " + SessionCache.size());
        Thread.sleep(600_000);
    }
}
