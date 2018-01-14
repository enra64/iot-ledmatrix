package de.oerntec.matledcontrol.networking.communication;

import org.json.JSONObject;

/**
 * Created by arne on 13.01.18.
 */

public interface ConstantConnectionModuleListener {
    /**
     * Called if the run thread has exited
     */
    void moduleStopped();
    void matrixShutDown();
    JSONObject getNextOutMessage();
    void onMatrixAcceptedConnection(int width, int height);

    void onReceive(JSONObject receivedJson);
}
