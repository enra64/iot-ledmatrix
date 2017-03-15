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
 * {@link DiscoveryFragmentInteractionListener} interface
 * to handle interaction events.
 * Use the {@link DiscoveryFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DiscoveryFragment extends Fragment implements OnDiscoveryListener, ExceptionListener {
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_DEVICE_NAME = "param1";
    private static final String ARG_SERVER_DISCOVERY_PORT = "param2";

    private String mDeviceName;
    private int mServerDiscoveryPort;

    private DiscoveryFragmentInteractionListener mListener;

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
    List<NetworkDevice> mServerList;

    /**
     * This discovery client enables us to find servers
     */
    DiscoveryClient mDiscovery;

    /**
     * Required empty public constructor
     */
    public DiscoveryFragment() {
    }

    /**
     * Use this factory to create a new {@link DiscoveryFragment}.
     * @param deviceName name of this device
     * @param discoveryPort the discovery port the server is listening on
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
                mListener.onServerClicked(mServerList.get(i));
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
            mListener = (DiscoveryFragmentInteractionListener) context;
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
                    mDiscovery = new DiscoveryClient(
                            DiscoveryFragment.this,
                            DiscoveryFragment.this,
                            mServerDiscoveryPort,
                            54122,
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
            setDiscoveringHintEnabled(true);
        }
    }

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
    public interface DiscoveryFragmentInteractionListener {
        /**
         * Called when the user tapped on a server
         * @param server identification of the clicked server
         */
        void onServerClicked(NetworkDevice server);
    }
}
