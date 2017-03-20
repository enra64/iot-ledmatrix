package de.oerntec.matledcontrol.networking.communication;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

/**
 * Created by arne on 16.03.17.
 */

public interface ConnectionListener {
    void onConnectionRequestResponse(LedMatrix matrix, boolean granted);
    void onMatrixDisconnected(LedMatrix matrix);
}
