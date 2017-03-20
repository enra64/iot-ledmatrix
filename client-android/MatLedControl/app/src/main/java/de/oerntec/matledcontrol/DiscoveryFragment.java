package de.oerntec.matledcontrol;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.security.InvalidParameterException;
import java.util.List;

import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.networking.discovery.DiscoveryClient;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;
import de.oerntec.matledcontrol.networking.discovery.OnDiscoveryListener;


/**
 * A simple {@link Fragment} subclass.
 * Activities that contain this fragment must implement the
 * {@link DiscoveryFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link DiscoveryFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DiscoveryFragment extends Fragment implements OnDiscoveryListener, ExceptionListener, ScriptFragmentInterface {
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_DEVICE_NAME = "param1";
    private static final String ARG_SERVER_DISCOVERY_PORT = "param2";

    private String mDeviceName;
    private int mServerDiscoveryPort;

    private DiscoveryFragmentInteractionListener mDiscoveryListener;

    /**
     * ProgressBar hinting at running discovery
     */
    ProgressBar mDiscoveryProgressBar;

    /**
     * TextView hinting at running discovery
     */
    TextView mDiscoveryTextView;

    /**
     * The ListView we use to display available servers
     */
    ListView mPossibleConnections;

    /**
     * List of current servers
     */
    List<LedMatrix> mServerList;

    /**
     * This discovery client enables us to find servers
     */
    DiscoveryClient mDiscovery;

    /**
     * Listener for concurrent exceptions
     */
    private ExceptionListener mExceptionListener;

    /**
     * Required empty public constructor
     */
    public DiscoveryFragment() {
    }

    /**
     * Use this factory to create a new {@link DiscoveryFragment}.
     * @param deviceName name of this device
     * @param discoveryPort the discovery dataPort the server is listening on
     * @return new instance of {@link DiscoveryFragment}
     */
    @SuppressWarnings("unused")
    public static DiscoveryFragment newInstance(String deviceName, int discoveryPort) {
        DiscoveryFragment fragment = new DiscoveryFragment();
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
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        mPossibleConnections.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                mDiscoveryListener.onDiscoveredMatrixClicked(mServerList.get(i));
            }
        });
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View inflated = inflater.inflate(R.layout.fragment_discovery, container, false);
        mPossibleConnections = (ListView) inflated.findViewById(R.id.discovery_fragment_server_list);
        mDiscoveryProgressBar = (ProgressBar) inflated.findViewById(R.id.discovery_fragment_progress_bar);
        mDiscoveryTextView = (TextView) inflated.findViewById(R.id.discovery_fragment_searching_text);
        return inflated;
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof DiscoveryFragmentInteractionListener) {
            mDiscoveryListener = (DiscoveryFragmentInteractionListener) context;
            mExceptionListener = (ExceptionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement DiscoveryFragmentInteractionListener");
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
                    mDiscovery = new DiscoveryClient(mDeviceName, mServerDiscoveryPort, this, this);
                    // this is a network problem
                } catch (IOException | JSONException | NumberFormatException | InvalidParameterException e) {
                    onException(this, e, "DiscoveryActivity: could not create DiscoveryClient because of: " + e.getClass().toString());
                }
            }

            // start discovery
            mDiscovery.start();
            setDiscoveringHintEnabled(true);
        }
    }

    /**
     * Show or hide a spinning indicator and a text to signal the user that we are searching for matrices
     */
    private void setDiscoveringHintEnabled(boolean enable) {
        mDiscoveryProgressBar.setVisibility(enable ? View.VISIBLE : View.GONE);
        mDiscoveryTextView.setVisibility(enable ? View.VISIBLE : View.GONE);
    }

    /**
     * Stop discovering
     */
    private void stopDiscovery() {
        if (mDiscovery != null)
            mDiscovery.close();
        setDiscoveringHintEnabled(false);
    }

    /**
     * Called by the ServerList in DiscoveryClient when a new server has responded
     * @param servers list of current servers
     */
    @Override
    public void onServerListUpdated(List<LedMatrix> servers) {
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
        mExceptionListener.onException(origin, exception, info);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mDiscoveryListener = null;
        mExceptionListener = null;
    }

    @Override
    public String requestScript() {
        throw new AssertionError("The discovery fragment does not need to load a script");
    }

    @Override
    public void onMessage(JSONObject data) {
        Log.w("discoveryfragment", "received unexpected message");
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
    interface DiscoveryFragmentInteractionListener {
        /**
         * Called when the user tapped on a server
         * @param server identification of the clicked server
         */
        void onDiscoveredMatrixClicked(LedMatrix server);
    }
}