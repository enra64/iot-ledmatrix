package de.oerntec.matledcontrol.networking.communication;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.zeromq.ZMQException;

import java.nio.channels.ClosedSelectorException;

import de.oerntec.matledcontrol.BuildConfig;
import de.oerntec.matledcontrol.networking.ConnectionTester;

/**
 * Created by arne on 13.01.18.
 */

public class ConstantConnectionModule extends Thread implements ConstantConnectionModuleInterface {
    private org.zeromq.ZMQ.Socket zmqSocket;
    private ConnectionTester mConnectionTester = new ConnectionTester(this, 750);
    private boolean continueRunning;
    private String connectionString;
    private ConstantConnectionModuleListener constantConnectionModuleListener;
    private static final int ZMQ_CONTEXT_TERMINATED = 156384765;

    @Override
    public void run() {
        zmqSocket.connect(connectionString);

        while (continueRunning) {
            listenToMatrix();
            listenToApp();
        }

        zmqSocket.close();
    }

    private void listenToApp() {
        JSONObject nextOutMessage = constantConnectionModuleListener.getNextOutMessage();
        try {
            if (nextOutMessage != null)
                zmqSocket.send(nextOutMessage.toString());
        } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException e) {
            if (BuildConfig.DEBUG) Log.w("zmatrixcomm", "could not send " + nextOutMessage, e);
            constantConnectionModuleListener.moduleFailed();
        }

        try {
            if (mConnectionTester.requirePing())
                zmqSocket.send("{message_type:\"connection_test\"}");
        } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException e) {
            if (BuildConfig.DEBUG) Log.w("zmatrixcomm", "could not send connection test", e);
            constantConnectionModuleListener.moduleFailed();
        }
    }

    private void listenToMatrix() {
        String received = "";
        try {
            received = zmqSocket.recvStr();
            JSONObject receivedJson = new JSONObject(received);

            String messageType = receivedJson.getString("message_type");

            mConnectionTester.setAlive();

            switch (messageType) {
                case "connection_request_response":
                    constantConnectionModuleListener.onMatrixAcceptedConnection(receivedJson.getInt("matrix_width"), receivedJson.getInt("matrix_height"));
                    mConnectionTester.start();
                    break;
                case "shutdown_notification":
                    constantConnectionModuleListener.matrixShutDown();
                    break;
                case "connection_test_response":
                    // handled already
                    break;
                default:
                    constantConnectionModuleListener.onReceive(receivedJson);
            }


        } catch (JSONException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "undecipherable JSON received: " + received, e);
        } catch (ClosedSelectorException e) {
            constantConnectionModuleListener.moduleFailed();
        } catch (zmq.ZError.IOException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "ZError.IOException occurred!", e);
        } catch (ArrayIndexOutOfBoundsException e) {
            if (BuildConfig.DEBUG)
                Log.w("zmatrixcomm", "Array index out of bounds!", e);
        } catch (ZMQException e) {
            // if the context has been terminated before the receive call, ignore that exception
            // we also expect the continue running flag to be no longer set
            if (continueRunning || e.getErrorCode() != ZMQ_CONTEXT_TERMINATED)
                if (BuildConfig.DEBUG)
                    Log.w("zmatrixcomm", "ZMQException occurred!", e);
        }
    }

    public void onTimeout() {
        continueRunning = false;
        constantConnectionModuleListener.moduleFailed();
    }

    @Override
    public void start(String connectionString, org.zeromq.ZMQ.Context context, ConstantConnectionModuleListener constantConnectionModuleListener) {
        this.connectionString = connectionString;
        this.constantConnectionModuleListener = constantConnectionModuleListener;
    }

    @Override
    public void endConnection() {
        continueRunning = false;
        zmqSocket.setLinger(10);
    }
}
