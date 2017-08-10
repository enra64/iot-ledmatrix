package de.oerntec.matledcontrol.script_clients.wordclock;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.ColorInt;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.pavelsikun.vintagechroma.ChromaDialog;
import com.pavelsikun.vintagechroma.IndicatorMode;
import com.pavelsikun.vintagechroma.OnColorSelectedListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

import static com.pavelsikun.vintagechroma.colormode.ColorMode.RGB;

public class WordclockFragment extends Fragment implements ScriptFragmentInterface, View.OnClickListener, DrawingView.UpdateRequiredListener {
    private MessageSender mMessageSender;

    /**
     * The view used to display the currently chosen color
     */
    private View mColorView;

    /**
     * The view that is displaying the drawn stuff to the user
     */
    private DrawingView mDrawingView;

    @ColorInt
    private int DEFAULT_COLOR = Color.WHITE;


    public WordclockFragment() {
        // Required empty public constructor
    }

    public static WordclockFragment newInstance() {
        return new WordclockFragment();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_wordclock, container, false);
        Button colorButton = (Button) v.findViewById(R.id.fragment_wordclock_choose_color_button);
        colorButton.setOnClickListener(this);

        mDrawingView = (DrawingView) v.findViewById(R.id.fragment_wordclock_drawing_view);
        LedMatrix currentMatrix = mMessageSender.getCurrentMatrix();
        mDrawingView.setChangeListener(this);

        mColorView = v.findViewById(R.id.fragment_draw_current_color_view);
        mColorView.setBackgroundColor(DEFAULT_COLOR);
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
    public String requestScript() {
        return "_WordClock";
    }

    @Override
    public void onMessage(JSONObject data) {
        // ignore incoming messages
        try {
            final JSONArray wordLines = data.getJSONArray("lines");

        } catch (JSONException e) {
            e.printStackTrace();
            Log.w("wordclockfragment", "indecipherable json data");
        }
    }

    @Override
    public void onClick(View view) {
        new ChromaDialog.Builder()
                .initialColor(DEFAULT_COLOR)
                .colorMode(RGB)
                .indicatorMode(IndicatorMode.HEX)
                .onColorSelected(new OnColorSelectedListener() {
                    @Override
                    public void onColorSelected(@ColorInt int color) {
                        mDrawingView.setColor(color);
                        mColorView.setBackgroundColor(color);
                    }
                })
                .create()
                .show(getChildFragmentManager(), "ChromaDialog");
    }

    @Override
    public void onWordChanged() {
        mMessageSender.sendScriptData(mDrawingView.getAsJsonObject());
    }


}
