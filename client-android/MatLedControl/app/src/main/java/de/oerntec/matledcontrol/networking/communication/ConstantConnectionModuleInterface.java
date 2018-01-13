package de.oerntec.matledcontrol.networking.communication;

import org.zeromq.ZMQ;

/**
 * Created by arne on 13.01.18.
 */

public interface ConstantConnectionModuleInterface {
    void start(String connectionString, ZMQ.Context context, ConstantConnectionModuleListener constantConnectionModuleListener);
    void endConnection();
}
