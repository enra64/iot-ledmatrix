package de.oerntec.matledcontrol;

import android.content.Context;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.ColorInt;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.SeekBar;

import com.jraska.console.Console;
import com.pavelsikun.vintagechroma.ChromaDialog;
import com.pavelsikun.vintagechroma.IndicatorMode;
import com.pavelsikun.vintagechroma.OnColorSelectedListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;

import static com.pavelsikun.vintagechroma.colormode.ColorMode.RGB;

public class ScrollingTextFragment extends Fragment implements ScriptFragmentInterface, View.OnClickListener {
    private MessageSender mMessageSender;
    private ExceptionListener mExceptionListener;
    private Button mSendTextButton;
    private Button mChooseColorButton;
    private SeekBar mSpeedSeekbar;
    private EditText mTextEdit;

    public ScrollingTextFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @return A new instance of fragment ScrollingTextFragment.
     */
    public static ScrollingTextFragment newInstance() {
        return new ScrollingTextFragment();
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_scrolling_text, container, false);
        mSendTextButton = (Button) v.findViewById(R.id.fragment_scrolling_text_send_text_button);
        mChooseColorButton = (Button) v.findViewById(R.id.fragment_scrolling_text_color_button);
        mSpeedSeekbar = (SeekBar) v.findViewById(R.id.fragment_scrolling_text_seekbar);
        mTextEdit = (EditText) v.findViewById(R.id.fragment_scrolling_text_text_edit);

        mSendTextButton.setOnClickListener(this);
        mChooseColorButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new ChromaDialog.Builder()
                        .initialColor(Color.argb(255, 255, 255, 255))
                        .colorMode(RGB)
                        .indicatorMode(IndicatorMode.HEX)
                        .onColorSelected(new OnColorSelectedListener() {
                            @Override
                            public void onColorSelected(@ColorInt int color) {
                                JSONArray colorArray = new JSONArray();
                                colorArray.put(Color.red(color));
                                colorArray.put(Color.green(color));
                                colorArray.put(Color.blue(color));
                                try {
                                    JSONObject response = new JSONObject();
                                    response.put("command", "change_color");
                                    response.put("color", colorArray);
                                    mMessageSender.sendScriptData(response);
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                            }
                        })
                        .create()
                        .show(getChildFragmentManager(), "ChromaDialog");
            }
        });

        mSpeedSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                ScrollingTextFragment.this.onSpeedChanged(progress);
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });
        return v;
    }

    private void onSpeedChanged(int speed) {
        try {
            JSONObject response = new JSONObject();
            response.put("command", "change_speed");
            response.put("speed", speed);
            mMessageSender.sendScriptData(response);
        } catch (JSONException e) {
            e.printStackTrace();
        }
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
        return "_ScrollingText";
    }

    @Override
    public void onMessage(JSONObject data) {

    }

    @Override
    public void onClick(View v) {
        if(v.getId() == R.id.fragment_scrolling_text_send_text_button){
            try {
                JSONObject response = new JSONObject();
                response.put("command", "change_text");
                response.put("text", mTextEdit.getText().toString());
                mMessageSender.sendScriptData(response);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }
}
