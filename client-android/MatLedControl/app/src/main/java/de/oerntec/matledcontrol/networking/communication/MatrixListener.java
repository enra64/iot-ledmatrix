package de.oerntec.matledcontrol.networking.communication;

import com.google.gson.JsonObject;

/**
 * This listener interface must be implemented to be notified of data sent by the matrix
 */
public interface MatrixListener {
    /**
     * The script the fragment wants the server to load.
     * @return the name of the script minus ".py" as well as the name of the contained class. "null" is reserved.
     */
    String requestScript();

    /**
     * Called whenever this script receives data from the matrix
     */
    void onMessage(JsonObject data);
}
