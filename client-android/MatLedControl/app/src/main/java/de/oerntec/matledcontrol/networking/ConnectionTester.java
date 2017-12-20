package de.oerntec.matledcontrol.networking;

import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.communication.ZeroMatrixConnection;

public class ConnectionTester {

    private final ZeroMatrixConnection connection;
    private final int interval;
    private boolean alive, killFlag;

    public ConnectionTester(ZeroMatrixConnection connection, int interval) {
        this.connection = connection;
        this.interval = interval;
        alive = true;
        killFlag = false;
        sendKeepAliveMessage();
        startChecker();
    }

    private void startChecker() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (!killFlag) {
                    if(alive) {
                        alive = false;
                        sendKeepAliveMessage();
                        try {
                            Thread.sleep(interval);
                        } catch (InterruptedException ignored) {
                        }
                    } else {
                        if(!killFlag)
                            connection.timedOut();
                        break;
                    }
                }
            }
        }).start();
    }

    private void sendKeepAliveMessage() {
        connection.sendMessage(new JSONObject(), "connection_test");
    }

    public void setAlive() {
        alive = true;
    }

    public void stop() {
        killFlag = true;
    }
}
