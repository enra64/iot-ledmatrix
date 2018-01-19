package de.oerntec.matledcontrol.script_clients;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.google.gson.JsonObject;
import com.jraska.console.Console;

import de.oerntec.matledcontrol.ExceptionListener;
import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;
import de.oerntec.matledcontrol.networking.communication.MessageSender;

public class AdministrationFragmentRemote extends Fragment implements MatrixListener, View.OnClickListener {
    private MessageSender mMessageSender;
    private ExceptionListener mExceptionListener;
    private Button mRebootButton, mEchoButton, mRestartScriptButton;

    public AdministrationFragmentRemote() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @return A new instance of fragment AdministrationFragmentRemote.
     */
    public static AdministrationFragmentRemote newInstance() {
        AdministrationFragmentRemote fragment = new AdministrationFragmentRemote();
        Bundle args = new Bundle();
        fragment.setArguments(args);
        return fragment;
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_administration, container, false);
        mRebootButton = (Button) v.findViewById(R.id.admin_reboot_rpi_button);
        mRebootButton.setOnClickListener(this);
        mEchoButton = (Button) v.findViewById(R.id.admin_echo_test_button);
        mEchoButton.setOnClickListener(this);
        mRestartScriptButton = (Button) v.findViewById(R.id.admin_restart_matrix_control);
        mRestartScriptButton.setOnClickListener(this);
        return v;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof MessageSender && context instanceof ExceptionListener) {
            mMessageSender = (MessageSender) context;
            mExceptionListener = (ExceptionListener) context;

            Console.clear();
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mMessageSender = null;
        mExceptionListener = null;
    }

    @Override
    public String requestScript() {
        return "_Administration";
    }

    @Override
    public void onMessage(final JsonObject data) {
        Console.writeLine(data.toString());
    }

    @Override
    public void onClick(View view) {
        JsonObject response = new JsonObject();
        switch (view.getId()){
            case R.id.admin_echo_test_button:
                response.addProperty("command", "echo_test");
                break;
            case R.id.admin_reboot_rpi_button:
                Console.writeLine("Sending reboot command");
                response.addProperty("command", "reboot_rpi");
                break;
            case R.id.admin_shutdown_rpi_button:
                Console.writeLine("Sending reboot command");
                response.addProperty("command", "shutdown_rpi");
                break;
            case R.id.admin_restart_matrix_control:
                Console.writeLine("Sending restart command. Please re-connect manually.");
                response.addProperty("command", "restart_matrix_server");
                break;
        }
        mMessageSender.sendScriptData(response);
    }
}
