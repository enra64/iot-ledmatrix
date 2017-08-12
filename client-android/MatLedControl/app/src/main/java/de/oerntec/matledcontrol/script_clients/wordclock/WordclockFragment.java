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
import android.widget.Toast;

import com.pavelsikun.vintagechroma.ChromaDialog;
import com.pavelsikun.vintagechroma.IndicatorMode;
import com.pavelsikun.vintagechroma.OnColorSelectedListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;

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
    private int mCurrentChosenColor = Color.WHITE;


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
        mDrawingView.setColor(mCurrentChosenColor);
        mDrawingView.setChangeListener(this);

        mColorView = v.findViewById(R.id.fragment_wordclock_current_color_view);
        mColorView.setBackgroundColor(mCurrentChosenColor);
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
        return "_Wordclock";
    }

    @Override
    public void onMessage(JSONObject data) {
        // ignore incoming messages
        try {

            updateDrawingViewWords(data.getJSONArray("configuration"));
        } catch (JSONException e) {
            e.printStackTrace();
            Log.w("wordclockfragment", "indecipherable json data");
        }
    }

    private void updateDrawingViewWords(JSONArray lines) throws JSONException {
        final ArrayList<String[]> lineList = new ArrayList<>();
        for (int i = 0; i < lines.length(); i++) {
            JSONArray line = lines.getJSONArray(i);
            String[] lineArray = new String[line.length()];
            for (int j = 0; j < line.length(); j++)
                lineArray[j] = line.getString(j);
            lineList.add(lineArray);
        }

        if (getActivity() != null)
            getActivity().runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mDrawingView.setLines(lineList);
                }
            });
    }

    @Override
    public void onClick(View view) {
        new ChromaDialog.Builder()
                .initialColor(mCurrentChosenColor)
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

    @Override
    public void onColorCopied(@ColorInt int color) {
        mColorView.setBackgroundColor(color);
        mDrawingView.setColor(color);
        mCurrentChosenColor = color;
        Toast.makeText(WordclockFragment.this.getContext(), R.string.color_copied, Toast.LENGTH_SHORT).show();
    }


}
