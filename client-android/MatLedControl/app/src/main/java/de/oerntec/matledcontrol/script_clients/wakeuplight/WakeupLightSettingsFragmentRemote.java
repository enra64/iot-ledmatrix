package de.oerntec.matledcontrol.script_clients.wakeuplight;

import android.annotation.SuppressLint;
import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TimePicker;


import com.appyvet.materialrangebar.IRangeBarFormatter;
import com.appyvet.materialrangebar.RangeBar;

import org.json.JSONException;
import org.json.JSONObject;

import java.text.ParseException;
import java.util.Calendar;
import java.util.TimeZone;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;
import de.oerntec.matledcontrol.script_clients.draw.GridDrawingView;
@SuppressLint("DefaultLocale")
public class WakeupLightSettingsFragmentRemote extends Fragment implements MatrixListener {
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
    private RangeBar colorTempSeeker;

    private int lowerColorTemperatureLimit, upperColorTemperatureLimit;

    public WakeupLightSettingsFragmentRemote() {
        // Required empty public constructor
    }

    public static WakeupLightSettingsFragmentRemote newInstance() {
        return new WakeupLightSettingsFragmentRemote();
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
        blendInDurationSpinner.setSelection(1);

        wakeTimePicker = (TimePicker) v.findViewById(R.id.wakeup_light_time_picker);
        wakeTimePicker.setIs24HourView(true);
        wakeTimePicker.setOnTimeChangedListener(new TimePicker.OnTimeChangedListener() {
            @Override
            public void onTimeChanged(TimePicker view, int hourOfDay, int minute) {
                currentTimePickerHour = hourOfDay;
                currentTimePickerMinute = minute;
            }
        });

        colorTempSeeker = (RangeBar) v.findViewById(R.id.wakeup_light_color_temperature_seekbar);
        colorTempSeeker.setDrawTicks(false);
        colorTempSeeker.setRangePinsByIndices(800, 1800);
        colorTempSeeker.setFormatter(new IRangeBarFormatter() {

            @Override
            public String format(String value) {
                return String.format("%dK", Integer.valueOf(value) + 1090);
            }
        });
        colorTempSeeker.setOnRangeBarChangeListener(new RangeBar.OnRangeBarChangeListener() {
            @Override
            public void onRangeChangeListener(RangeBar rangeBar, int leftPinIndex, int rightPinIndex, String leftPinValue, String rightPinValue) {
                int lowerLimit = leftPinIndex < rightPinIndex ? leftPinIndex : rightPinIndex;
                int upperLimit = leftPinIndex >= rightPinIndex ? leftPinIndex : rightPinIndex;

                lowerLimit += 1090;
                upperLimit += 1090;

                if (lowerLimit != lowerColorTemperatureLimit)
                    onColorTemperatureChanged(lowerLimit);
                else
                    onColorTemperatureChanged(upperLimit);

                lowerColorTemperatureLimit = lowerLimit;
                upperColorTemperatureLimit = upperLimit;
            }
        });

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            currentTimePickerHour = wakeTimePicker.getHour();
            currentTimePickerMinute = wakeTimePicker.getMinute();
        } else {
            currentTimePickerHour = wakeTimePicker.getCurrentHour();
            currentTimePickerMinute = wakeTimePicker.getCurrentMinute();
        }

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
        JSONObject timeSetMessage = new JSONObject();
        try {
            timeSetMessage.put("command", "wakeuplight_set_time");
            timeSetMessage.put("wake_hour", currentTimePickerHour);
            timeSetMessage.put("wake_minute", currentTimePickerMinute);
            timeSetMessage.put("wake_timezone", TimeZone.getDefault().getID());
            timeSetMessage.put("blend_duration", currentBlendInDuration);
            timeSetMessage.put("lower_color_temperature", lowerColorTemperatureLimit);
            timeSetMessage.put("upper_color_temperature", upperColorTemperatureLimit);
        } catch (JSONException ignored) {
        }

        mMessageSender.sendScriptData(timeSetMessage);
    }

    private void onColorTemperatureChanged(int colorTemp) {
        JSONObject timeSetMessage = new JSONObject();
        try {
            timeSetMessage.put("command", "test_color_temperature");
            timeSetMessage.put("color_temperature", colorTemp);
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
