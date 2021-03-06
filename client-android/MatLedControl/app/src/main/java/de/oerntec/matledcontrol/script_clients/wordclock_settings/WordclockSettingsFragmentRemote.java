package de.oerntec.matledcontrol.script_clients.wordclock_settings;

import android.content.Context;
import android.os.Bundle;
import android.support.constraint.ConstraintLayout;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;

import com.google.gson.JsonObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;
import de.oerntec.matledcontrol.networking.communication.MessageSender;

public class WordclockSettingsFragmentRemote extends Fragment implements MatrixListener, CompoundButton.OnCheckedChangeListener, SeekBar.OnSeekBarChangeListener, AdapterView.OnItemSelectedListener {
    private MessageSender mMessageSender;

    private ConstraintLayout timeSettingsLayout;
    private SeekBar timeSettingsEnableAt;
    private SeekBar timeSettingsDisableAt;
    private CheckBox timeLimitsEnabled;
    private TextView timeSettingsDisableAtText;
    private TextView timeSettingsEnableAtText;
    private Spinner randomizationSpinner;
    private CheckBox randomizationEnabled;

    public WordclockSettingsFragmentRemote() {
        // Required empty public constructor
    }

    public static WordclockSettingsFragmentRemote newInstance() {
        return new WordclockSettingsFragmentRemote();
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


        randomizationEnabled = (CheckBox) v.findViewById(R.id.wordclock_settings_randomization_enabled);
        randomizationSpinner = (Spinner) v.findViewById(R.id.wordclock_settings_randomization_interval_spinner);

        randomizationEnabled.setOnCheckedChangeListener(this);
        randomizationSpinner.setOnItemSelectedListener(this);

        return v;
    }

    @Override
    public void onResume() {
        super.onResume();
        Context context = this.getContext();
        if (context instanceof MessageSender) {
            mMessageSender = (MessageSender) context;

            JsonObject com = new JsonObject();
            com.addProperty("command", "retry sending wordclock config");
            mMessageSender.sendScriptData(com);
        } else {
            throw new RuntimeException((context != null ? context.toString() : "???")
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
    public void onMessage(JsonObject data) {
        fromJson(data);
    }

    private JsonObject toJson() {
        JsonObject result = new JsonObject();
        result.addProperty("limit_display_time", timeLimitsEnabled.isChecked());
        result.addProperty("display_time_start_h", timeSettingsEnableAt.getProgress());
        result.addProperty("display_time_stop_h", timeSettingsDisableAt.getProgress());
        result.addProperty("randomization_enabled", randomizationEnabled.isChecked());
        result.addProperty("randomization_interval", randomizationSpinner.getSelectedItemPosition());
        return result;
    }

    private void fromJson(final JsonObject data) {
        String messageType = data.get("message_type").getAsString();

        if (getActivity() != null && "wordclock_configuration".equals(messageType))
            getActivity().runOnUiThread(() -> {
                JsonObject settings = data.get("settings").getAsJsonObject();
                boolean timeLimitsEnabled = settings.get("limit_display_time").getAsBoolean();
                int enableAt = settings.get("display_time_start_h").getAsInt();
                int disableAt = settings.get("display_time_stop_h").getAsInt();
                boolean enableRandomization = settings.get("randomization_enabled").getAsBoolean();
                int randomizationInterval = settings.get("randomization_interval").getAsInt();

                WordclockSettingsFragmentRemote.this.timeLimitsEnabled.setChecked(timeLimitsEnabled);
                setViewAndChildrenEnabled(timeSettingsLayout, timeLimitsEnabled);
                WordclockSettingsFragmentRemote.this.timeSettingsEnableAt.setProgress(enableAt);
                WordclockSettingsFragmentRemote.this.timeSettingsDisableAt.setProgress(disableAt);
                updateTimeLimitDisplay();
                WordclockSettingsFragmentRemote.this.randomizationEnabled.setChecked(enableRandomization);
                WordclockSettingsFragmentRemote.this.randomizationSpinner.setSelection(randomizationInterval);
            });
    }

    /**
     * Randomization interval spinner callbacks
     */
    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        updateRemote();
    }

    private void updateRemote() {
        JsonObject update = new JsonObject();
        update.addProperty("command", "update_settings");
        update.add("settings", toJson());
        mMessageSender.sendScriptData(update);
    }

    /**
     * Called when the checked state of a compound button has changed.
     *
     * @param buttonView The compound button view whose state has changed.
     * @param isChecked  The new checked state of buttonView.
     */
    @Override
    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
        if (buttonView.getId() == R.id.settings_enable_display_time_limits)
            setViewAndChildrenEnabled(timeSettingsLayout, isChecked);
        else if (buttonView.getId() == R.id.wordclock_settings_randomization_enabled)
            setViewAndChildrenEnabled(randomizationSpinner, isChecked);
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

    /**
     * Callback method to be invoked when the selection disappears from this
     * view. The selection can disappear for instance when touch is activated
     * or when the adapter becomes empty.
     *
     * @param parent The AdapterView that now contains no selected item.
     */
    @Override
    public void onNothingSelected(AdapterView<?> parent) {

    }
}
