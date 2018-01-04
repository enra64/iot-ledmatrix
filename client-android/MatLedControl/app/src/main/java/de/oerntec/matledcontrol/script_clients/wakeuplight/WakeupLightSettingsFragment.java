package de.oerntec.matledcontrol.script_clients.wakeuplight;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TimePicker;

import org.json.JSONException;
import org.json.JSONObject;

import java.text.ParseException;
import java.util.Calendar;
import java.util.Date;
import java.util.TimeZone;
import java.util.logging.Logger;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.script_clients.draw.GridDrawingView;

public class WakeupLightSettingsFragment extends Fragment implements ScriptFragmentInterface {
    private MessageSender mMessageSender;

    /**
     * The view used to display the currently chosen color
     */
    private View mColorView;

    /**
     * The view that is displaying the drawn stuff to the user
     */
    private GridDrawingView mDrawingView;
    private Spinner blendInDurationSpinner;
    private TimePicker wakeTimePicker;
    private Button sendButton;
    private int currentTimePickerHour, currentTimePickerMinute, currentBlendInDuration;

    public WakeupLightSettingsFragment() {
        // Required empty public constructor
    }

    public static WakeupLightSettingsFragment newInstance() {
        return new WakeupLightSettingsFragment();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_wakeup_light_settings, container, false);

        blendInDurationSpinner = (Spinner) v.findViewById(R.id.wakeup_light_blendin_duration_spinner);
        blendInDurationSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                switch (position) {
                    case 0:
                        currentBlendInDuration = 15;
                        break;
                    case 1:
                        currentBlendInDuration = 30;
                        break;
                    case 2:
                        currentBlendInDuration = 45;
                        break;
                    case 3:
                        currentBlendInDuration = 60;
                        break;
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });

        wakeTimePicker = (TimePicker) v.findViewById(R.id.wakeup_light_time_picker);
        wakeTimePicker.setOnTimeChangedListener(new TimePicker.OnTimeChangedListener() {
            @Override
            public void onTimeChanged(TimePicker view, int hourOfDay, int minute) {
                currentTimePickerHour = hourOfDay;
                currentTimePickerMinute = minute;
            }
        });

        sendButton = (Button) v.findViewById(R.id.wakeup_light_send_button);
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onSendClicked();
            }
        });

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

    private void onSendClicked() {
        Calendar calendar = Calendar.getInstance(TimeZone.getDefault());
        calendar.set(Calendar.MINUTE, currentTimePickerMinute);
        calendar.set(Calendar.HOUR, currentTimePickerHour);

        Date wakeTime = calendar.getTime();

        JSONObject timeSetMessage = new JSONObject();
        try {
            timeSetMessage.put("command", "wakeuplight_set_time");
            timeSetMessage.put("wake_time", ISO8601DateParser.toString(wakeTime));
            timeSetMessage.put("blend_duration", currentBlendInDuration);
        } catch (JSONException ignored) {
        }

        mMessageSender.sendScriptData(timeSetMessage);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mMessageSender = null;
    }

    @Override
    public String requestScript() {
        return "_WakeUpLight";
    }

    @Override
    public void onMessage(JSONObject data) {
        try {
            Calendar calendar = Calendar.getInstance(TimeZone.getDefault());
            calendar.setTime(ISO8601DateParser.parse(data.getString("wakeTime")));
            wakeTimePicker.setCurrentHour(calendar.get(Calendar.HOUR));
            wakeTimePicker.setCurrentMinute(calendar.get(Calendar.MINUTE));

            switch (data.getInt("blend_duration")) {
                case 15:
                    blendInDurationSpinner.setSelection(0);
                    break;
                case 30:
                    blendInDurationSpinner.setSelection(1);
                    break;
                case 45:
                    blendInDurationSpinner.setSelection(2);
                    break;
                case 60:
                    blendInDurationSpinner.setSelection(3);
                    break;
            }

        } catch (ParseException | JSONException ignored) {
        }
    }
}
