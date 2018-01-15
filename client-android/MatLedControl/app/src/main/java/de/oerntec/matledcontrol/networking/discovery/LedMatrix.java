package de.oerntec.matledcontrol.networking.discovery;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import org.json.JSONException;

import java.io.Serializable;

/**
 * This object is used to identify psychic network devices
 */
@SuppressWarnings("WeakerAccess")
public class LedMatrix implements Serializable {
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

    private static JsonParser jsonParser = new JsonParser();

    /**
     * ip address
     */
    public String address;
    public int width;
    public int height;

    /**
     * Create a new, fully defined, LedMatrix using the given parameters
     *
     * @param name    human readable name
     * @param dataPort    the device is listening on this dataPort for incoming data
     * @param address ip address
     */
    private LedMatrix(String name, int discoveryPort, int dataPort, String address, int width, int height) {
        this.name = name;
        this.dataPort = dataPort;
        this.address = address;
        this.discoveryPort = discoveryPort;
        this.width = width;
        this.height = height;
    }

    public boolean remoteIsConfigured(){
        return dataPort >= 0 && address != null && !"invalid".equals(address);
    }

    /**
     * Get the name as given by the LedMatrix
     *
     * @return the name as given by the LedMatrix
     */
    public String getName() {
        return name;
    }

    /**
     * Create a new LedMatrix when only the name is known
     *
     * @param name human readable name
     */
    public LedMatrix(String name) {
        this(name, -1, -1, "invalid", -1, -1);
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
        // if obj is not a LedMatrix, they are not the same object
        if (!(obj instanceof LedMatrix))
            return false;

        // for equality, only the name and address must be the same. thus, a device can have multiple servers,
        // and a name may be used multiple times in the same network
        LedMatrix server = (LedMatrix) obj;
        return address.equals(server.address) && name.equals(server.name);
    }

    /**
     * Create a new LedMatrix from a json representation
     *
     * @param json the information source
     * @return LedMatrix equal to the json representation
     * @throws JSONException if "name" or "dataPort" is missing in the json object
     */
    public static LedMatrix fromJson(JsonObject json) throws JSONException {
        String name = json.get("name").getAsString();
        int port = json.get("data_port").getAsInt();

        // default parameter values
        String address = "invalid";
        int discoveryPort = -1;
        int width = -1;
        int height = -1;

        if (json.has("address")) address = json.get("address").getAsString();
        if (json.has("discovery_port")) discoveryPort = json.get("discovery_port").getAsInt();
        if (json.has("matrix_width")) width = json.get("matrix_width").getAsInt();
        if (json.has("matrix_height")) height = json.get("matrix_height").getAsInt();

        return new LedMatrix(name, discoveryPort, port, address, width, height);
    }

    /**
     * Create a new LedMatrix from a json string representation
     *
     * @param json the information source
     * @return LedMatrix equal to the json representation
     * @throws JSONException if "name" or "dataPort" is missing in the json object
     */
    public static LedMatrix fromJsonString(String json) throws JSONException {
        return fromJson(jsonParser.parse(json).getAsJsonObject());
    }


    public JsonObject toJson() throws JSONException {
        JsonObject thisDevice = new JsonObject();
        thisDevice.addProperty("name", name);
        thisDevice.addProperty("data_port", dataPort);
        thisDevice.addProperty("discovery_port", discoveryPort);
        thisDevice.addProperty("matrix_width", width);
        thisDevice.addProperty("matrix_height", height);

        if (address != null)
            thisDevice.addProperty("address", address);

        return thisDevice;
    }

    public String toJsonString() throws JSONException {
        return this.toJson().toString();
    }
}
