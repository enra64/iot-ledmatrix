package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.zeromq.ZMQException;

import java.nio.channels.ClosedSelectorException;

import de.oerntec.matledcontrol.networking.ConnectionTester;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;
import zmq.ZMQ;

/**
 * Created by arne on 16.03.17.
 */

public class ZeroMatrixConnection extends Thread {
    private final org.zeromq.ZMQ.Context mContext;
    private final org.zeromq.ZMQ.Socket mSocket;
    private final ScriptFragmentInterface mListener;
    private final ConnectionListener mConnectionListener;
    private final LedMatrix mMatrix;
    private final ConnectionTester mConnectionTester;
    private volatile boolean mContinue = true;
    private static final int ZMQ_CONTEXT_TERMINATED = 156384765;


    public ZeroMatrixConnection(LedMatrix matrix, ScriptFragmentInterface listener, ConnectionListener connectionListener) {
        // listeners
        mListener = listener;
        mConnectionListener = connectionListener;

        // store connected networkdevice
        mMatrix = matrix;

        // zmq setup
        mContext = org.zeromq.ZMQ.context(1);
        mSocket = mContext.socket(ZMQ.ZMQ_DEALER);
        mSocket.connect("tcp://" + matrix.address + ":" + matrix.dataPort);

        // request connection with matrix
        sendMessage(new JSONObject(), "connection_request");
        start();

        mConnectionTester = new ConnectionTester(this, 750);
    }

    public void sendMessage(JSONObject message, @Nullable String messageType) {
        if (!message.has("message_type") && messageType == null)
            throw new AssertionError("Messages must have message_type set or a messageType must be given");

        if (messageType != null) {
            try {
                message.put("message_type", messageType);
            } catch (JSONException ignored) {
                throw new AssertionError("JSONException when adding messagetype");
            }
        }

        try {
            mSocket.send(message.toString());
        } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException ignored) {
            mConnectionListener.onMatrixDisconnected(mMatrix);
            close();
        }
    }

    @Override
    public void run() {
        while (mContinue) {
            String recv = "";
            try {
                recv = mSocket.recvStr();
                JSONObject recv_json = new JSONObject(recv);

                String messageType = recv_json.getString("message_type");

                mConnectionTester.setAlive();

                switch (messageType) {
                    case "connection_request_response":
                        mMatrix.width = recv_json.getInt("matrix_width");
                        mMatrix.height = recv_json.getInt("matrix_height");
                        mConnectionListener.onConnectionRequestResponse(mMatrix, recv_json.getBoolean("granted"));
                        break;
                    case "shutdown_notification":
                        mConnectionListener.onMatrixDisconnected(mMatrix);
                        break;
                    case "connection_test_response":
                        // handled already
                        break;
                    default:
                        mListener.onMessage(recv_json);
                }


            } catch (JSONException e) {
                Log.w("zmatrixcomm", "undecipherable JSON received: " + recv, e);
            } catch (ClosedSelectorException e) {
                Log.w("zmatrixcomm", "closed selector exception occurred!", e);
            } catch (zmq.ZError.IOException e) {
                Log.w("zmatrixcomm", "ZError.IOException occurred!", e);
            } catch (ArrayIndexOutOfBoundsException e) {
                Log.w("zmatrixcomm", "Array index out of bounds!", e);
            } catch (ZMQException e) {
                // if the context has been terminated here, a ZMQException about termination is to
                // be expected, but if it is something else we still want to log it.
                if (mContinue || e.getErrorCode() != ZMQ_CONTEXT_TERMINATED)
                    Log.w("zmatrixcomm", "ZMQException occurred!", e);
            }
        }
    }

    public void timedOut() {
        mConnectionListener.onMatrixDisconnected(mMatrix);
        close();
    }

    public void close() {
        mContinue = false;
        mConnectionTester.stop();
        sendMessage(new JSONObject(), "shutdown_notification");
        // drop all messages soon if we cannot send
        mSocket.setLinger(10);

        // close down shop
        mSocket.close();
    }

    public void terminate() {
        close();
        mContext.term();
    }
}
