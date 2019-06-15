## BLE MQTT Sensor 


>BLE MQTT Sensor是一款ha自定义插件,配合esp32-ble2mqtt使用,能够整合mqtt信息到homeassistant


### 下载custom component
下载custom_components下面所有文件到如下目录/config/custom_components/

```
//文件目录结构如下
/config/custom_components/ble_mqtt_sensor/__init__.py
/config/custom_components/ble_mqtt_sensor/sensor.py
/config/custom_components/ble_mqtt_sensor/manifest.json
```

### configuration.yaml配置 
| 名称 | 可选 | 描述 |
| --- | --- | --- |
| name | 否 | ha中显示传感器的名字 |  
| mac | 否 | 小写mac地址 |
| topic | 是 | ble2mqtt config.json里面配置的service name和characteristics name 默认/SensorService/SensorValue | 
| set_suffix | 是 | ble2mqtt config.json里面配置的set_suffix，默认/Set |
| scan_interval | 是 | 扫描间隔s，默认30 |
| device_class | 否 | meizu_remote代表魅族遥控器 |
```yaml
sensor:
  - platform: ble_mqtt_sensor
    name: 'Meizu Remote'
    mac: '68:3e:34:cc:d4:69'
    topic: '/SensorService/SensorValue'
    set_suffix: '/Set'
    scan_interval: 60
    device_class: meizu_remote
```

### 多个配置
```yaml
sensor:
  - platform: ble_mqtt_sensor
    name: 'Meizu Remote'
    mac: '68:3e:34:cc:d4:69'
    device_class: meizu_remote
    
  - platform: ble_mqtt_sensor
    name: 'Living Room Meizu Remote'
    mac: '68:3e:34:cc:d4:70'
    device_class: meizu_remote
    
  - platform: ble_mqtt_sensor
    name: 'Bedroom Meizu Remote'
    mac: '68:3e:34:cc:d4:71'
    device_class: meizu_remote
```