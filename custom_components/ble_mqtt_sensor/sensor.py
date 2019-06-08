import logging
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import (TEMP_CELSIUS, CONF_NAME, )
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv
import homeassistant.components.mqtt as mqtt

_LOGGER = logging.getLogger(__name__)

CONFIG_MAC = 'mac'
CONFIG_DEVICE_TYPE = 'device_type'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONFIG_MAC): cv.string,
    vol.Required(CONFIG_DEVICE_TYPE): cv.string,
})

ATTR_TEMPERATURE = 'Temperature'
ATTR_HUMIDITY = 'Humidity'
ATTR_BATTERY = 'Battery'

def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    temperature_name = name + ' ' + ATTR_TEMPERATURE
    humidity_name = name + ' ' + ATTR_HUMIDITY
    battery_name = name + ' ' + ATTR_BATTERY
    mac_address = config.get(CONFIG_MAC)
    add_devices([
        MeizuTemperature(hass, temperature_name, mac_address),
        MeizuHumidity(hass, humidity_name, mac_address),
        MeizuBattery(hass, battery_name, mac_address),
    ])


class MeizuTemperature(Entity):
    def __init__(self, hass, name, mac_address):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name
        self._mac_address = mac_address
        self._state = 0
        self.update()

    def update(self):
        payload = '85,3,8,17'
        sub_topic = self._mac_address + '/SensorService/SensorValue'
        pub_topic = sub_topic + '/Set'
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            #返回数据8位是温湿度信息
            if len(results) == 8:
                self._state = (int(results[4]) + int(results[5]) * 16 * 16) / 100

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
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


class MeizuHumidity(Entity):
    def __init__(self, hass, name, mac_address):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name
        self._mac_address = mac_address
        self._state = 0
        self.update()

    def update(self):
        payload = '85,3,8,17'
        sub_topic = self._mac_address + '/SensorService/SensorValue'
        pub_topic = sub_topic + '/Set'
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            #返回数据8位是温湿度信息
            if len(results) == 8:
                self._state = (int(results[6]) + int(results[7]) * 16 * 16) / 100

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
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return '%'


class MeizuBattery(Entity):
    def __init__(self, hass, name, mac_address):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name
        self._mac_address = mac_address
        self._state = 0
        self.update()

    def update(self):
        payload = '85,3,1,16'
        sub_topic = self._mac_address + '/SensorService/SensorValue'
        pub_topic = sub_topic + '/Set'
        mqtt.publish(self._hass, pub_topic, payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            # 返回数据5位是电量信息
            if len(results) == 5:
                self._state = int(results[4]) / 10

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
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'V'
