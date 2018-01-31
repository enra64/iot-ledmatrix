package de.oerntec.matledcontrol.networking.communication;

import org.zeromq.ZMQ;

/**
 * Interface for classes implementing a connection module
 */
public interface ConstantConnectionModule {
    void start(String connectionString, ZMQ.Context context, ConstantConnectionModuleListener constantConnectionModuleListener, String installationId);
    void endConnection();
}
