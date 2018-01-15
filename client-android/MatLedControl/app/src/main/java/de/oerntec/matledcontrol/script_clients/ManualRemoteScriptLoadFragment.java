package de.oerntec.matledcontrol.script_clients;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.LayoutRes;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.ArrayList;
import java.util.List;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;
import de.oerntec.matledcontrol.networking.communication.MessageSender;

public class ManualRemoteScriptLoadFragment extends Fragment implements MatrixListener {
    /**
     * The MessageSender responsible for getting our messages out
     */
    private MessageSender mMessageSender;
    private ListView mList;
    private TextView mRefreshingText;
    private ProgressBar mRefreshingSpinner;

    public ManualRemoteScriptLoadFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @return A new instance of fragment ManualRemoteScriptLoadFragment.
     */
    public static ManualRemoteScriptLoadFragment newInstance() {
        ManualRemoteScriptLoadFragment fragment = new ManualRemoteScriptLoadFragment();
        Bundle args = new Bundle();
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_manual_script_load, container, false);
        mList = (ListView) v.findViewById(R.id.fragment_manual_script_load_list);
        mRefreshingSpinner = (ProgressBar) v.findViewById(R.id.fragment_manual_script_load_querying_spinner);
        mRefreshingText = (TextView) v.findViewById(R.id.fragment_manual_script_load_querying_text);
        return v;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof MessageSender) {
            mMessageSender = (MessageSender) context;
            requestScriptList();
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    /**
     * Request a list of available scripts from the script
     */
    private void requestScriptList() {
        JsonObject msg = new JsonObject();
        msg.addProperty("command", "request_script_list");
        mMessageSender.sendScriptData(msg);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mMessageSender = null;
    }

    @Override
    public String requestScript() {
        return "_ScriptLoader";
    }

    @Override
    public void onMessage(JsonObject data) {
        // convert script list to java list
        final JsonArray scriptList = data.get("script_list").getAsJsonArray();
        final List<String> scripts = new ArrayList<>(scriptList.size());
        for(int i = 0; i < scriptList.size(); i++)
            scripts.add(scriptList.get(i).getAsString());

        // display scripts, hide "querying..."
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                mList.setAdapter(new ScriptAdapter(getContext(), R.layout.script_list_item, scripts));
                mRefreshingSpinner.setVisibility(View.GONE);
                mRefreshingText.setVisibility(View.GONE);
            }
        });
    }

    private void requestScript(String script) {
        JsonObject msg = new JsonObject();
        msg.addProperty("command", "script_load_request");
        msg.addProperty("requested_script", script);
        mMessageSender.sendScriptData(msg);
    }

    private class ScriptAdapter extends ArrayAdapter<String> {

        ScriptAdapter(@NonNull Context context, @LayoutRes int resource, @NonNull List<String> objects) {
            super(context, resource, objects);
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View itemView, @NonNull ViewGroup parent) {
            View hmm = itemView;
            if (hmm == null) {
                LayoutInflater vi = LayoutInflater.from(getContext());
                hmm = vi.inflate(R.layout.script_list_item, null);
            }

            final String scriptName = getItem(position);

            if(scriptName != null){
                ((TextView) hmm.findViewById(R.id.large_text)).setText(scriptName);

                Button button = (Button) hmm.findViewById(R.id.button);

                button.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        ManualRemoteScriptLoadFragment.this.mMessageSender.requestScript(scriptName);
                    }
                });
            }

            return hmm;
        }
    }
}
