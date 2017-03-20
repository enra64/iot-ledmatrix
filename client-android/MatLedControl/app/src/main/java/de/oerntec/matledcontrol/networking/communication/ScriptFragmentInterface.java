package de.oerntec.matledcontrol.networking.communication;

import org.json.JSONObject;

/**
 * This listener interface must be implemented to be notified of data sent by the matrix
 */
public interface ScriptFragmentInterface {
    /**
     * The script the fragment wants the server to load.
     * @return the name of the script minus ".py" as well as the name of the contained class. "null" is reserved.
     */
    String requestScript();

    /**
     * Called whenever this script receives data from the matrix
     */
    void onMessage(JSONObject data);
}
