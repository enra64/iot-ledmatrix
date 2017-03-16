package de.oerntec.matledcontrol.networking.communication;

import org.json.JSONObject;

import java.net.InetAddress;

import de.oerntec.matledcontrol.networking.discovery.NetworkDevice;

/**
 * This listener interface must be implemented to be notified of data sent by the matrix
 */
public interface MessageListener {
    void onMessage(JSONObject data);
}
