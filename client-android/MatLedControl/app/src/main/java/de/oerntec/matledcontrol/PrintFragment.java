package de.oerntec.matledcontrol;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.communication.MessageListener;
import de.oerntec.matledcontrol.networking.communication.MessageSender;

public class PrintFragment extends Fragment implements MessageListener, View.OnClickListener {
    private MessageSender mMessageSender;

    private Button mSendButton;
    private EditText mSendEditText;
    private TextView mResponseView;

    public PrintFragment() {
        // Required empty public constructor
    }

    public static PrintFragment newInstance() {
        PrintFragment fragment = new PrintFragment();
        Bundle args = new Bundle();
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_print, container, false);
        mSendButton = (Button) v.findViewById(R.id.print_tester_send_button);
        mSendButton.setOnClickListener(this);
        mSendEditText = (EditText) v.findViewById(R.id.print_tester_send_to_server_edittext);
        mResponseView = (TextView) v.findViewById(R.id.print_tester_response_textview);
        return v;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof MessageSender) {
            mMessageSender = (MessageSender) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mMessageSender = null;
    }

    @Override
    public void onMessage(final JSONObject data) {
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                mResponseView.append(data.toString());
            }
        });
    }

    @Override
    public void onClick(View view) {
        try {
            mMessageSender.sendMessage(new JSONObject(mSendEditText.getText().toString()), "print_test");
            mSendEditText.setText("{\"\":}");
        } catch (JSONException e) {
            Toast.makeText(getContext(), "Invalid JSON encountered!", Toast.LENGTH_SHORT).show();
        }
    }
}
