package de.oerntec.matledcontrol.script_clients.camera;

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
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;
import de.oerntec.matledcontrol.script_clients.draw.GridDrawingView;

import static com.pavelsikun.vintagechroma.colormode.ColorMode.RGB;

public class CameraFragment extends Fragment implements ScriptFragmentInterface {

    @Override
    public String requestScript() {
        return null;
    }

    @Override
    public void onMessage(JSONObject data) {

    }
}
