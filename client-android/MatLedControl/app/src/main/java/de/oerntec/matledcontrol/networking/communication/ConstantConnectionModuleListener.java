package de.oerntec.matledcontrol.networking.communication;

import com.google.gson.JsonObject;

/**
 * The listener for classes that want to react to state changes of a connection module
 */
public interface ConstantConnectionModuleListener {
    /**
     * Called if the run thread of the module has exited
     */
    void moduleStopped(boolean hadTimeout);
    void matrixShutDown();
    JsonObject getNextOutMessage();
    void onMatrixAcceptedConnection(int width, int height);

    void onReceive(JsonObject receivedJson);
}
