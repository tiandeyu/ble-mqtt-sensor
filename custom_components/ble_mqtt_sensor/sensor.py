import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import homeassistant.components.mqtt as mqtt
from datetime import datetime, timedelta
from homeassistant.core import callback
from homeassistant.const import (TEMP_CELSIUS,
                                 CONF_NAME, CONF_MAC, CONF_SCAN_INTERVAL, CONF_DEVICE_CLASS,
                                 DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_BATTERY, )
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_TOPIC = "topic"
CONF_SET_SUFFIX = "set_suffix"
SCAN_INTERVAL = timedelta(seconds=30)
DEFAULT_TOPIC = "/SensorService/SensorValue"
DEFAULT_SET_SUFFIX = "/Set"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_MAC): cv.string,
    vol.Required(CONF_DEVICE_CLASS): cv.string('meizu_remote'),
})

ATTR_TEMPERATURE = 'Temperature'
ATTR_HUMIDITY = 'Humidity'
ATTR_BATTERY = 'Battery'


def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    mac_address = config.get(CONF_MAC)
    topic = config.get(CONF_TOPIC, DEFAULT_TOPIC)
    set_suffix = config.get(CONF_SET_SUFFIX, DEFAULT_SET_SUFFIX)
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    add_devices([
        MeizuTemperature(hass, name, mac_address, update_interval, topic, set_suffix),
        MeizuHumidity(hass, name, mac_address, update_interval),
    ])


class MeizuTemperature(Entity):
    def __init__(self, hass, name, mac_address, interval, topic, set_suffix):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name + ' ' + ATTR_TEMPERATURE
        self._mac_address = mac_address
        self._topic = topic
        self._set_suffix = set_suffix
        self._state = None
        self._state_attrs = {
            ATTR_HUMIDITY: None,
            ATTR_BATTERY: None
        }
        self._update()
        self.update_battery_level()
        self.update = Throttle(interval)(self._update)

    def _update(self):
        payload = '85,3,8,17'
        sub_topic = self._mac_address + self._topic
        pub_topic = sub_topic + self._set_suffix
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            # 返回数据8位是温湿度信息
            if len(results) == 8:
                self._state = round((int(results[4]) + int(results[5]) * 16 * 16) / 100, 1)
                self._state_attrs[ATTR_HUMIDITY] = round((int(results[6]) + int(results[7]) * 16 * 16) / 100, 1)

        mqtt.subscribe(self._hass, sub_topic, msg_callback)

    @Throttle(timedelta(hours=12))
    def update_battery_level(self):
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
                self._state_attrs[ATTR_BATTERY] = round(int(results[4]) / 10, 1)

        mqtt.subscribe(self._hass, sub_topic, msg_callback)

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
    def __init__(self, hass, name, mac_address, interval):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name + ' ' + ATTR_HUMIDITY
        self._entity_id = "sensor." + name.replace(" ", "_") + "_" + ATTR_TEMPERATURE
        self._mac_address = mac_address
        self._state = None
        self._update()
        self.update = Throttle(interval)(self._update)

    def _update(self):
        stat = self._hass.states.get(self._entity_id)
        if stat:
            nowtime = datetime.utcnow()
            updated_time = stat.last_updated.replace(tzinfo=None)
            if nowtime - updated_time < timedelta(minutes=3):
                self._state = stat.attributes[ATTR_HUMIDITY]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_HUMIDITY

