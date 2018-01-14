package de.oerntec.matledcontrol.networking.communication;

import android.os.Handler;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.zeromq.ZMQ;

import java.util.Queue;
import java.util.concurrent.ArrayBlockingQueue;

import de.oerntec.matledcontrol.BuildConfig;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

public class ConstantConnection implements Connection, ConstantConnectionModuleListener {
    private LedMatrix matrix;
    private MatrixListener matrixListener;
    private ConnectionStatusListener connectionStatusListener;
    private ConstantConnectionModuleInterface module;
    private Queue<JSONObject> outBox;
    private ZMQ.Context zmqContext;
    private String connectionString;
    private String installationId;

    @Override
    public void initialize(LedMatrix matrix, MatrixListener listener, ConnectionStatusListener connectionStatusListener, @NonNull String installationId) {
        this.matrix = matrix;
        this.matrixListener = listener;
        this.installationId = installationId;
        this.connectionStatusListener = connectionStatusListener;
        outBox = new ArrayBlockingQueue<>(200);
        zmqContext = org.zeromq.ZMQ.context(1);
        connectionString = "tcp://" + matrix.address + ":" + matrix.dataPort;
        cycleModule();

        sendMessage(new JSONObject(), "connection_request");
    }

    @Override
    public void sendMessage(JSONObject message, @Nullable String messageType) {
        if (!message.has("message_type") && messageType == null)
            throw new AssertionError("Messages must have message_type set or a messageType must be given");

        if (messageType != null) {
            try {
                message.put("message_type", messageType);
            } catch (JSONException ignored) {
            }
        }

        try {
            message.put("id", installationId);
        } catch (JSONException e) {
            if (BuildConfig.DEBUG)
                Log.w("ConstantConnection", e);
        }

        outBox.add(message);
    }

    /**
     * Close the current connection
     */
    @Override
    public void closeConnection() {
        if (module != null)
            module.endConnection();
        module = null;
    }

    /**
     * Close the connection, free resources
     */
    @Override
    public void destroy() {
        closeConnection();
        new Handler().post(new Runnable() {
            @Override
            public void run() {
                zmqContext.close();
            }
        });
    }

    @Override
    public void moduleStopped() {
        cycleModule();
    }

    private void cycleModule() {
        if (module != null)
            module.endConnection();
        module = new ConstantConnectionModule();
        module.start(connectionString, zmqContext, this, installationId);
    }

    @Override
    public void matrixShutDown() {
        connectionStatusListener.onMatrixDisconnected(matrix);
    }

    @Override
    @Nullable
    public JSONObject getNextOutMessage() {
        return outBox.poll();
    }

    @Override
    public void onMatrixAcceptedConnection(int width, int height) {
        matrix.width = width;
        matrix.height = height;
        connectionStatusListener.onConnectionRequestResponse(matrix, true);
    }

    @Override
    public void onReceive(JSONObject receivedJson) {
        matrixListener.onMessage(receivedJson);
    }
}
