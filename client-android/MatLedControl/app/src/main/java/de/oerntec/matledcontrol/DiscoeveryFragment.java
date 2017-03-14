package de.oerntec.matledcontrol;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;

import java.io.IOException;
import java.security.InvalidParameterException;
import java.util.List;

import de.oerntec.matledcontrol.networking.DiscoveryClient;
import de.oerntec.matledcontrol.networking.ExceptionListener;
import de.oerntec.matledcontrol.networking.NetworkDevice;
import de.oerntec.matledcontrol.networking.OnDiscoveryListener;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link DiscoeveryFragment.OnFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link DiscoeveryFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DiscoeveryFragment extends Fragment implements OnDiscoveryListener, ExceptionListener {
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_DEVICE_NAME = "param1";
    private static final String ARG_SERVER_DISCOVERY_PORT = "param2";

    private String mDeviceName;
    private int mServerDiscoveryPort;

    private OnFragmentInteractionListener mListener;

    /**
     * The button we use for discovery
     */
    Button mStartDiscoveryButton;

    /**
     * The ListView we use to display available servers
     */
    ListView mPossibleConnections;

    /**
     * List of current servers
     */
    List<NetworkDevice> mServerList;

    /**
     * This discovery client enables us to find servers
     */
    DiscoveryClient mDiscovery;

    /**
     * Required empty public constructor
     */
    public DiscoeveryFragment() {
    }

    /**
     * Use this factory to create a new {@link DiscoeveryFragment}.
     * @param deviceName name of this device
     * @param discoveryPort the discovery port the server is listening on
     * @return new instance of {@link DiscoeveryFragment}
     */
    public static DiscoeveryFragment newInstance(String deviceName, int discoveryPort) {
        DiscoeveryFragment fragment = new DiscoeveryFragment();
        Bundle args = new Bundle();
        args.putString(ARG_DEVICE_NAME, deviceName);
        args.putInt(ARG_SERVER_DISCOVERY_PORT, discoveryPort);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mDeviceName = getArguments().getString(ARG_DEVICE_NAME);
            mServerDiscoveryPort = getArguments().getInt(ARG_SERVER_DISCOVERY_PORT);


            mPossibleConnections.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                    if(mServerList.size() <= i)
                        return;

                    NetworkDevice server = new NetworkDevice(mServerList.get(i).name, mServerList.get(i).discoveryPort, mServerList.get(i).dataPort, mServerList.get(i).address);

                    mListener.onServerClicked(server);

                    // stop the discovery server
                    mDiscovery.close();
                }
            });
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View inflated = inflater.inflate(R.layout.fragment_discoevery, container, false);
        mPossibleConnections = (ListView) inflated.findViewById(R.id.discovery_fragment_server_list);
        return inflated;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnFragmentInteractionListener) {
            mListener = (OnFragmentInteractionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnFragmentInteractionListener");
        }
    }

    @Override
    public void onResume() {
        super.onResume();
        startDiscovery();
    }

    @Override
    public void onPause() {
        super.onPause();
        stopDiscovery();
    }

    /**
     * Start (or restart) the discovery server gracefully
     */
    public void startDiscovery() {
        // only start new discovery if not running yet
        if (mDiscovery == null || !mDiscovery.isRunning()) {
            // create a new discovery thread, if this one already completed
            if (mDiscovery == null || mDiscovery.hasRun()) {
                try {
                    // create discovery client
                    mDiscovery = new DiscoveryClient(
                            DiscoeveryFragment.this,
                            DiscoeveryFragment.this,
                            mServerDiscoveryPort,
                            mDeviceName);
                    // this is a network problem
                } catch (IOException e) {
                    onException(this, e, "DiscoveryActivity: could not create DiscoveryClient");
                }
                // these exceptions are thrown if the port is invalid, so we do not want to continue
                catch (NumberFormatException | InvalidParameterException e) {
                    return;
                }
            }

            // start discovery
            mDiscovery.start();
        }
    }

    /**
     * Stop discovering
     */
    private void stopDiscovery() {
        if (mDiscovery != null)
            mDiscovery.close();
    }

    @Override
    public void onServerListUpdated(List<NetworkDevice> servers) {
        mServerList = servers;             //save server names and ips for further use

        final String[] stringNames = new String[servers.size()];

        for (int i = 0; i < servers.size(); i++)
            stringNames[i] = servers.get(i).name;

        // since this is called from a separate thread, we must use runOnUiThread to update the lits
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                ArrayAdapter<String> serverNameAdapter = new ArrayAdapter<>(getContext(), android.R.layout.simple_list_item_1, stringNames);
                mPossibleConnections.setAdapter(serverNameAdapter);
            }
        });
    }

    @Override
    public void onException(Object origin, Exception exception, String info) {
        Log.e(origin.toString(), info, exception);
        exception.printStackTrace();
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnFragmentInteractionListener {
        /**
         * Called when the user tapped on a server
         * @param server identification of the clicked server
         */
        void onServerClicked(NetworkDevice server);
    }
}
