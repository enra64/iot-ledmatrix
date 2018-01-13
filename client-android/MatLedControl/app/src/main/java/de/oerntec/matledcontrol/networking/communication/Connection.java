package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;

import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

/**
 * Created by arne on 13.01.18.
 */

public interface Connection {
    void initialize(LedMatrix matrix, MatrixListener listener, ConnectionStatusListener connectionStatusListener);

    void sendMessage(JSONObject message, @Nullable String messageType);

    /**
     * Close the current connection
     */
    void closeConnection();

    /**
     * Close the connection, free resources
     */
    void destroy();
}
