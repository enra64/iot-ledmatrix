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
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import de.oerntec.matledcontrol.networking.communication.MatrixConnection;
import de.oerntec.matledcontrol.networking.communication.MessageListener;
import de.oerntec.matledcontrol.networking.discovery.ExceptionListener;
import de.oerntec.matledcontrol.networking.discovery.NetworkDevice;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener, DiscoveryFragment.DiscoveryFragmentInteractionListener, ExceptionListener, MessageListener {

    private static final int DISCOVERY_PORT = 54123;

    private MatrixConnection mConnection;

    private MessageListener mCurrentMessageDigestor;

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

        if(lastMatrix != null){
            try {
                // try to reconnect to the given matrix
                NetworkDevice lastDevice = NetworkDevice.fromJsonString(lastMatrix);
                connectToMatrix(lastDevice);
            } catch (JSONException e) {
                Log.w("main", "could not parse stored last matrix!");
            }
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
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
                return true;
            case R.id.choose_server:
                fragment = getDiscoveryFragment();
                break;
            default:
                Log.w("ledmat:main", "unknown menu item clicked");
        }

        //noinspection ConstantConditions // according to AS, fragment is always null or always instanceof MessageListener, both of which seems unlikely
        if (!(fragment instanceof MessageListener))
            throw new AssertionError("All main fragments must implement messagelistener!");

        FragmentManager fragmentManager = getSupportFragmentManager();
        fragmentManager.beginTransaction().replace(R.id.main_fragment_container, fragment).commit();

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    private void connectToMatrix(NetworkDevice matrix) {
        if(mConnection != null)
            mConnection.close();
        try {
            mConnection = new MatrixConnection(this, this);
            mConnection.start(matrix);
            mConnection.requestConnection(matrix);
        } catch (IOException e) {
            onException(this, e, "Could not construct MatrixConnection!");
        }
    }

    private void saveMatrix(NetworkDevice matrix) {
        SharedPreferences.Editor prefs = PreferenceManager.getDefaultSharedPreferences(this).edit();

        try {
            prefs.putString(getString(R.string.sp_last_connected_matrix), matrix.toJsonString());
        } catch (JSONException e) {
            onException(this, e, "Could not serialize matrix for storage");
        }

        prefs.apply();
    }

    @Override
    public void onMatrixClicked(final NetworkDevice server) {
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

    @Override
    public void onException(Object origin, Exception exception, String info) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(R.string.error_occurred);
        builder.setMessage(info);
        builder.setPositiveButton(R.string.ok, null);
    }

    private void onConnectionAccepted(NetworkDevice matrix) {
        saveMatrix(matrix);

        //noinspection ConstantConditions // should be set, see onCreate
        getSupportActionBar().setSubtitle("Connected to " + matrix.name);
    }

    @Override
    public void onMessage(NetworkDevice matrix, JSONObject data) {
        try {
            if(data.getString("message_type").equals("connection_request_answer")){
                if(data.getBoolean("granted"))
                    onConnectionAccepted(matrix);
            }
            else
                mCurrentMessageDigestor.onMessage(matrix, data);
        } catch (JSONException e) {
            onException(this, e, "Could not parse message_type!");
        }
    }
}
