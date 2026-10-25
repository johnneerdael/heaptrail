package shop;

/** One signed-in visitor. Each session carries an 8 KiB scratch buffer. */
final class Session {
    final String id;
    final byte[] scratch = new byte[8 * 1024];

    Session(String id) {
        this.id = id;
    }
}
