package de.oerntec.matledcontrol.networking.discovery;

import android.util.Log;

import com.google.gson.JsonObject;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InterfaceAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;
import java.util.LinkedList;
import java.util.List;
import java.util.TimerTask;

import de.oerntec.matledcontrol.ExceptionListener;

/**
 * This class can be used together with {@link java.util.Timer} to periodically send broadcasts
 * into the network.
 */
class Broadcaster extends TimerTask {
    /**
     * The address used for broadcasting to the network.
     * The default is simply 255.255.255.255, but because broadcasting from a hotspot is a very
     * interesting use case, we have a whole lotta code dedicated to detecting being a hotspot
     */
    private final List<InetAddress> mBroadcastAddresses;

    /**
     * BREAK GLASS IN CASE OF EXCEPTION
     */
    private final ExceptionListener mExceptionListener;

    /**
     * The dataPort the discovery server must be listening on
     */
    private final int mRemoteDiscoveryPort;

    /**
     * description of this device as a json string in utf-8 byte form
     */
    private final JsonObject mThisDevice;

    /**
     * The socket that should be used for broadcasting information. Not owned by this class.
     */
    private DatagramSocket mSocket;

    /**
     * Create a new broadcaster.
     *
     * @param deviceName          name of this device
     * @param remoteDiscoveryPort required for sending broadcasts
     * @throws IOException when we cannot detect the correct broadcast address
     */
    Broadcaster(String deviceName, ExceptionListener exceptionListener, int remoteDiscoveryPort) throws IOException {
        mRemoteDiscoveryPort = remoteDiscoveryPort;
        mExceptionListener = exceptionListener;
        mBroadcastAddresses = getBroadcastAddresses();

        JsonObject deviceJson = new LedMatrix(deviceName).toJson();
        deviceJson.addProperty("message_type", "discovery");
        mThisDevice = deviceJson;
    }

    void setSocket(DatagramSocket socket) {
        try {
            mSocket = socket;
            mThisDevice.addProperty("discovery_port", mSocket.getLocalPort());
            socket.setBroadcast(true);
        } catch (SocketException e) {
            Log.w("broadcaster", "could not setBroadcast(true)");
            mExceptionListener.onException(this, e, "could not setSocket()");
        }
    }

    /**
     * Return a list of all useful broadcast addresses of this device. Called once in the constructor.
     */
    private List<InetAddress> getBroadcastAddresses() {
        List<InetAddress> resultList = new LinkedList<>();

        try {
            // iterate over all network interfaces
            Enumeration<NetworkInterface> networkInterfaces = NetworkInterface.getNetworkInterfaces();
            while (networkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = networkInterfaces.nextElement();

                // iterate over the interfaces addresses
                for (InterfaceAddress ifAddress : networkInterface.getInterfaceAddresses()) {
                    // avoid loopback interfaces
                    if (!ifAddress.getAddress().isLoopbackAddress()) {
                        // avoid weird connections
                        if (networkInterface.getDisplayName().contains("wlan0") ||
                                networkInterface.getDisplayName().contains("eth0") ||
                                networkInterface.getDisplayName().contains("ap0"))
                            // add to list of possible broadcast addresses
                            if (ifAddress.getBroadcast() != null)
                                resultList.add(ifAddress.getBroadcast());
                    }
                }
            }

        } catch (SocketException ex) {
            mExceptionListener.onException(this, ex, "Broadcaster: Could not find device ip addresses");
        }
        return resultList;
    }

    /**
     * sends a self identification broadcast
     */
    @Override
    public void run() {
        // send our identification data via broadcast
        try {
            byte[] thisDevice = mThisDevice.toString().getBytes("utf-8");
            for (InetAddress address : mBroadcastAddresses)
                mSocket.send(new DatagramPacket(thisDevice, thisDevice.length, address, mRemoteDiscoveryPort));
        } catch (IOException e) {
            mExceptionListener.onException(this, e, "Discovery: Broadcaster: Exception when trying to broadcast");
        }
    }
}