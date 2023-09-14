import requests
import paho.mqtt.client as mqtt
import yaml
import os
import json
import time
import socket

def fetch_prices(emi_config):
    try:
        api_key = emi_config['api_key']
        api_filter = emi_config['gxp']
        
        # Set api endpoint
        api_endpoint = "https://emi.azure-api.net/real-time-dispatch/"
        
        # Set the headers to include API key
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/json",
        }

        # Combine the base URL and API path
        url = f"{api_endpoint}?$filter=PointOfConnectionCode eq '{api_filter}'"

        # Send a GET request to the OpenShift API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for any HTTP errors

        # Process the response content (e.g., JSON data)
        data = response.json()

        cleaned_data = {}
        # Loop through items in data that gets sent back
        for item in data:
            # Extract the 'PointOfConnectionCode' value from the response
            point_of_connection = item['PointOfConnectionCode']

            # Drop surplus elements from dictionary
            del item['PointOfConnectionCode']
            del item['FiveMinuteIntervalNumber']
            del item['RunDateTime']

            # Rename and Reorder elements from dictionary
            item['datetime'] = item.pop('FiveMinuteIntervalDatetime')
            item['price_mwh'] = item.pop('DollarsPerMegawattHour')
            item['load_mw'] = item.pop('SPDLoadMegawatt')
            item['generation_mw'] = item.pop('SPDGenerationMegawatt')

            # Create the new dictionary with the desired structure
            new_dict = {point_of_connection: item}

            # Add the cleaned data to the dictionary
            cleaned_data.update(new_dict)

        return cleaned_data

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

def get_hostname():
    # Get hostname for local machine
    return socket.gethostname()

def publish_price_data(config):

    emi_config =  config["emi"]
    mqtt_config = config["mqtt"]
    
    # Extract MQTT configuration values
    broker_address = mqtt_config["broker_address"]
    port = mqtt_config["port"]
    username = mqtt_config["username"]
    password = mqtt_config["password"]
    wait_seconds = mqtt_config["wait_seconds"]
    run_verbose =  mqtt_config["run_verbose"]
    
    # Topic settings
    server_name = get_hostname()
    lwt_topic = f"tele/{server_name}/LWT"  # Define the LWT topic
    lwt_message = "Offline"  # Define the LWT message
    sensor_topic = f"tele/{server_name}/PRICES"  # Change to the desired topic
    
        # Create an MQTT client
    client = mqtt.Client("python_publisher")

    # Set the username and password
    client.username_pw_set(username, password)

    # Set the LWT message and topic
    client.will_set(lwt_topic, lwt_message, 0, retain=True)

    # Connect to the MQTT broker
    client.connect(broker_address, port)

    # Initiate the LWT to "Online" when connected
    client.publish(lwt_topic, "Online", 0, retain=True)
    
    if run_verbose:
        print(f"Script Running\nPrices publishing to: {sensor_topic}\nLWT publishing to:     {lwt_topic}\n")

    while True:
        
        price_data = fetch_prices(emi_config)
        
        # Serialize the dictionary to a JSON string
        message_json = json.dumps(price_data)

        # Publish the message to the MQTT topic
        client.publish(sensor_topic, message_json)

        if run_verbose:
            print(message_json)
            
        # Wait for the specified number of seconds before publishing the next message
        time.sleep(wait_seconds)

if __name__ == "__main__":
# Example usage:
    # Get the directory of the current script
    script_dir = os.path.dirname(__file__)

    # Define the relative path to the YAML configuration file
    config_file_path = os.path.join(script_dir, "nzem_config.yaml")

    # Load MQTT configuration from the YAML file
    with open(config_file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        
    # Call the function to start publishing data
    publish_price_data(config)

