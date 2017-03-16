package de.oerntec.matledcontrol.networking.communication;

import de.oerntec.matledcontrol.networking.discovery.NetworkDevice;

/**
 * Created by arne on 16.03.17.
 */

public interface ConnectionListener {
    void onConnectionRequestResponse(NetworkDevice matrix, boolean granted);
}
