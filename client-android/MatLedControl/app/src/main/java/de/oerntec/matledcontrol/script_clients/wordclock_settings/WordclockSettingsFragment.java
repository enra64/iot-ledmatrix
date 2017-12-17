package de.oerntec.matledcontrol.script_clients.wordclock_settings;

import android.content.Context;
import android.os.Bundle;
import android.support.constraint.ConstraintLayout;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;

public class WordclockSettingsFragment extends Fragment implements ScriptFragmentInterface, CompoundButton.OnCheckedChangeListener, SeekBar.OnSeekBarChangeListener {
    private MessageSender mMessageSender;

    private ConstraintLayout timeSettingsLayout;
    private SeekBar timeSettingsEnableAt;
    private SeekBar timeSettingsDisableAt;
    private CheckBox timeLimitsEnabled;
    private TextView timeSettingsDisableAtText;
    private TextView timeSettingsEnableAtText;

    public WordclockSettingsFragment() {
        // Required empty public constructor
    }

    public static WordclockSettingsFragment newInstance() {
        return new WordclockSettingsFragment();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_wordclock_settings, container, false);
        timeSettingsLayout = (ConstraintLayout) v.findViewById(R.id.settings_display_time_limits_layout);
        timeLimitsEnabled = (CheckBox) v.findViewById(R.id.settings_enable_display_time_limits);
        timeSettingsEnableAt = (SeekBar) v.findViewById(R.id.settings_enable_display_at);
        timeSettingsDisableAt = (SeekBar) v.findViewById(R.id.settings_disable_display_at);
        timeSettingsEnableAtText = (TextView) v.findViewById(R.id.wordclock_settings_enable_at_text);
        timeSettingsDisableAtText = (TextView) v.findViewById(R.id.wordclock_settings_disable_at_text);

        timeLimitsEnabled.setOnCheckedChangeListener(this);
        timeSettingsEnableAt.setOnSeekBarChangeListener(this);
        timeSettingsDisableAt.setOnSeekBarChangeListener(this);

        return v;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof MessageSender) {
            mMessageSender = (MessageSender) context;

            try {
                JSONObject com = new JSONObject();
                com.put("command", "retry sending wordclock config");
                mMessageSender.sendScriptData(com);
            } catch (JSONException e) {
                e.printStackTrace();
                Log.wtf("wordclockfragment", "ffs putting a string in a json object just crashed");
            }
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    private static void setViewAndChildrenEnabled(View view, boolean enabled) {
        view.setEnabled(enabled);
        if (view instanceof ViewGroup) {
            ViewGroup viewGroup = (ViewGroup) view;
            for (int i = 0; i < viewGroup.getChildCount(); i++) {
                View child = viewGroup.getChildAt(i);
                setViewAndChildrenEnabled(child, enabled);
            }
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mMessageSender = null;
    }

    @Override
    public String requestScript() {
        return "_Wordclock";
    }

    @Override
    public void onMessage(JSONObject data) {
        try {
            fromJson(data);
        } catch (JSONException e) {
            e.printStackTrace();
            Log.w("wordclockfragment", "indecipherable json data");
        }
    }

    private JSONObject toJson() throws JSONException {
        JSONObject result = new JSONObject();
        result.put("limit_display_time", timeLimitsEnabled.isChecked());
        result.put("display_time_start_h", timeSettingsEnableAt.getProgress());
        result.put("display_time_stop_h", timeSettingsDisableAt.getProgress());
        return result;
    }

    private void fromJson(final JSONObject data) throws JSONException {
        String messageType = data.getString("message_type");

        if (getActivity() != null && "wordclock_settings".equals(messageType))
            getActivity().runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        JSONObject settings = data.getJSONObject("settings");
                        boolean timeLimitsEnabled = settings.getBoolean("limit_display_time");
                        int enableAt = settings.getInt("display_time_start_h");
                        int disableAt = settings.getInt("display_time_stop_h");

                        WordclockSettingsFragment.this.timeLimitsEnabled.setChecked(timeLimitsEnabled);
                        setViewAndChildrenEnabled(timeSettingsLayout, timeLimitsEnabled);
                        WordclockSettingsFragment.this.timeSettingsEnableAt.setProgress(enableAt);
                        WordclockSettingsFragment.this.timeSettingsDisableAt.setProgress(disableAt);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }
            });
    }

    private void updateRemote() {
        try {
            JSONObject update = new JSONObject();
            update.put("command", "update_settings");
            update.put("settings", toJson());
            mMessageSender.sendScriptData(update);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /**
     * Called when the checked state of a compound button has changed.
     *
     * @param buttonView The compound button view whose state has changed.
     * @param isChecked  The new checked state of buttonView.
     */
    @Override
    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
        setViewAndChildrenEnabled(timeSettingsLayout, isChecked);
        updateRemote();
    }

    private void updateTimeLimitDisplay() {
        int enableAt = timeSettingsEnableAt.getProgress();
        int disableAt = timeSettingsDisableAt.getProgress();

        timeSettingsEnableAtText.setText(getResources().getString(R.string.enable_display_at, enableAt));
        timeSettingsDisableAtText.setText(getResources().getString(R.string.disable_display_at, disableAt));
    }

    /**
     * Notification that the progress level has changed. Clients can use the fromUser parameter
     * to distinguish user-initiated changes from those that occurred programmatically.
     */
    @Override
    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        updateRemote();
        updateTimeLimitDisplay();
    }

    /**
     * Notification that the user has started a touch gesture. Clients may want to use this
     * to disable advancing the seekbar.
     *
     * @param seekBar The SeekBar in which the touch gesture began
     */
    @Override
    public void onStartTrackingTouch(SeekBar seekBar) {

    }

    /**
     * Notification that the user has finished a touch gesture. Clients may want to use this
     * to re-enable advancing the seekbar.
     *
     * @param seekBar The SeekBar in which the touch gesture began
     */
    @Override
    public void onStopTrackingTouch(SeekBar seekBar) {

    }
}
