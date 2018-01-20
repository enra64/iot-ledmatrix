package de.oerntec.matledcontrol.networking.communication;

import com.google.gson.JsonObject;

/**
 * Created by arne on 13.01.18.
 */

public interface ConstantConnectionModuleListener {
    /**
     * Called if the run thread has exited
     */
    void moduleStopped(boolean hadTimeout);
    void matrixShutDown();
    JsonObject getNextOutMessage();
    void onMatrixAcceptedConnection(int width, int height);

    void onReceive(JsonObject receivedJson);
}
