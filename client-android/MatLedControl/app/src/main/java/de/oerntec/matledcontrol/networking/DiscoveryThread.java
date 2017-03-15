package de.oerntec.matledcontrol.networking;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;

/**
 * This abstract class serves as a skeleton for implementing both the discovery server implementation
 * as well as the discovery client implementation.
 */
@SuppressWarnings("WeakerAccess")
public abstract class DiscoveryThread extends Thread {
    /**
     * The socket this thread should use for all of its network operations
     */
    private DatagramSocket mSocket;

    /**
     * True if the thread should keep running
     */
    private boolean mIsRunning = false;

    /**
     * True if the thread was started once
     */
    private boolean mHasRun = false;

    /**
     * A NetworkDevice that identifies the device this Object is running on
     */
    private NetworkDevice mSelfDeviceId;

    /**
     * The port at which some server should be listening
     */
    private int mLocalDiscoveryPort;

    /**
     * Create a new DiscoveryThread when you already know your command- and data port, for example for use in a server
     * announcing where to connect.
     *
     * @param selfName         the discovery thread will announce this name to other devices seeking partners in the network
     * @param localDataPort    a data server should be listening here to receive further communication
     */
    public DiscoveryThread(String selfName, int localDataPort) {
        mSelfDeviceId = new NetworkDevice(selfName, localDataPort);
    }

    /**
     * This function must be overridden to complete the DiscoveryThread. You probably want to do something like
     * <pre>
     *     {@code while(started())
     *          listen(); }
     * </pre>
     */
    @Override
    public abstract void run();

    /**
     * Send an object identifying the configured network device.
     *
     * @param targetHost to which target the message should be sent
     * @param targetPort at which discoveryPort the message should arrive on targetHost
     * @throws IOException if the identification message could not be sent
     */
    public void sendSelfIdentification(InetAddress targetHost, int targetPort) throws IOException, JSONException {
        JSONObject deviceJson = mSelfDeviceId.toJson();
        deviceJson.put("message_type", "discovery");

        byte[] data = deviceJson.toString().getBytes("utf-8");

        // create an UDP packet from the byte buffer and send it to the desired host/discoveryPort combination
        DatagramPacket sendPacket = new DatagramPacket(data, data.length, targetHost, targetPort);
        mSocket.send(sendPacket);
    }

    /**
     * Start the thread. To quote the java api specification "It is never legal to start a thread
     * more than once. In particular, a thread may not be restarted once it has completed execution."
     * Use {@link #hasRun()} to check whether you may start the thread
     */
    @Override
    public synchronized void start() {
        mHasRun = true;
        mIsRunning = true;
        super.start();
    }

    /**
     * Check whether this threads {@link #start()} has already been called. If it returns true,
     * start() must not be called on this instance, since threads cannot be restarted.
     * @return true if this thread has already been started
     */
    public boolean hasRun() {
        return mHasRun;
    }

    /**
     * Wait for a NetworkDevice object to arrive on the set {@link DatagramSocket}. Other messages will be discarded.
     *
     * @throws IOException either a {@link SocketTimeoutException} if the wait times out, or any other IO exception that occurse
     */
    protected void listen() throws IOException {
        // wait for a message on our socket
        byte[] recvBuf = new byte[4096];
        DatagramPacket receivePacket = new DatagramPacket(recvBuf, recvBuf.length);
        mSocket.receive(receivePacket);

        // initialise an ObjectInputStream

        NetworkDevice identification;
        try {
            // create the NetworkDevice describing our remote partner
            identification = NetworkDevice.fromJsonString(new String(receivePacket.getData()));
            identification.address = receivePacket.getAddress().getHostAddress();

            // notify sub-class
            onDiscovery(identification);

            // if the cast to NetworkDevice fails, this message was not sent by the discovery system, and may be ignored
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /**
     * Called when {@link #listen()} gets a discovery message
     *
     * @param newDevice the device that sent the message
     */
    protected abstract void onDiscovery(NetworkDevice newDevice);

    /**
     * Check whether the server is set to stay running
     *
     * @return true if the server will continue running
     */
    public boolean isRunning() {
        return mIsRunning;
    }

    /**
     * Get the socket currently configured to be used by the discovery system
     *
     * @return socket currently used by the discovery system
     */
    protected DatagramSocket getSocket() {
        return mSocket;
    }

    /**
     * Set the socket to be used by this {@link DiscoveryThread}
     *
     * @param socket new socket configuration
     * @throws SocketException if some of the configuration failed
     */
    protected void setSocket(DatagramSocket socket) throws SocketException {
        // socket must be broadcasting
        socket.setBroadcast(true);

        // save socket
        mSocket = socket;

        // update our local discoveryPort; this is the only definitive source
        mLocalDiscoveryPort = socket.getLocalPort();

        // update self device id so the server can respond to our discovery address
        mSelfDeviceId.discoveryPort = mLocalDiscoveryPort;
    }

    /**
     * Signal the running while loop to stop
     */
    public void close() {
        mIsRunning = false;
    }
}
