import serial
import re
import paho.mqtt.client as mqtt
import time

# MQTT Settings
MQTT_BROKER = "192.168.1.103" # or whereever you have it
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASSWORD = "mqtt_password"
MQTT_TOPIC = "/homeassistant/technical/powerwall/" # or whatever you want it

# Serial Port Settings
SERIAL_PORT = "/dev/ttyACM0" # or wherever you have it
BAUD_RATE = 115200

# Global flag for service menu mode
in_service_menu = False

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/homeassistant/technical/powerwall/command")

def on_publish(client, userdata, result):
    print("Data published")

def on_message(client, userdata, message):
    global in_service_menu

    # Debug print to confirm the function is called
    print("on_message function called")

        try:
            msg = message.payload.decode('utf-8').strip()
            print(f"Received MQTT message: '{msg}'")  # Debug print for received message

            # Send the message to the serial device
            ser.write(msg.encode() + b'\r')
            print(f"Sent '{msg}' to the serial device.")  # Debug print for sent message

            if msg == 's':
                in_service_menu = True
                print("Entered service menu mode")  # Debug print for entering service menu mode
        except Exception as e:
            print(f"Error in on_message: {e}")  # Print any exception that occurs


    # Set up MQTT client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe("/homeassistant/technical/powerwall/command")
    client.on_connect = on_connect
    client.on_message = on_message


    client.loop_start()

    # Set up serial connection
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    def calculate_module_and_cell(cell_num):
        cell_num = int(cell_num)
        module_num = (cell_num // 6) + 1  # Calculate module number
        cell_in_module = (cell_num % 6) + 1  # Calculate cell number within the module
        return module_num, cell_in_module

    def read_service_menu():
        menu_data = ""
        regular_data_detected = False
        ser.flushInput()  # Clear the serial buffer
        time.sleep(2)  # Wait for 2 seconds before reading the menu

        last_data_time = time.time()
        while not regular_data_detected:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                menu_data += line + "\n"
                last_data_time = time.time()  # Update the time of the last received data

                if "Module #" in line:
                    regular_data_detected = True

            elif time.time() - last_data_time > 5:  # 5-second timeout since the last line received
                break  # Exit if no data received for 5 seconds

        return menu_data, regular_data_detected

    try:
        while True:
            if in_service_menu:
                # Read the service menu
                menu, regular_data_detected = read_service_menu()
                client.publish("/homeassistant/technical/powerwall/service_menu", menu)

                if regular_data_detected:
                    in_service_menu = False  # Exit service menu mode if regular data is detected
            else:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(line)  # For debugging

                    # Extract data using regex
                    cell_voltages = re.findall(r'Cell(\d+): (\d+\.\d+)V', line)
                    delta_voltage = re.search(r'Delta Voltage: (\d+)mV', line)
                    module_voltages = re.findall(r'Module #(\d+)\s+(\d+\.\d+)V', line)
                    module_temps = re.findall(r'Module #(\d+).*Neg Term Temp: (\d+\.\d+)C.*Pos Term Temp: (\d+\.\d+)C', lin>

                    if cell_voltages:
                        # Organize cell voltages by module
                        module_voltages_dict = {}
                        for cell_num, voltage in cell_voltages:
                            module_num, _ = calculate_module_and_cell(cell_num)
                            if module_num not in module_voltages_dict:
                                module_voltages_dict[module_num] = []
                            module_voltages_dict[module_num].append(float(voltage))

                        # Calculate and publish module delta voltages
                        for module_num, voltages in module_voltages_dict.items():
                            if voltages:
                                module_delta = max(voltages) - min(voltages)
                                formatted_delta = "{:.2f}".format(module_delta)  # Format to two decimal place
                                delta_topic = f"{MQTT_TOPIC}module_{module_num}_delta_voltage"
                                client.publish(delta_topic, formatted_delta)

                        # Publish individual cell voltages
                        for cell_num, voltage in cell_voltages:
                            module_num, cell_in_module = calculate_module_and_cell(cell_num)
                            cell_topic = f"{MQTT_TOPIC}Mod{module_num}_Cell{cell_in_module}_Voltage"
                            client.publish(cell_topic, voltage)

                    if delta_voltage:
                        client.publish(MQTT_TOPIC + "delta_voltage", delta_voltage.group(1))

                      # Publish module voltages
                    if module_voltages:
                        for module_num, voltage in module_voltages:
                            voltage_topic = f"{MQTT_TOPIC}module_{module_num}_voltage"
                            client.publish(voltage_topic, voltage)

                      # Publish module temperatures
                    if module_temps:
                        for module_num, neg_temp, pos_temp in module_temps:
                            neg_temp_topic = f"{MQTT_TOPIC}module_{module_num}_neg_term_temp"
                            pos_temp_topic = f"{MQTT_TOPIC}module_{module_num}_pos_term_temp"
                            client.publish(neg_temp_topic, neg_temp )
                            client.publish(pos_temp_topic, pos_temp )
                else:
                     print("No data received from serial.")  # Debug line for unsuccessful reads
            time.sleep(2.4)  # Adjust as necessary

    except KeyboardInterrupt:
        print("Script interrupted, exiting.")
        client.loop_stop()




    # Close the serial connection
    ser.close()
