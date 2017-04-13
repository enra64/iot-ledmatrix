package de.oerntec.matledcontrol.script_clients.draw;

import android.content.Context;
import android.os.Bundle;
import android.support.annotation.ColorInt;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.pavelsikun.vintagechroma.ChromaDialog;
import com.pavelsikun.vintagechroma.IndicatorMode;
import com.pavelsikun.vintagechroma.OnColorSelectedListener;

import org.json.JSONObject;

import de.oerntec.matledcontrol.R;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;

import static com.pavelsikun.vintagechroma.colormode.ColorMode.RGB;

public class DrawFragment extends Fragment implements ScriptFragmentInterface, View.OnClickListener, GridDrawingView.GridChangeListener {
    private MessageSender mMessageSender;

    /**
     * The view used to display the currently chosen color
     */
    private View mColorView;

    /**
     * The view that is displaying the drawn stuff to the user
     */
    private GridDrawingView mDrawingView;

    public DrawFragment() {
        // Required empty public constructor
    }

    public static DrawFragment newInstance() {
        return new DrawFragment();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View v = inflater.inflate(R.layout.fragment_draw, container, false);
        Button colorButton = (Button) v.findViewById(R.id.fragment_draw_choose_color_button);
        colorButton.setOnClickListener(this);

        mDrawingView = (GridDrawingView) v.findViewById(R.id.fragment_draw_drawing_view);
        LedMatrix currentMatrix = mMessageSender.getCurrentMatrix();
        mDrawingView.setGridSize(currentMatrix.width, currentMatrix.height);
        mDrawingView.setGridChangeListener(this);

        mColorView = v.findViewById(R.id.fragment_draw_current_color_view);
        mColorView.setBackgroundColor(mDrawingView.getColor());
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
        return "_SimpleDrawing";
    }

    @Override
    public void onMessage(JSONObject data) {
        // ignore incoming messages
    }

    @Override
    public void onClick(View view) {
        new ChromaDialog.Builder()
                .initialColor(mDrawingView.getColor())
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
    public void onGridChanged() {
        mMessageSender.sendScriptData(mDrawingView.getGridAsJsonObject());
    }
}
