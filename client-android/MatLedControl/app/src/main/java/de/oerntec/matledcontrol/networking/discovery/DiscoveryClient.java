package de.oerntec.matledcontrol.networking.discovery;


import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.json.JSONException;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ConcurrentHashMap;

import de.oerntec.matledcontrol.ExceptionListener;

/**
 * This abstract class serves as a skeleton for implementing both the discovery server implementation
 * as well as the discovery client implementation.
 */
@SuppressWarnings("WeakerAccess")
public class DiscoveryClient extends Thread {
    /**
     * Constant specifying how old a server discovery may be before it is regarded offline
     */
    private static final long MAXIMUM_SERVER_AGE_MS = 1000;

    /**
     * Timing variables
     */
    @SuppressWarnings("FieldCanBeLocal")
    private static final int DISCOVERY_BROADCAST_DELAY = 0,
            DISCOVERY_BROADCAST_PERIOD = 25,
            SERVER_LIST_REFRESH_DELAY = 25,
            SERVER_LIST_REFRESH_PERIOD = 10;

    /**
     * The ExceptionListener to be notified of exceptions
     */
    private final ExceptionListener mExceptionListener;

    /**
     * Our broadcaster handles the recurring self identification broadcasts.
     */
    private Broadcaster mBroadcaster;

    /**
     * Timer used to schedule recurring broadcasts
     */
    private Timer mRecurringBroadcastTimer = new Timer();

    /**
     * Timer used to keep the list of servers up to date by regularly removing old servers
     */
    private Timer mServerListTimer = new Timer();

    /**
     * list of servers
     */
    private ServerList mCurrentMatrixList;

    /**
     * True if the thread should keep running
     */
    private boolean mIsRunning = false;

    /**
     * True if the thread was started once
     */
    private boolean mHasRun = false;

    /**
     * Json parser for parsing json
     */
    JsonParser jsonParser = new JsonParser();

    /**
     * Create a new DiscoveryClient. In contrast to the DiscoveryServer, the DiscoveryClient does not
     * have to know its command- and data dataPort yet, because we can instantiate those when acutally
     * connecting to the ports supplied in the discovery response sent by the sever.
     *
     * @param listener            this listener will be notified of changes in the list of known servers
     * @param remoteDiscoveryPort the discoveryPort the discovery server listens on
     * @param selfName            the name this device should announce itself as
     */
    public DiscoveryClient(String selfName, int remoteDiscoveryPort, OnDiscoveryListener listener, ExceptionListener exceptionListener) throws IOException, JSONException {
        // name thread
        setName("DiscoveryClient");

        // save who wants to be notified of new servers
        mCurrentMatrixList = new ServerList(listener);

        mExceptionListener = exceptionListener;

        // the broadcaster handles everything related to sending broadcasts
        mBroadcaster = new Broadcaster(selfName, exceptionListener, remoteDiscoveryPort);
    }

    /**
     * Broadcast our information into the network, and listen to responding servers
     */
    @Override
    public void run() {
        try {
            DatagramSocket socket = new DatagramSocket();
            mBroadcaster.setSocket(socket);

            // send a new broadcast every n milliseconds, beginning now
            mRecurringBroadcastTimer.scheduleAtFixedRate(mBroadcaster, DISCOVERY_BROADCAST_DELAY, DISCOVERY_BROADCAST_PERIOD);
            mServerListTimer.scheduleAtFixedRate(mCurrentMatrixList, SERVER_LIST_REFRESH_DELAY, SERVER_LIST_REFRESH_PERIOD);

            // continuously check if we should continue listening
            while (isRunning()) {
                try {
                    listen(socket);
                    // ignore timeoutexceptions, they are necessary to be able to check isRunning
                } catch (SocketTimeoutException ignored) {
                } catch (SocketException e) {
                    socket = new DatagramSocket();
                    mBroadcaster.setSocket(socket);
                }
            }

            // endConnection the socket after use
            socket.close();
        } catch (IOException ex) {
            mExceptionListener.onException(this, ex, "IOException occurred while broadcasting for matrices.");
        } finally {
            // stop sending broadcasts
            mRecurringBroadcastTimer.cancel();

            // stop updating the server list
            mServerListTimer.cancel();
        }
    }

    /**
     * Start the thread. To quote the java api specification "It is never legal to start a thread
     * more than once. In particular, a thread may not be restarted once it has completed execution."
     * Use {@link #hasRun()} to check whether you may start the thread
     */
    @Override
    public synchronized void start() {
        if (mHasRun)
            throw new AssertionError("You are trying to restart a thread. That is not legal. Create a new instance instead.");
        mHasRun = true;
        mIsRunning = true;
        super.start();
    }

    /**
     * Check whether the server is set to stay running
     *
     * @return true if the server will continue running
     */
    public boolean isRunning() {
        return mIsRunning;
    }

    public void close() {
        // stop the listening loop
        mIsRunning = false;
    }

    /**
     * Check whether this threads {@link #start()} has already been called. If it returns true,
     * start() must not be called on this instance, since threads cannot be restarted.
     *
     * @return true if this thread has already been started
     */
    public boolean hasRun() {
        return mHasRun;
    }

    /**
     * Wait for a LedMatrix object to arrive on the set {@link DatagramSocket}. Other messages will be discarded.
     *
     * @throws IOException either a {@link SocketTimeoutException} if the wait times out, or any other IO exception that occurse
     */
    protected void listen(DatagramSocket socket) throws IOException {
        // wait for a message on our socket
        byte[] recvBuf = new byte[4096];
        DatagramPacket receivePacket = new DatagramPacket(recvBuf, recvBuf.length);
        socket.receive(receivePacket);

        // initialise an ObjectInputStream

        LedMatrix identification;
        try {
            JsonObject received_object = jsonParser.parse(new String(receivePacket.getData())).getAsJsonObject();
            // create the LedMatrix describing our remote partner
            identification = LedMatrix.fromJson(received_object);
            identification.address = receivePacket.getAddress().getHostAddress();

            // notify sub-class
            mCurrentMatrixList.addMatrix(identification);

            // if the cast to LedMatrix fails, this message was not sent by the discovery system, and may be ignored
        } catch (JSONException e) {
            mExceptionListener.onException(this, e, "Error when parsing discovery response from matrix");
        }
    }

    /**
     * A TimerTask extension that removes old servers
     */
    private class ServerList extends TimerTask {
        /**
         * Current list of known servers as well as a timestamp marking their time of discovery
         */
        private ConcurrentHashMap<LedMatrix, Long> mCurrentServerList = new ConcurrentHashMap<>();

        /**
         * Listener to be called when our list of servers is updated
         */
        private OnDiscoveryListener mDiscoveryListener;

        /**
         * Flag variable to trigger updates if necessary
         */
        private boolean mChanged = false;

        /**
         * Create a new ServerList that will push the most current list to the discovery listener
         * at regular intervals
         */
        ServerList(OnDiscoveryListener onDiscoveryListener) {
            mDiscoveryListener = onDiscoveryListener;
        }

        @Override
        public void run() {
            long now = System.currentTimeMillis();

            // remove all servers older than MAXIMUM_SERVER_AGE_MS
            Iterator<Map.Entry<LedMatrix, Long>> it = mCurrentServerList.entrySet().iterator();
            while (it.hasNext()) {
                // get the next devices discovery timestamp
                long discoveryTimestamp = it.next().getValue();

                // if the device is too old, remove it and flag a change
                if ((now - discoveryTimestamp) > MAXIMUM_SERVER_AGE_MS) {
                    it.remove();
                    mChanged = true;
                }
            }

            // notify listener of update if a change occurred
            if (mChanged) {
                mDiscoveryListener.onServerListUpdated(getCurrentServers());
                mChanged = false;
            }
        }

        /**
         * Retrieve an up-to-date list of known servers
         */
        private List<LedMatrix> getCurrentServers() {
            return new ArrayList<>(mCurrentServerList.keySet());
        }

        /**
         * Adds a server to the list or, if it already exists, updates it.
         */
        void addMatrix(LedMatrix device) {
            // the list only changed if the device was unknown
            if (!mCurrentServerList.containsKey(device))
                mChanged = true;

            // store (possibly) new device
            mCurrentServerList.put(device, System.currentTimeMillis());
        }
    }
}
