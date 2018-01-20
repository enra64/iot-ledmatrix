package de.oerntec.matledcontrol.networking;

import de.oerntec.matledcontrol.networking.communication.ConstantConnectionModule;

public class ConnectionTester {

    private final ConstantConnectionModule connection;
    private final int interval;
    private boolean alive, killFlag, requirePing;

    public ConnectionTester(ConstantConnectionModule connection, int interval) {
        this.connection = connection;
        this.interval = interval;
        alive = true;
        killFlag = false;
        requirePing = true;

    }

    public void start() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (!killFlag) {
                    if (alive) {
                        alive = false;
                        requirePing = true;
                        try {
                            Thread.sleep(interval);
                        } catch (InterruptedException ignored) {
                        }
                    } else {
                        // not a time out if the kill flag was set
                        if (!killFlag)
                            connection.onTimeout();
                        break;
                    }
                }
            }
        }).start();
    }

    public boolean requirePing() {
        if (requirePing) {
            requirePing = false;
            return true;
        }
        return false;
    }

    public void setAlive() {
        alive = true;
    }

    public void stop() {
        killFlag = true;
    }
}
