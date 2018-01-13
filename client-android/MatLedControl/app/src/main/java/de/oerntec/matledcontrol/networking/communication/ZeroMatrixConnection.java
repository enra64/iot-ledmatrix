package de.oerntec.matledcontrol.networking.communication;

import android.os.AsyncTask;
import android.support.annotation.Nullable;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;
import org.zeromq.ZMQException;

import java.nio.channels.ClosedSelectorException;
import java.util.concurrent.ExecutionException;

import de.oerntec.matledcontrol.networking.ConnectionTester;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;
import zmq.ZMQ;

/**
 * Created by arne on 16.03.17.
 */

public class ZeroMatrixConnection extends Thread {
    private org.zeromq.ZMQ.Context mContext;
    private org.zeromq.ZMQ.Socket mSocket;
    private final ScriptFragmentInterface mListener;
    private final ConnectionListener mConnectionListener;
    private final LedMatrix mMatrix;
    private ConnectionTester mConnectionTester;
    private volatile boolean mContinue = true;
    private static final int ZMQ_CONTEXT_TERMINATED = 156384765;


    public ZeroMatrixConnection(LedMatrix matrix, ScriptFragmentInterface listener, ConnectionListener connectionListener) {
        // listeners
        mListener = listener;
        mConnectionListener = connectionListener;

        // store connected networkdevice
        mMatrix = matrix;

        // zmq setup
        zmqConnect();

        // request connection with matrix
        sendMessage(new JSONObject(), "connection_request");

        // start self-thread
        start();
    }

    private void startConnectionHealthTester() {
        if (mConnectionTester == null)
            mConnectionTester = new ConnectionTester(this, 750);
    }

    private void zmqConnect() {
        mContext = org.zeromq.ZMQ.context(1);
        mSocket = mContext.socket(ZMQ.ZMQ_DEALER);
        boolean success;
        try {
            success = new ConnectTask(mSocket).execute("tcp://" + mMatrix.address + ":" + mMatrix.dataPort).get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
            success = false;
        }

        if(!success) {
            mConnectionListener.onMatrixDisconnected(mMatrix);
            if (mContinue)
                close();
        }
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

        boolean success;
        try {
            success = new SendMessageTask(mSocket).execute(message).get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
            success = false;
        }

        if (!success) {
            mConnectionListener.onMatrixDisconnected(mMatrix);
            if (mContinue)
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

                if (mConnectionTester != null)
                    mConnectionTester.setAlive();

                switch (messageType) {
                    case "connection_request_response":
                        mMatrix.width = recv_json.getInt("matrix_width");
                        mMatrix.height = recv_json.getInt("matrix_height");
                        mConnectionListener.onConnectionRequestResponse(mMatrix, recv_json.getBoolean("granted"));
                        startConnectionHealthTester();
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
                mConnectionListener.onMatrixDisconnected(mMatrix);
                if (mContinue)
                    close();
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
        if (mConnectionTester != null)
            mConnectionTester.stop();

        sendMessage(new JSONObject(), "shutdown_notification");
        // drop all messages soon if we cannot send
        mSocket.setLinger(10);

        // close down shop
        try {
            new CloseTask(mSocket).execute().get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
        mSocket.close();
    }

    public void terminate() {
        close();
        if (mContext != null){
            try {
                new TerminateTask(mContext).execute().get();
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }
    }

    private static class CloseTask extends AsyncTask<Void, Void, Void> {
        private final org.zeromq.ZMQ.Socket socket;

        CloseTask(org.zeromq.ZMQ.Socket socket) {
            this.socket = socket;
        }

        @Override
        protected Void doInBackground(Void... voids) {
            socket.close();
            return null;
        }
    }

    private static class TerminateTask extends AsyncTask<Void, Void, Void> {
        private final org.zeromq.ZMQ.Context context;

        TerminateTask(org.zeromq.ZMQ.Context  context) {
            this.context = context;
        }


        @Override
        protected Void doInBackground(Void... voids) {
            context.term();
            return null;
        }
    }

    private static class SendMessageTask extends AsyncTask<JSONObject, Void, Boolean> {
        private final org.zeromq.ZMQ.Socket socket;

        SendMessageTask(org.zeromq.ZMQ.Socket socket) {
            this.socket = socket;
        }

        @Override
        protected Boolean doInBackground(JSONObject... jsonObjects) {
            try {
                socket.send(jsonObjects[0].toString());
                return true;
            } catch (ArrayIndexOutOfBoundsException | ClosedSelectorException ignored) {
                return false;
            }
        }
    }

    private static class ConnectTask extends AsyncTask<String, Void, Boolean> {
        private final org.zeromq.ZMQ.Socket socket;

        ConnectTask(org.zeromq.ZMQ.Socket socket) {
            this.socket = socket;
        }

        @Override
        protected Boolean doInBackground(String... connectionParams) {
            String connectionString = connectionParams[0];
            try {
                socket.connect(connectionString);
            } catch (Exception e) {
                return false;
            }
            return true;
        }
    }
}
