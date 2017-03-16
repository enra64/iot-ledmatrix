package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;

import org.json.JSONObject;

public interface MessageSender {
    void sendMessage(JSONObject json, @Nullable String messageType);
}
