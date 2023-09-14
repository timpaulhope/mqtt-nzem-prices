## EMI Price Publisher

This beginner Python script fetches electricity price data from the EMI (Electricity Market Information) API and publishes it to an MQTT broker. The script is designed to be easily configurable and can run as a background process to provide real-time electricity price information.

### Prerequisites

Before using this script, you need to:

1. Have access to the [EMI API](https://emi.portal.azure-api.net/) and obtain an API key.
2. Install the required Python libraries (`requests`, `paho-mqtt`, `yaml`).

### Configuration

Configuration settings are loaded from a YAML file (`nzem_config.yaml` in this example). You can customize the following parameters in the configuration file:

- EMI API settings, including the API key and the desired point of connection (POC) code you want to return prices for.
- MQTT broker settings, including the broker address, port, username, password, wait time between updates, and whether to run in verbose mode.
- Hostname of the local machine (automatically retrieved).

### Usage

1. Ensure you have the required libraries installed.

```bash
pip install requests paho-mqtt PyYAML
```

2. Update the `nzem_config.yaml` file with your EMI API key and MQTT broker settings.

3. Run the script:

```bash
python emi_price_publisher.py
```

The script will start fetching electricity price data from the EMI API and publishing it to the specified MQTT topic. The script will continue running until manually stopped (e.g., by pressing Ctrl+C).

### MQTT Topics

The script publishes data to two MQTT topics:

- `tele/{hostname}/PRICES`: This is the main topic where price data is published.
- `tele/{hostname}/LWT`: This topic is used for the Last Will and Testament (LWT) feature to indicate whether the script is online or offline.

### Verbose Mode

By default, the script runs in non-verbose mode. In verbose mode, it prints the JSON messages it sends to MQTT, which can be helpful for debugging and monitoring.

### Error Handling

The script includes basic error handling for API requests and MQTT connections. If an error occurs, it will be displayed in the console.

### Notes

- Make sure to configure your MQTT broker to accept incoming connections and topic publishing.
- Customize the MQTT topics to match your setup if needed.
- Ensure that your EMI user is subcribed to the [Wholesale Market Price](https://emi.portal.azure-api.net/products/wholesale-price-data) API.
- This script is designed to be a starting point; you can modify it to suit your specific requirements or integrate it with other systems.
- The script uses the `requests` library to fetch data from the EMI API and the `paho-mqtt` library to publish data to MQTT.

Please use this script responsibly and be mindful of API usage limits and data privacy considerations.
