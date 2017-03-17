package de.oerntec.matledcontrol.networking.discovery;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;
import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * This object is used to identify psychic network devices
 */
@SuppressWarnings("WeakerAccess")
public class NetworkDevice implements Serializable {
    /**
     * A human-readable name
     */
    public String name;

    /**
     * dataPort the device is listening on this dataPort for incoming data
     */
    public int dataPort;

    /**
     * dataPort the device is listening on for discovery packets
     */
    public int discoveryPort;

    /**
     * ip address
     */
    public String address;

    /**
     * Create a new, fully defined, NetworkDevice using the given parameters
     *
     * @param name    human readable name
     * @param dataPort    the device is listening on this dataPort for incoming data
     * @param address ip address
     */
    public NetworkDevice(String name, int discoveryPort, int dataPort, String address) {
        this.name = name;
        this.dataPort = dataPort;
        this.address = address;
        this.discoveryPort = discoveryPort;
    }

    public boolean remoteIsConfigured(){
        return dataPort >= 0 && address != null && !"invalid".equals(address);
    }

    /**
     * Get the name as given by the NetworkDevice
     *
     * @return the name as given by the NetworkDevice
     */
    public String getName() {
        return name;
    }

    /**
     * j
     * Create a new NetworkDevice which will announce itself as "name" who may be contacted using commandPort and dataPort
     *
     * @param name human readable name
     * @param dataPort the device is listening on this dataPort for incoming data
     */
    public NetworkDevice(String name, int dataPort) {
        this(name, -1, dataPort, "invalid");
    }

    /**
     * Create a new NetworkDevice when only the name is known
     *
     * @param name human readable name
     */
    public NetworkDevice(String name) {
        this(name, -1);
    }

    /**
     * Returns this devices address to an {@link InetAddress} object
     *
     * @return InetAddress pointing to this device
     * @throws UnknownHostException if this NetworkDevice is not configured sufficiently or the address could not be converted
     */
    public InetAddress getInetAddress() throws UnknownHostException {
        // check whether we actually have set a valid address yet
        if ("invalid".equals(address))
            throw new UnknownHostException("This NetworkDevice is not configured sufficiently to provide an InetAddress");

        // convert and return address
        return InetAddress.getByName(address);
    }

    /**
     * Returns this network device formatted as "name" at "address"
     */
    @Override
    public String toString() {
        return name + " at " + address;
    }

    /**
     * This hashcode implementation maps to our implementation of {@link #equals(Object)}, and computes
     * the hash by adding the hash codes of the address and the name.
     * <p>
     * If the {@link #equals(Object)} method is changed, this must be adjusted as well!
     */
    @Override
    public int hashCode() {
        // this hash code implementation relies on the fact that the java string hash code is always
        // the same for the same string
        return address.hashCode() + name.hashCode();
    }

    /**
     * Check whether two network devices identify as the same device. This only checks their address
     * and name; the dataPort may change!
     * <p>
     * If the {@link #hashCode()} method is changed, this must be adjusted as well!
     */
    @Override
    public boolean equals(Object obj) {
        // if obj is not a NetworkDevice, they are not the same object
        if (!(obj instanceof NetworkDevice))
            return false;

        // for equality, only the name and address must be the same. thus, a device can have multiple servers,
        // and a name may be used multiple times in the same network
        NetworkDevice server = (NetworkDevice) obj;
        return address.equals(server.address) && name.equals(server.name);
    }

    /**
     * Create a new NetworkDevice from a json representation
     *
     * @param json the information source
     * @return NetworkDevice equal to the json representation
     * @throws JSONException if "name" or "dataPort" is missing in the json object
     */
    public static NetworkDevice fromJson(JSONObject json) throws JSONException {
        String name = json.getString("name");
        int port = json.getInt("data_port");
        String address = "invalid";
        int discoveryPort = -1;

        if (json.has("address")) address = json.getString("address");
        if (json.has("discovery_port")) discoveryPort = json.getInt("discovery_port");

        return new NetworkDevice(name, discoveryPort, port, address);
    }

    /**
     * Create a new NetworkDevice from a json string representation
     *
     * @param json the information source
     * @return NetworkDevice equal to the json representation
     * @throws JSONException if "name" or "dataPort" is missing in the json object
     */
    public static NetworkDevice fromJsonString(String json) throws JSONException {
        return fromJson(new JSONObject(json));
    }


    public JSONObject toJson() throws JSONException {
        JSONObject thisDevice = new JSONObject();
        thisDevice.put("name", name);
        thisDevice.put("data_port", dataPort);
        thisDevice.put("discovery_port", discoveryPort);

        if (address != null)
            thisDevice.put("address", address);

        return thisDevice;
    }

    public String toJsonString() throws JSONException {
        return this.toJson().toString();
    }
}
