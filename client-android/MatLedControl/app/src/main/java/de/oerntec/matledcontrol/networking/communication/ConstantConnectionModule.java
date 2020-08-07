package de.oerntec.matledcontrol.networking.communication;

import org.zeromq.ZContext;

/**
 * Interface for classes implementing a connection module
 */
public interface ConstantConnectionModule {
    void start(String connectionString, ZContext context, ConstantConnectionModuleListener constantConnectionModuleListener, String installationId);
    void endConnection();
}
