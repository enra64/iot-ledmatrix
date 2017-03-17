package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;

import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

public interface MessageSender {
    LedMatrix getCurrentMatrix();
    void sendMessage(JSONObject json, @Nullable String messageType);
}
