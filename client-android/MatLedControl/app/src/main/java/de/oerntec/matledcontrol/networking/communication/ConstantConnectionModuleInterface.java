package de.oerntec.matledcontrol.networking.communication;

import org.zeromq.ZMQ;


public interface ConstantConnectionModuleInterface {
    void start(String connectionString, ZMQ.Context context, ConstantConnectionModuleListener constantConnectionModuleListener, String installationId);
    void endConnection();
}
