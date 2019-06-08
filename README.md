BLE MQTT Sensor是一款ha自定义插件，配合esp32-ble2mqtt使用
能够整合mqtt信息到homeassistant
---

下载custom_components下面所有文件到如下目录/config/custom_components/

download all files from custom_components to your ha machine folder /config/custom_components/
```
//文件目录结构如下
//the folder should be the same as below
/config/custom_components/ble_mqtt_sensor/__init__.py
/config/custom_components/ble_mqtt_sensor/sensor.py
/config/custom_components/ble_mqtt_sensor/manifest.json
```

在configuration.yaml配置
 
name: ha中显示传感器的名字
 
mac: 小写mac地址 

```yaml
sensor:
  - platform: ble_mqtt_sensor
    name: 'Meizu Remote'
    mac: '68:3e:34:cc:d4:69'
    device_type: meizu_remote
```
