package de.oerntec.matledcontrol.networking.communication;

import com.google.gson.JsonObject;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

public interface MessageSender {
    /**
     * Get an LedMatrix object containing all known information about the matrix the MessageSender
     * is currently connected to
     */
    LedMatrix getCurrentMatrix();

    /**
     * send the json object as script data to the currently running script.
     * @param json json data to be wrapped in a script_data message
     */
    void sendScriptData(JsonObject json);

    /**
     * Request the listed script
     * @param scriptName name of the script
     */
    void requestScript(String scriptName);
}
