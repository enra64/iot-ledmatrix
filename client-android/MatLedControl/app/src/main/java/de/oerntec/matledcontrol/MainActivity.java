package de.oerntec.matledcontrol;

import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.preference.PreferenceManager;
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
    private ScriptFragmentInterface mCurrentMessageDigestor;

    /**
     * The matrix we currently are connected to, or null.
     */
    private LedMatrix mCurrentMatrix = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // load discovery fragment per default
        FragmentManager fragmentManager = getSupportFragmentManager();
        DiscoveryFragment fragment = getDiscoveryFragment();
        mCurrentMessageDigestor = fragment;
        fragmentManager.beginTransaction().replace(R.id.main_fragment_container, fragment).commit();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
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
        String lastMatrix = prefs.getString(getString(R.string.sp_last_connected_matrix), null);

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

    private DiscoveryFragment getDiscoveryFragment() {
        return DiscoveryFragment.newInstance(Build.MODEL, DISCOVERY_PORT);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks here.
        // thx http://chrisrisner.com/Using-Fragments-with-the-Navigation-Drawer-Activity
        Fragment fragment = null;
        switch (item.getItemId()) {
            case R.id.simple_drawing:
                fragment = DrawFragment.newInstance();
                break;
            case R.id.choose_server:
                fragment = getDiscoveryFragment();
                break;
            case R.id.camera:
                fragment = Camera2BasicFragment.newInstance();
                break;
            default:
                Log.w("ledmat:main", "unknown menu item clicked");
        }

        //noinspection ConstantConditions // according to AS, fragment is always null or always instanceof ScriptFragmentInterface, both of which seems unlikely
        if (!(fragment instanceof ScriptFragmentInterface))
            throw new AssertionError("All main fragments must implement messagelistener!");

        mCurrentMessageDigestor = (ScriptFragmentInterface) fragment;

        // the discovery fragment requests no script
        if(!(fragment instanceof DiscoveryFragment)) {
            String requestedScript = mCurrentMessageDigestor.requestScript();
            try {
                mConnection.sendMessage(new JSONObject("{requested_script: "+ requestedScript + "}"), "script_load_request");
            } catch (JSONException ignored) {
            }
        }

        FragmentManager fragmentManager = getSupportFragmentManager();
        fragmentManager.beginTransaction().replace(R.id.main_fragment_container, fragment).commit();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
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
            prefs.putString(getString(R.string.sp_last_connected_matrix), matrix.toJsonString()).apply();
        } catch (JSONException e) {
            onException(this, e, "Could not serialize matrix for storage");
        }
    }

    /**
     * Called when the user clicks a matrix in the discovery fragment
     * @param server identification of the clicked server
     */
    @Override
    public void onDiscoveredMatrixClicked(final LedMatrix server) {
        Toast.makeText(this, "chose server " + server.name, Toast.LENGTH_LONG).show();

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(R.string.connect_to_matrix);
        builder.setMessage(R.string.connect_to_matrix_message);
        builder.setPositiveButton(getString(R.string.yes), new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialogInterface, int i) {
                connectToMatrix(server);
            }
        });
        builder.setNegativeButton(getString(R.string.no), null);
        builder.show();
    }

    /**
     * Can be called to signal exceptions across threads
     * @param origin    the instance (or, if it is a hidden instance, the known parent) that produced the exception
     * @param exception the exception that was thrown
     * @param info additional information to help identify the problem
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
                }
            });
        } else {
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle(R.string.matrix_denied_title);
            builder.setMessage(R.string.matrix_denied_msg);
            builder.setPositiveButton(R.string.ok, null);
            builder.show();
        }
    }

    @Override
    public void onMatrixDisconnected(LedMatrix matrix) {
        mCurrentMatrix = null;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                //noinspection ConstantConditions // a SupportActionBar should be set, see onCreate
                getSupportActionBar().setSubtitle(null);
            }
        });
        mConnection.close();
        mConnection = null;
    }

    @Override
    public LedMatrix getCurrentMatrix() {
        return mCurrentMatrix;
    }

    @Override
    public void sendScriptData(JSONObject json) {
        JSONObject wrapper = new JSONObject();
        try {
            wrapper.put("script_data", json);
        } catch (JSONException e) {
            Log.w("mainactivity", "could not send message for script");
        }

        mConnection.sendMessage(wrapper, "script_data");
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
     * @param data message content
     */
    @Override
    public void onMessage(JSONObject data) {
        mCurrentMessageDigestor.onMessage(data);
    }
}
