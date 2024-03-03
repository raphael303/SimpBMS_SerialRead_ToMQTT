# SimpBMS Battery Management System - Read the debug info, which is sent via USB and send it to MQTT
This reads from a SimpBMS, connected via USB, and sends the debug output to MQTT. Tested on a raspberry Pi.

Copy serial_to_mqtt.py to some folder on your pi or create it in some place with: 
```
sudo nano serial_to_mqtt.py 
```

Make sure it is executable:
```
sudo chmod +x serial_to_mqtt.py
```

Run with:
```
python3 serial_to_mqtt.py
```
Stop with control-c

This is just for testing. You probably want to run this as a service and on boot.

Create a service: 
```
sudo nano /etc/systemd/system/serial_to_mqtt.service
```
### This is the content of serial_to_mqtt.service:
```
[Unit]
Description=Serial to MQTT Service
After=multi-user.target

[Service]
Type=simple
User=YOURUSERNAME
ExecStart=/usr/bin/python3 YOURPATH/serial_to_mqtt.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Safe the file
Then make enable it and start it.
```
sudo systemctl daemon-reload
sudo systemctl enable serial_to_mqtt.service
sudo systemctl start serial_to_mqtt.service
```

Check Service with:
```
sudo systemctl status serial_to_mqtt.service
```
Stop Service with:
```
sudo systemctl stop serial_to_mqtt.service
```
