package de.oerntec.matledcontrol.networking.communication;

import android.os.Handler;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;

import com.google.gson.JsonObject;

import org.zeromq.ZContext;
import org.zeromq.ZMQ;

import java.util.Queue;
import java.util.concurrent.ArrayBlockingQueue;

import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

public class ConstantConnection implements Connection, ConstantConnectionModuleListener {
    private static final int[] BACKOFF_MULTIPLIERS = new int[] { 1, 1, 2, 3, 5, 8, 13 };

    /**
     * The LedMatrix we want to connect to
     */
    private LedMatrix matrix;

    /**
     * This {@link MatrixListener} instance is used to react to common matrix data events
     */
    private MatrixListener matrixListener;

    /**
     * The connectionstatuslistener we want to inform about significant connection state changes
     */
    private ConnectionStatusListener connectionStatusListener;

    /**
     * The constant connection module currently in use
     */
    private ConstantConnectionModule module;

    /**
     * Queue for outgoing messages
     */
    private Queue<JsonObject> outBox;

    /**
     * The ZMQ context
     */
    private ZContext zmqContext;

    /**
     * The connection string that can be used to connect to the matrix
     */
    private String connectionString;

    /**
     * The installation id of this app
     */
    private String installationId;

    /**
     * True if the context has been terminated by this class
     */
    private boolean zmqContextTerminated = false;

    /**
     * Amount of cycling that should be tried before declaring the connection dead
     */
    private static final int MAXIMUM_CYCLE_COUNT = BACKOFF_MULTIPLIERS.length;

    /**
     * The millis() timestamp after which the next connection try may be made
     */
    private long nextConnectionTry = -1;

    /**
     * The millis() timestamp at which the last cycle has been initiated
     */
    private long lastConnectionInitialization = -1;

    /**
     * the number of tries we have now done to reconnect to the matrix
     */
    private int currentCycleIteration = 0;

    @Override
    public void initialize(LedMatrix matrix, MatrixListener listener, ConnectionStatusListener connectionStatusListener, @NonNull String installationId) {
        this.matrix = matrix;
        this.matrixListener = listener;
        this.installationId = installationId;
        this.connectionStatusListener = connectionStatusListener;
        outBox = new ArrayBlockingQueue<>(200);
        zmqContext = new ZContext(1);
        connectionString = "tcp://" + matrix.address + ":" + matrix.dataPort;
        cycleModule();

        sendMessage(new JsonObject(), "connection_request");
    }

    @Override
    public void sendMessage(JsonObject message, @Nullable String messageType) {
        if (!message.has("message_type") && messageType == null)
            throw new AssertionError("Messages must have message_type set or a messageType must be given");

        if (messageType != null) {
                message.addProperty("message_type", messageType);
        }

        message.addProperty("id", installationId);

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
        new Handler().post(() -> {
            zmqContextTerminated = true;
            zmqContext.close();
        });
    }

    @Override
    public void moduleStopped(boolean hadTimeout) {
        if (currentCycleIteration < MAXIMUM_CYCLE_COUNT)
            cycleModule();
        else {
            connectionStatusListener.onConnectionRetryLimitReached(matrix);
            closeConnection();
        }
    }

    private void cycleModule() {
        if (module != null)
            module.endConnection();

        if (zmqContextTerminated)
            return;

        if (System.currentTimeMillis() > nextConnectionTry) {
            // allow the next try only after some time (50ms * BACKOFF...)
            nextConnectionTry = System.currentTimeMillis() + (50 * BACKOFF_MULTIPLIERS[currentCycleIteration]);

            // make the next try wait a little longer
            currentCycleIteration++;

            // try to connect
            module = new ConstantConnectionModuleImpl();
            module.start(connectionString, zmqContext, this, installationId);
        }
    }

    @Override
    public void matrixShutDown() {
        connectionStatusListener.onMatrixShutDown(matrix);
    }

    @Override
    @Nullable
    public JsonObject getNextOutMessage() {
        return outBox.poll();
    }

    @Override
    public void onMatrixAcceptedConnection(int width, int height) {
        matrix.width = width;
        matrix.height = height;
        connectionStatusListener.onConnectionRequestResponse(matrix, true);
    }

    @Override
    public void onReceive(JsonObject receivedJson) {
        matrixListener.onMessage(receivedJson);
    }
}
