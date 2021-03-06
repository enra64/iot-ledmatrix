package de.oerntec.matledcontrol.networking.communication;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

/**
 * An interface abstracting necessary callbacks informing the users of matrix connection state changes
 */
public interface ConnectionStatusListener {
    /**
     * Called when matrix answered the connection request
     * @param matrix the matrix we wanted to connect to
     * @param granted true if the connection was granted, false otherwise
     */
    void onConnectionRequestResponse(LedMatrix matrix, @SuppressWarnings("SameParameterValue") boolean granted);

    /**
     * Called when matrix has sent a shutdown notification
     * @param matrix the matrix that went offline
     */
    void onMatrixShutDown(LedMatrix matrix);

    /**
     * Called when the limit for connection retries has been reached
     *
     * @param matrix the matrix that we are trying to connect to
     */
    void onConnectionRetryLimitReached(LedMatrix matrix);
}
