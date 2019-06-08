import logging
import asyncio
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import (TEMP_CELSIUS, CONF_NAME, )
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv
import homeassistant.components.mqtt as mqtt

_LOGGER = logging.getLogger(__name__)

CONFIG_MAC = 'mac'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONFIG_MAC): cv.string,
})

ATTR_TEMPERATURE = 'temperature'
ATTR_HUMIDITY = 'humidity'
ATTR_BATTERY = 'battery'

def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    mac_address = config.get(CONFIG_MAC)
    add_devices([
        BleMqttSensor(hass, name, mac_address)
    ])


class BleMqttSensor(Entity):
    def __init__(self, hass, name, mac_address):
        """Initialize the generic Xiaomi device."""
        self._hass = hass
        self._name = name
        self._mac_address = mac_address
        self._state = None
        self._state_attrs = {
            ATTR_TEMPERATURE: 0,
            ATTR_HUMIDITY: 0,
            ATTR_BATTERY: 0
        }
        self.update()

    def update(self):
        temperature_humidity_payload = '85,3,8,17'
        battery_level_payload = '85,3,1,16'
        sub_topic = self._mac_address + '/SensorService/SensorValue'
        pub_topic = sub_topic + '/Set'
        mqtt.publish(self._hass, pub_topic, temperature_humidity_payload)
        mqtt.publish(self._hass, pub_topic, battery_level_payload)

        @callback
        def msg_callback(msg):
            """Receive events published by and fire them on this hass instance."""
            results = msg.payload.split(',')
            #返回数据8位是温湿度信息
            if len(results) == 8:
                temperature = (int(results[4]) + int(results[5]) * 16 * 16) / 100
                humidity = (int(results[6]) + int(results[7]) * 16 * 16) / 100
                self._state_attrs.update({
                    ATTR_TEMPERATURE: temperature,
                    ATTR_HUMIDITY: humidity
                })

            #返回数据5位是电量信息
            if len(results) == 5:
                battery = int(results[4]) / 10
                self._state_attrs.update({
                    ATTR_BATTERY: battery
                })

        mqtt.subscribe(self._hass, sub_topic, msg_callback)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def mac_address(self):
        """Flag supported features."""
        return self._mac_address

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
