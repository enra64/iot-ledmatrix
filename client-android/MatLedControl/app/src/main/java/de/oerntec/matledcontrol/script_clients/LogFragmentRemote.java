package de.oerntec.matledcontrol.script_clients;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.support.v4.content.ContextCompat;
import android.text.Spannable;
import android.text.style.ForegroundColorSpan;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;

public class LogFragmentRemote extends Fragment implements MatrixListener {
    private MessageSender mMessageSender;
    private TextView mConsole;

    public LogFragmentRemote() {
        // Required empty public constructor
    }

    public static LogFragmentRemote newInstance() {
        return new LogFragmentRemote();
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);
        requestLog();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_log, container, false);
        mConsole = (TextView) v.findViewById(R.id.fragment_log_console);
        mConsole.setTextSize(mConsole.getTextSize() * 0.8f);
        return v;
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        MenuItem refresh = menu.add(R.string.refresh);
        refresh.setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS);
        refresh.setIcon(R.drawable.ic_refresh);
        refresh.getIcon().setTint(ContextCompat.getColor(getContext(), android.R.color.white));
        refresh.setOnMenuItemClickListener(new MenuItem.OnMenuItemClickListener() {
            @Override
            public boolean onMenuItemClick(MenuItem menuItem) {
                requestLog();
                return true;
            }
        });
        super.onCreateOptionsMenu(menu, inflater);
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

    private void requestLog() {
        try {
            JSONObject com = new JSONObject();
            com.put("command", "give_me_log_pls");
            mMessageSender.sendScriptData(com);
        } catch (JSONException ignored) {
        }
    }

    @Override
    public String requestScript() {
        return "_LogReader";
    }

    public void appendLineToConsole(String text, int color) {
        int start = mConsole.getText().length();
        mConsole.append(text);
        int end = mConsole.getText().length();

        Spannable spannableText = (Spannable) mConsole.getText();
        spannableText.setSpan(new ForegroundColorSpan(color), start, end, 0);
    }

    private void displayLogArray(final JSONArray log) {
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Context context = getContext();
                for (int i = 0; i < log.length(); i++) {
                    try {
                        String line = log.getString(i);
                        int color = ContextCompat.getColor(context, R.color.log_info);

                        // choose a color appropriate for the log
                        if (line.contains("INFO"))
                            color = ContextCompat.getColor(context, R.color.log_info);
                        else if (line.contains("WARNING"))
                            color = ContextCompat.getColor(context, R.color.log_warning);
                        else if (line.contains("ERROR") || line.contains("Exception") || line.contains("Error"))
                            color = ContextCompat.getColor(context, R.color.log_error);
                        else if (line.contains("CRITICAL"))
                            color = ContextCompat.getColor(context, R.color.log_criticial);
                        else if (line.contains("DEBUG"))
                            color = ContextCompat.getColor(context, R.color.log_debug);
                        else if (line.contains("NOTSET"))
                            color = ContextCompat.getColor(context, R.color.log_notset);

                        appendLineToConsole(line, color);
                    } catch (JSONException e) {
                        Log.i("logfragment", "bad json");
                    }
                }
            }
        });
    }

    @Override
    public void onMessage(final JSONObject data) {
        try {
            boolean isArray = data.optJSONArray("log") != null;

            if (isArray) {
                displayLogArray(data.getJSONArray("log"));
            } else {
                getActivity().runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Context context = getContext();
                        try {
                            appendLineToConsole(data.getString("log"), ContextCompat.getColor(context, R.color.log_info));
                        } catch (JSONException e) {
                            Log.i("logfragment", "bad json");
                        }
                    }
                });
            }


        } catch (JSONException ignored) {
            Log.w("logfragment", "bad json");
        }
    }
}
