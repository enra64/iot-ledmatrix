package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.NonNull;
import android.support.annotation.Nullable;

import com.google.gson.JsonObject;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

/**
 * Created by arne on 13.01.18.
 */

public interface Connection {
    void initialize(LedMatrix matrix, MatrixListener listener, ConnectionStatusListener connectionStatusListener, @NonNull String installationId);

    void sendMessage(JsonObject message, @Nullable String messageType);

    /**
     * Close the current connection
     */
    void closeConnection();

    /**
     * Close the connection, free resources
     */
    void destroy();
}
