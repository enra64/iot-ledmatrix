package de.oerntec.matledcontrol.script_clients.camera;

import android.support.v4.app.Fragment;

import com.google.gson.JsonObject;

import de.oerntec.matledcontrol.networking.communication.MatrixListener;

public class CameraFragmentRemote extends Fragment implements MatrixListener {

    @Override
    public String requestScript() {
        return null;
    }

    @Override
    public void onMessage(JsonObject data) {

    }
}
