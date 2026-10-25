package shop;

import java.util.HashMap;
import java.util.Map;

/** A cache that never evicts: every session ever created stays reachable from this static map. */
final class SessionCache {
    private static final Map<String, Session> BY_ID = new HashMap<>();

    static void put(Session session) {
        BY_ID.put(session.id, session);
    }

    static int size() {
        return BY_ID.size();
    }
}
