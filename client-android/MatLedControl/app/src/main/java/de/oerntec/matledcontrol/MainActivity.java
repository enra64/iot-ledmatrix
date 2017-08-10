package de.oerntec.matledcontrol;

import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.annotation.IdRes;
import android.support.annotation.NonNull;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import de.oerntec.matledcontrol.networking.communication.ScriptFragmentInterface;
import de.oerntec.matledcontrol.networking.communication.ConnectionListener;
import de.oerntec.matledcontrol.networking.communication.MessageSender;
import de.oerntec.matledcontrol.networking.communication.ZeroMatrixConnection;
import de.oerntec.matledcontrol.networking.discovery.LedMatrix;
import de.oerntec.matledcontrol.script_clients.AdministrationFragment;
import de.oerntec.matledcontrol.script_clients.LogFragment;
import de.oerntec.matledcontrol.script_clients.ManualScriptLoadFragment;
import de.oerntec.matledcontrol.script_clients.camera.Camera2BasicFragment;
import de.oerntec.matledcontrol.script_clients.draw.DrawFragment;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener, DiscoveryFragment.DiscoveryFragmentInteractionListener, ExceptionListener, ScriptFragmentInterface, ConnectionListener, MessageSender {

    /**
     * The port set for discovery
     */
    private static final int DISCOVERY_PORT = 54123;

    /**
     * The connection instance we use for communicating with the matrix
     */
    private ZeroMatrixConnection mConnection;

    /**
     * The currently active fragment, if it implements the ScriptFragmentInterface interface, or null.
     */
    private ScriptFragmentInterface mCurrentScriptFragment;

    /**
     * The matrix we currently are connected to, or null.
     */
    private LedMatrix mCurrentMatrix = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // set toolbar
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // init drawer layout
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this,
                drawer,
                toolbar,
                R.string.navigation_drawer_open,
                R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        // init navigation view
        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        // load discovery fragment per default
        loadFragment(R.id.device_discovery);
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
        String lastMatrix = prefs.getString(getString(R.string.sp_last_connected_device), null);

        if (lastMatrix != null) {
            try {
                // try to reconnect to the given matrix
                LedMatrix lastDevice = LedMatrix.fromJsonString(lastMatrix);
                connectToMatrix(lastDevice);
            } catch (JSONException e) {
                Log.w("main", "could not parse stored last matrix!");
            }
        }
    }


    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        loadFragment(item.getItemId());
        return true;
    }

    private void loadFragment(@IdRes int id) {
        // thx http://chrisrisner.com/Using-Fragments-with-the-Navigation-Drawer-Activity
        Fragment fragment = null;
        switch (id) {
            case R.id.drawing:
                fragment = DrawFragment.newInstance();
                break;
            case R.id.device_discovery:
                fragment = DiscoveryFragment.newInstance(Build.MODEL, DISCOVERY_PORT);
                break;
            case R.id.camera:
                fragment = Camera2BasicFragment.newInstance();
                break;
            case R.id.administration:
                fragment = AdministrationFragment.newInstance();
                break;
            case R.id.manual_script_load:
                fragment = ManualScriptLoadFragment.newInstance();
                break;
            case R.id.log_viewer:
                fragment = LogFragment.newInstance();
                break;
            case R.id.scrolling_text:
                fragment = ScrollingTextFragment.newInstance();
                break;
            default:
                Log.w("ledmat:main", "unknown menu item clicked");
        }

        //noinspection ConstantConditions // according to AS, fragment is always null or always instanceof ScriptFragmentInterface, both of which seems unlikely
        if (!(fragment instanceof ScriptFragmentInterface))
            throw new AssertionError("All main fragments must implement ScriptFragmentInterface!");

        // enable later callbacks
        mCurrentScriptFragment = (ScriptFragmentInterface) fragment;

        // the discovery fragment requests no script
        if (!(fragment instanceof DiscoveryFragment))
            requestScript(mCurrentScriptFragment.requestScript());

        // actually load the fragment
        FragmentManager fragmentManager = getSupportFragmentManager();
        fragmentManager.beginTransaction().replace(R.id.main_fragment_container, fragment).commit();

        // finally, close the drawer
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
    }


    /**
     * Called from within this activity to request a connection to the specified matrix
     *
     * @param matrix connection request target
     */
    private void connectToMatrix(LedMatrix matrix) {
        if (mConnection != null)
            mConnection.close();
        mConnection = new ZeroMatrixConnection(matrix, this, this);
    }

    /**
     * Call this to save a matrix as the one that was last connected to
     */
    private void saveMatrix(LedMatrix matrix) {
        try {
            SharedPreferences.Editor prefs = PreferenceManager.getDefaultSharedPreferences(this).edit();
            prefs.putString(getString(R.string.sp_last_connected_device), matrix.toJsonString()).apply();
        } catch (JSONException e) {
            onException(this, e, "Could not serialize matrix for storage");
        }
    }

    /**
     * Called when the user clicks a matrix in the discovery fragment
     *
     * @param server identification of the clicked server
     */
    @Override
    public void onDiscoveredMatrixClicked(final LedMatrix server) {
        connectToMatrix(server);
    }

    /**
     * Can be called to signal exceptions across threads
     *
     * @param origin    the instance (or, if it is a hidden instance, the known parent) that produced the exception
     * @param exception the exception that was thrown
     * @param info      additional information to help identify the problem
     */
    @Override
    public void onException(Object origin, Exception exception, String info) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(R.string.error_occurred);
        builder.setMessage(info);
        builder.setPositiveButton(R.string.ok, null);
        builder.show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mConnection.terminate();
    }

    /**
     * Get an LedMatrix object containing all known information about the matrix the MessageSender
     * is currently connected to
     */
    @Override
    public LedMatrix getCurrentMatrix() {
        return mCurrentMatrix;
    }

    /**
     * send the json object as script data to the currently running script.
     * @param json json data to be wrapped in a script_data message
     */
    @Override
    public void sendScriptData(JSONObject json) {
        // avoid trying to send without a valid connection
        if(mConnection == null)
            return;

        JSONObject wrapper = new JSONObject();
        try {
            wrapper.put("script_data", json);
        } catch (JSONException e) {
            Log.w("mainactivity", "could not send message for script");
        }

        mConnection.sendMessage(wrapper, "script_data");
    }

    @Override
    public void requestScript(String scriptName) {
        try {
            mConnection.sendMessage(new JSONObject("{requested_script: " + scriptName + "}"), "script_load_request");
        } catch (JSONException ignored) {
        } catch (NullPointerException e){
            Toast.makeText(this, getString(R.string.err_could_not_communicate), Toast.LENGTH_SHORT).show();
            Log.i("mainactivity", "could not request script " + scriptName);
        }
    }


    /**
     * This would be the script the fragment wants the server to load, except this is not a script fragment,
     * but the mainactivity, so we dont want to load any script.
     */
    @Override
    public String requestScript() {
        throw new AssertionError("stub!");
    }

    /**
     * Called when the {@link ZeroMatrixConnection} receives a message that it cannot handle
     * (like for example a matrix disconnect). In an ideal world, all such messages are script data.
     *
     * @param data message content
     */
    @Override
    public void onMessage(JSONObject data) {
        mCurrentScriptFragment.onMessage(data);
    }


    /**
     * Called when matrix answered the connection request
     *
     * @param matrix  the matrix we wanted to connect to
     * @param granted true if the connection was granted, false otherwise
     */
    @Override
    public void onConnectionRequestResponse(final LedMatrix matrix, boolean granted) {
        if (granted) {
            saveMatrix(matrix);

            mCurrentMatrix = matrix;

            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    //noinspection ConstantConditions // a SupportActionBar should be set, see onCreate
                    getSupportActionBar().setSubtitle("Connected to " + matrix.name);
                    if(mCurrentScriptFragment instanceof DiscoveryFragment)
                        ((DiscoveryFragment) mCurrentScriptFragment).refreshMatrices();
                }
            });
        } else {
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle(R.string.device_denied_connection_request_title);
            builder.setMessage(R.string.device_denied_connection_request_msg);
            builder.setPositiveButton(R.string.ok, null);
            builder.show();
        }
    }

    /**
     * Called when matrix has sent a shutdown notification.
     *
     * @param matrix the matrix that went offline
     */
    @Override
    public void onMatrixDisconnected(final LedMatrix matrix) {
        mCurrentMatrix = null;

        if(mConnection != null)
            mConnection.close();
        mConnection = null;

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (matrix != null)
                    Toast.makeText(MainActivity.this, matrix.name + " lost connection", Toast.LENGTH_SHORT).show();
                //noinspection ConstantConditions // a SupportActionBar should be set, see onCreate
                getSupportActionBar().setSubtitle(null);
                loadFragment(R.id.device_discovery);
            }
        });
    }
}
