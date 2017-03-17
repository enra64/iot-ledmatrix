package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;

import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.discovery.NetworkDevice;

public interface MessageSender {
    NetworkDevice getCurrentServer();
    void sendMessage(JSONObject json, @Nullable String messageType);
}
