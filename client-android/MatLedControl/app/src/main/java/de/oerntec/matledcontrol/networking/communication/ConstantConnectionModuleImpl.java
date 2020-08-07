package de.oerntec.matledcontrol.networking.communication;

import android.util.Log;

import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonParser;

import org.zeromq.SocketType;
import org.zeromq.ZContext;
import org.zeromq.ZMQException;

import java.nio.channels.ClosedSelectorException;

import de.oerntec.matledcontrol.BuildConfig;
import de.oerntec.matledcontrol.networking.ConnectionTester;
import zmq.ZError;


public class ConstantConnectionModuleImpl extends Thread implements ConstantConnectionModule {
    private org.zeromq.ZMQ.Socket zmqSocket;
    private ZContext zmqContext;
    private ConnectionTester mConnectionTester = new ConnectionTester(this, 750);
    private boolean continueRunning = true;
    private String connectionString;
    private ConstantConnectionModuleListener constantConnectionModuleListener;
    private static final int ZMQ_CONTEXT_TERMINATED = 156384765;
    private String pingMessage;
    private boolean hadTimeout = false;

    @Override
    public void run() {
        zmqSocket = zmqContext.createSocket(SocketType.DEALER);
        zmqSocket.connect(connectionString);
        zmqSocket.setReceiveTimeOut(100);

        while (continueRunning) {
            listenToMatrix();
            if (continueRunning)
                listenToApp();
        }

        zmqSocket.close();
        constantConnectionModuleListener.moduleStopped(hadTimeout);
    }

    private void listenToApp() {
        JsonObject nextOutMessage = constantConnectionModuleListener.getNextOutMessage();
        try {
            if (nextOutMessage != null)
                zmqSocket.send(nextOutMessage.toString());
        } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "could not send " + nextOutMessage, e);
            continueRunning = false;
            return;
        }

        try {
            if (mConnectionTester.requirePing())
                zmqSocket.send(pingMessage);
        } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "could not send connection test", e);
            continueRunning = false;
        }
    }

    private void listenToMatrix() {
        String received = "";
        try {
            received = zmqSocket.recvStr();

            if (received == null)
                return;

            JsonObject receivedJson = JsonParser.parseString(received).getAsJsonObject();

            String messageType = receivedJson.get("message_type").getAsString();

            mConnectionTester.setAlive();

            switch (messageType) {
                case "connection_request_response":
                    int matrixWidth = receivedJson.get("matrix_width").getAsInt();
                    int matrixHeight = receivedJson.get("matrix_height").getAsInt();
                    constantConnectionModuleListener.onMatrixAcceptedConnection(matrixWidth, matrixHeight);
                    mConnectionTester.start();
                    break;
                case "shutdown_notification":
                    continueRunning = false;
                    constantConnectionModuleListener.matrixShutDown();
                    return;
                case "connection_test_response":
                    // handled already
                    break;
                default:
                    constantConnectionModuleListener.onReceive(receivedJson);
            }
        } catch (JsonParseException e) {
            if (BuildConfig.DEBUG)
                Log.e("ccm", "JsonParseException for " + received, e);
        } catch (ClosedSelectorException e) {
            continueRunning = false;
        } catch (zmq.ZError.IOException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "ZError.IOException occurred!", e);
        } catch (ArrayIndexOutOfBoundsException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "Array index out of bounds!", e);
        } catch (ZMQException e) {
            // if the context has been terminated before the receive call, ignore that exception
            // we also expect the continue running flag to be no longer set
            if (continueRunning || e.getErrorCode() != ZMQ_CONTEXT_TERMINATED) {
                if (BuildConfig.DEBUG)
                    Log.w("zmatrixcomm", "ZMQException occurred!", e);
                continueRunning = false;
            }
        }
    }

    public void onTimeout() {
        continueRunning = false;
        hadTimeout = true;
    }

    @Override
    public void start(String connectionString, ZContext context, ConstantConnectionModuleListener constantConnectionModuleListener, String installationId) {
        this.connectionString = connectionString;
        this.constantConnectionModuleListener = constantConnectionModuleListener;
        this.zmqContext = context;
        this.pingMessage = String.format("{\"id\":\"%s\",\"message_type\":\"connection_test\"}", installationId);
        start();
    }

    @Override
    public void endConnection() {
        continueRunning = false;


        if (zmqSocket != null) {
            try {
                zmqSocket.setLinger(10);
            } catch (ZError.CtxTerminatedException e) {
                if (BuildConfig.DEBUG) {
                    Log.w("const conn module", "the context was already terminated upon calling endConnection");
                }
            }
        }

    }
}
