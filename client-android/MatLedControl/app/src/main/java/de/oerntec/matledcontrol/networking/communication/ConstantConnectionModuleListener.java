package de.oerntec.matledcontrol.networking.communication;

import org.json.JSONObject;

/**
 * Created by arne on 13.01.18.
 */

public interface ConstantConnectionModuleListener {
    void moduleFailed();
    void matrixShutDown();
    JSONObject getNextOutMessage();
    void onMatrixAcceptedConnection(int width, int height);

    void onReceive(JSONObject receivedJson);
}
