import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import homeassistant.components.mqtt as mqtt
from datetime import timedelta
from homeassistant.core import callback
from homeassistant.const import (TEMP_CELSIUS,
                                 CONF_NAME, CONF_MAC, CONF_SCAN_INTERVAL, CONF_DEVICE_CLASS,
                                 DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_BATTERY, )
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.helpers.event import track_time_interval

_LOGGER = logging.getLogger(__name__)

CONF_TOPIC = "topic"
CONF_SET_SUFFIX = "set_suffix"
SCAN_INTERVAL = timedelta(seconds=30)
BATTERY_SCAN_INTERVAL = timedelta(hours=12)
DEFAULT_TOPIC = "/SensorService/SensorValue"
DEFAULT_SET_SUFFIX = "/Set"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_TOPIC): cv.string,
    vol.Optional(CONF_SET_SUFFIX): cv.string,
    vol.Required(CONF_DEVICE_CLASS): cv.string('meizu_remote'),
})

ATTR_TEMPERATURE = 'Temperature'
ATTR_HUMIDITY = 'Humidity'
ATTR_BATTERY = 'Battery'


def setup_platform(hass, config, add_devices, discovery_info=None):
    # get config
    name = config.get(CONF_NAME)
    mac_address = config.get(CONF_MAC)
    topic = config.get(CONF_TOPIC, DEFAULT_TOPIC)
    set_suffix = config.get(CONF_SET_SUFFIX, DEFAULT_SET_SUFFIX)
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    # init meizu remote
    meizu_remote = MeizuRemote(hass, name, mac_address, topic, set_suffix)
    add_devices(meizu_remote.sensors)
    # set update time
    track_time_interval(hass, meizu_remote.update_temperature_humidity, update_interval)
    track_time_interval(hass, meizu_remote.update_battery_level, BATTERY_SCAN_INTERVAL)


class MeizuRemote(object):
    def __init__(self, hass, name, mac_address, topic, set_suffix):
        self._hass = hass
        self._mac_address = mac_address
        self._topic = topic
        self._set_suffix = set_suffix
        self._temperature_sensor = MeizuTemperature(hass, name)
        self._humidity_sensor = MeizuHumidity(hass, name)

        self.sensors = [
            self._temperature_sensor,
            self._humidity_sensor
        ]
        self.update_temperature_humidity()

    def update_temperature_humidity(self, now=None):
        #check if battery level out of date
        if not (self._temperature_sensor.device_state_attributes[ATTR_BATTERY] and self._humidity_sensor.device_state_attributes[ATTR_BATTERY]):
            _LOGGER.info("update meizu battery because it's out of date")
            self.update_battery_level()
        payload = '85,3,8,17'
        sub_topic = self._mac_address + self._topic
        pub_topic = sub_topic + self._set_suffix
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            # 返回数据8位是温湿度信息, 45位温度，67位是湿度
            if len(results) == 8:
                temperature = round((int(results[4]) + int(results[5]) * 16 * 16) / 100, 1)
                humidity = round((int(results[6]) + int(results[7]) * 16 * 16) / 100, 1)
                self._temperature_sensor.update_state(temperature)
                self._humidity_sensor.update_state(humidity)

        mqtt.subscribe(self._hass, sub_topic, msg_callback)

    def update_battery_level(self, now=None):
        payload = '85,3,1,16'
        sub_topic = self._mac_address + self._topic
        pub_topic = sub_topic + self._set_suffix
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            # 返回数据5位是电量信息
            if len(results) == 5:
                battery_level = round(int(results[4]) / 10, 1)
                self._temperature_sensor.update_battery(battery_level)
                self._humidity_sensor.update_battery(battery_level)

        mqtt.subscribe(self._hass, sub_topic, msg_callback)


class MeizuTemperature(Entity):
    def __init__(self, hass, name):
        self._hass = hass
        self._name = name + ' ' + ATTR_TEMPERATURE
        self._state = None
        self._state_attrs = {
            ATTR_BATTERY: None
        }

    def update_state(self, state):
        self._state = state

    def update_battery(self, battery):
        self._state_attrs[ATTR_BATTERY] = battery

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_TEMPERATURE


class MeizuHumidity(Entity):
    def __init__(self, hass, name):
        self._hass = hass
        self._name = name + ' ' + ATTR_HUMIDITY
        self._state = None
        self._state_attrs = {
            ATTR_BATTERY: None
        }

    def update_state(self, state):
        self._state = state

    def update_battery(self, battery):
        self._state_attrs[ATTR_BATTERY] = battery

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_HUMIDITY
