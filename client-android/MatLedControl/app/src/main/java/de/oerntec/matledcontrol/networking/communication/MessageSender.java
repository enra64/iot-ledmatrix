package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;

import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

public interface MessageSender {
    LedMatrix getCurrentMatrix();

    /**
     * send the json object as script data to the currently running script.
     * @param json json data to be wrapped in a script_data message
     */
    void sendScriptData(JSONObject json);
}
