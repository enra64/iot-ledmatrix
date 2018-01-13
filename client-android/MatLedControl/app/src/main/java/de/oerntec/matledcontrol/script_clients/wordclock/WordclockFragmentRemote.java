package de.oerntec.matledcontrol.script_clients.wordclock;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.ColorInt;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Toast;

import com.pavelsikun.vintagechroma.ChromaDialog;
import com.pavelsikun.vintagechroma.IndicatorMode;
import com.pavelsikun.vintagechroma.OnColorSelectedListener;

import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.MatrixListener;

import static android.view.View.GONE;
import static com.pavelsikun.vintagechroma.colormode.ColorMode.RGB;

public class WordclockFragmentRemote extends Fragment implements MatrixListener, View.OnClickListener, DrawingView.UpdateRequiredListener {
    private MessageSender mMessageSender;

    /**
     * The view used to display the currently chosen color
     */
    private View mColorView;

    /**
     * The view that is displaying the drawn stuff to the user
     */
    private DrawingView mDrawingView;

    private View mLoadingScreen;

    private int mRandomizeColorsActionBarItemId;

    @ColorInt
    private int mCurrentChosenColor = Color.WHITE;


    public WordclockFragmentRemote() {
        // Required empty public constructor
    }

    public static WordclockFragmentRemote newInstance() {
        return new WordclockFragmentRemote();
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

        mLoadingScreen = v.findViewById(R.id.waiting_layout);

        mColorView = v.findViewById(R.id.fragment_wordclock_current_color_view);
        mColorView.setBackgroundColor(mCurrentChosenColor);

        // allow the randomize icon
        setHasOptionsMenu(true);

        return v;
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        super.onCreateOptionsMenu(menu, inflater);

        MenuItem randomizeColorsItem = menu.add(R.string.randomize_colors);
        randomizeColorsItem.setIcon(R.drawable.ic_randomize);
        randomizeColorsItem.setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM);
        mRandomizeColorsActionBarItemId = randomizeColorsItem.getItemId();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == mRandomizeColorsActionBarItemId) {
            mDrawingView.randomizeColors();
            onWordChanged();
        }
        return super.onOptionsItemSelected(item);
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
            loadWordsIntoDrawingView(data);
            loadWordColors(data);
        } catch (JSONException e) {
            e.printStackTrace();
            Log.w("wordclockfragment", "indecipherable json data");
        }
    }

    private void loadWordColors(final JSONObject data) throws JSONException {
        String messageType = data.getString("message_type");

        if (getActivity() != null && "wordclock_color_configuration".equals(messageType))
            getActivity().runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        mDrawingView.setColors(data);
                    } catch (JSONException e) {
                        e.printStackTrace();
                        Log.w("wc view parser", "bad json");
                        Toast.makeText(
                                WordclockFragmentRemote.this.getContext(),
                                R.string.device_communication_error,
                                Toast.LENGTH_LONG).show();
                    }
                    mLoadingScreen.setVisibility(GONE);
                }
            });
    }

    private void loadWordsIntoDrawingView(final JSONObject lines) throws JSONException {
        String messageType = lines.getString("message_type");

        if (getActivity() != null && "wordclock_configuration".equals(messageType))
            getActivity().runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        mDrawingView.setLines(lines);
                    } catch (JSONException e) {
                        e.printStackTrace();
                        Log.w("wc view parser", "bad json");
                        Toast.makeText(
                                WordclockFragmentRemote.this.getContext(),
                                R.string.device_communication_error,
                                Toast.LENGTH_LONG).show();
                    }
                    mLoadingScreen.setVisibility(GONE);
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
        Toast.makeText(WordclockFragmentRemote.this.getContext(), R.string.color_copied, Toast.LENGTH_SHORT).show();
    }


}
