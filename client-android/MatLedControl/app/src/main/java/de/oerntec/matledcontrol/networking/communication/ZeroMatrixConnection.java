package de.oerntec.matledcontrol.networking.communication;

import android.support.annotation.Nullable;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.channels.ClosedChannelException;
import java.nio.channels.ClosedSelectorException;

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
    private volatile boolean mContinue = true;

    public ZeroMatrixConnection(LedMatrix matrix, ScriptFragmentInterface listener, ConnectionListener connectionListener){
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
    }

    public void sendMessage(JSONObject message, @Nullable String messageType) {
        if(!message.has("message_type") && messageType == null)
            throw new AssertionError("Messages must have message_type set or a messageType must be given");

        if(messageType != null)
            try { message.put("message_type", messageType); } catch (JSONException ignored) { }

        mSocket.send(message.toString());
    }

    @Override
    public void run() {
        while(mContinue) {
            String recv = "";
            try {
                recv = mSocket.recvStr();
                JSONObject recv_json = new JSONObject(recv);

                if (recv_json.getString("message_type").equals("connection_request_response")){
                    mMatrix.width = recv_json.getInt("matrix_width");
                    mMatrix.height = recv_json.getInt("matrix_height");
                    mConnectionListener.onConnectionRequestResponse(mMatrix, recv_json.getBoolean("granted"));
                } else if (recv_json.getString("message_type").equals("shutdown_notification")){
                    mConnectionListener.onMatrixDisconnected(mMatrix);
                }

                mListener.onMessage(recv_json);
            } catch (JSONException e) {
                Log.w("zmatrixcomm", "undecipherable JSON received " + recv);
            } catch (ClosedSelectorException e) {
                Log.w("zmatrixcomm", "closed selector exception occurred!");
                e.printStackTrace();
            } catch (zmq.ZError.IOException e) {
                Log.w("zmatrixcomm", "ZError.IOException occurred!");
                e.printStackTrace();
            }
        }
    }

    public void close() {
        mContinue = false;
        sendMessage(new JSONObject(), "shutdown_notification");
        // drop all messages soon if we cannot send
        mSocket.setLinger(10);

        // close down shop
        mSocket.close();
    }

    public void terminate(){
        close();
        mContext.term();
    }
}
