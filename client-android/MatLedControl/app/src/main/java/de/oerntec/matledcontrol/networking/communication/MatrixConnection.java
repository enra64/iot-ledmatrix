package de.oerntec.matledcontrol.networking.communication;


import android.os.Looper;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;

import de.oerntec.matledcontrol.BuildConfig;
import de.oerntec.matledcontrol.networking.discovery.ExceptionListener;
import de.oerntec.matledcontrol.networking.discovery.NetworkDevice;

/**
 * <p>
 * This class is able to both send and receive commands.
 * </p>
 * <p>
 * To receive commands with it, you must call {@link #start(NetworkDevice)} to start listening.
 * </p>
 * <p>
 * When you want to send commands with it, you need to configure the remote host using {@link #requestConnection(NetworkDevice)} )}
 * first.
 * </p>
 */
@SuppressWarnings("WeakerAccess")
public class MatrixConnection {
    /**
     * This listener must be notified of new messages arriving
     */
    private MessageListener mMessageListener;

    /**
     * The MessageListeningThread is responsible for listening to incoming commands
     */
    private MessageListeningThread mIncomingServer;

    /**
     * The listener that will be notified of exceptions
     */
    private ExceptionListener mExceptionListener;
    private NetworkDevice mRemote;

    /**
     * New control connection. The local listening port can be retrieved using {@link #getLocalPort()} after calling {@link #start(NetworkDevice)}.
     * The remote host and port may be set using {@link #requestConnection(NetworkDevice)}, data can then be sent there using {@link #sendJson(JSONObject)}
     *
     * @param listener the listener that will be notified of new messages arriving at this MatrixConnection
     */
    public MatrixConnection(MessageListener listener, ExceptionListener exceptionListener) throws IOException {
        mMessageListener = listener;
        mExceptionListener = exceptionListener;
    }

    /**
     * Retrieve the port this command connection is listening on
     */
    public int getLocalPort() {
        return mIncomingServer.getLocalPort();
    }

    /**
     * Assigns a new remote target for commands
     *
     * @param device remote device. Must have address and commandPort configured!
     * @throws UnknownHostException if the address was invalid
     */
    public void requestConnection(NetworkDevice device) throws UnknownHostException {
        mRemote = device;
        try {
            JSONObject connectionRequest = new JSONObject();
            connectionRequest.put("message_type", "connection_request");
            connectionRequest.put("data_port", mIncomingServer.getLocalPort());
            sendJson(connectionRequest);
        } catch (JSONException ignored) {
            Log.w("matrixconnection", "managed to get a jsonexception in a fresh json object. congrats.");
        }
    }

    /**
     * Use this function to send a command to the peer. It will assert that {@link #requestConnection(NetworkDevice)}} has been
     * used.
     */
    private void __sendJson(JSONObject object) {
        // ensure that the remote host is properly configured
        // note: this is the common project. it does not recognize androids BuildConfig.DEBUG.
        if (BuildConfig.DEBUG)
            if (!mRemote.remoteIsConfigured())
                throw new AssertionError("not configured for sending data");

        // this is a try-with-resources; it will automatically close its resources when finished, whatever happens.
        try (Socket outboundSocket = new Socket(mRemote.address, mRemote.port);
             DataOutputStream dos = new DataOutputStream(outboundSocket.getOutputStream());
             PrintWriter writer = new PrintWriter(dos)) {
            writer.println(object.toString());
        } catch (IOException e) {
            mExceptionListener.onException(this, e, "Could not send message!");
        }
    }

    /**
     * Use this function to send a command to the peer. It will assert that {@link #requestConnection(NetworkDevice)}} has been
     * used, and use a separate thread to avoid NetworkOnMainThread exceptions if necessary.
     */
    public void sendJson(final JSONObject object) {
        if (Looper.getMainLooper().getThread() == Thread.currentThread()) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    __sendJson(object);
                }
            }).start();
        } else {
            __sendJson(object);
        }
    }

    /**
     * Check whether the connection is running and configured
     *
     * @return true if the connection is listening and configured with a remote
     */
    public boolean isRunningAndConfigured() {
        return mIncomingServer.isRunning() && mRemote.remoteIsConfigured();
    }

    /**
     * Use this to gracefully stop operations
     */
    public void close() {
        if (mIncomingServer != null)
            mIncomingServer.shutdown();
        mIncomingServer = null;
    }

    /**
     * Use this to start listening for commands. Does not throw if called multiple times.
     *
     * @throws IOException if the port for command listening could not be bound
     */
    public void start(NetworkDevice remote) throws IOException {
        if (mIncomingServer == null) {
            mIncomingServer = new MessageListeningThread(this);
            mIncomingServer.start();

            mIncomingServer.setName("MessageListeningThread for " + remote.toString());
        }
    }

    /**
     * Called whenever our MessageListeningThread receives a command packet.
     *
     * @param origin the host which sent the command
     * @param data   the data we received
     */
    // this could have been implemented by MatrixConnection implementing the OnCommandListener, but because it is an
    // interface, it would have polluted our public surface with a method that is destined to be used by inner class
    // workings only.
    private void onCommand(InetAddress origin, JSONObject data) {
        if (origin.toString().equals(mRemote.address))
            mMessageListener.onMessage(mRemote, data);
        else
            Log.w("matrixConnection", "received message from unknown host");
    }

    /**
     * The {@link MessageListeningThread} class is used to listen to incoming commands.
     */
    private class MessageListeningThread extends Thread {
        /**
         * This listener is called whenever a new command object is received.
         */
        MatrixConnection mListener;

        /**
         * true if the server should continue running
         */
        private boolean mKeepRunning = true;

        /**
         * true while the server has not reached end of thread execution
         */
        private boolean mIsRunning = false;

        /**
         * Socket we use to listen
         */
        private ServerSocket mSocket;

        /**
         * A new MessageListeningThread instance created will open a socket on a random free port to grant listening for commands.
         *
         * @param listener this class will be called when a new command object is received
         * @throws IOException when an error occurs during binding of the socket
         */
        MessageListeningThread(MatrixConnection listener) throws IOException {
            super("MessageListeningThread without remote");

            // store listener
            mListener = listener;

            // get a socket now so we already know which port we will listen on
            mSocket = new ServerSocket(0);
        }

        /**
         * Returns the port the command server is listening on
         */
        int getLocalPort() {
            return mSocket.getLocalPort();
        }

        /**
         * Gracefully stop the server asap
         */
        void shutdown() {
            // kill the running server
            mKeepRunning = false;

            // try to close the socket
            if (mSocket != null)
                try {
                    mSocket.close();
                } catch (IOException e) {
                    // ignored, because we cannot handle it anyway
                }
        }

        /**
         * Listen on socket, forward commands
         */
        public void run() {
            // continue running till shutdown() is called
            mIsRunning = true;

            while (mKeepRunning) {
                // try-with-resource: close the socket after accepting the connection
                try (Socket connection = mSocket.accept()) {
                    connection.getInputStream();
                    // create an object input stream from the new connection
                    DataInputStream oinput = new DataInputStream(connection.getInputStream());

                    String test = oinput.readUTF();

                    // call listener with new command
                    mListener.onCommand(connection.getInetAddress(), new JSONObject(test));
                } catch (SocketException ignored) {
                    // this exception is thrown if #close() is called before #start(), but it is not relevant.
                } catch (IOException e) {
                    MatrixConnection.this.mExceptionListener.onException(MatrixConnection.this, e, "Could not listen for commands");
                } catch (JSONException e) {
                    MatrixConnection.this.mExceptionListener.onException(MatrixConnection.this, e, "Malformed JSON incoming");
                }
            }

            // try to close the socket after finishing running
            try {
                if (mSocket != null)
                    mSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

            mIsRunning = false;
        }

        /**
         * Returns true if we are currently in the listening loop
         *
         * @return true if we are currently in the listening loop
         */
        public boolean isRunning() {
            return mIsRunning;
        }
    }
}