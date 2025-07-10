import requests

class LibreNMS:
    """
    Client for interacting with the LibreNMS API.

    Provides methods to send API requests, check for existing devices,
    add new devices to LibreNMS and etc...

    Attributes:
        base_url (str): Base URL of the LibreNMS instance.
        api_token (str): API authentication token.

    Methods:

        device_exists(hostname: str) -> bool:
            Checks if a device with the given hostname exists in LibreNMS.

        add_device(hostname: str, community: str, snmp_version: str = "v2c"):
            Adds a new device to LibreNMS via the API.
    """
    def __init__(self, base_url: str, api_token: str, ssl_verify: bool = True):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'X-Auth-Token': self.api_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.ssl_verify = ssl_verify
        # Set API version
        self.api_verion = "/api/v0" 
        # Create a BaseURL
        self.base_url = f"{self.base_url}{self.api_verion}"
    
    def device_exists(self, hostname: str) -> bool:
        """
        Query LibreNMS for a device to verify whether such a device exists.

        Parameters:
        - hostname (str): The IP address or DNS name of the device.

        Returns:
         - bool: True if the device is found, False otherwise.

        """
        url = f"{self.base_url}/devices/{hostname}"
        response = requests.request(method="GET", url=url, headers=self.headers, verify=self.ssl_verify)
        if response.status_code == 404:
            result = response.json()
            if result.get('status') == 'error': 
                return False
        if response.status_code == 200:
            result = response.json()
            if result.get('count') > 0: 
                return True
        raise Exception(response)

    def add_device(self, hostname: str, community: str, snmp_version: str = "v2c") -> dict:
        """
        Adds a device to LibreNMS via the API.

        Parameters:
        - hostname (str): The IP address or DNS name of the device.
        - community (str): The SNMP community string.
        - snmp_version (str): The SNMP version to use (default is "v2c").

        Returns:
        - dict: The API response as a JSON-decoded dictionary.
        """
        
        # Check that such a hostname does not already exist
        if self.device_exists(hostname):
            return {"status":"error", "message":f"Device with hostname '{hostname}' already exists"}

        if snmp_version == "1":
            snmp_version = "v1"
        
        if snmp_version == "2":
            snmp_version = "v2c"
        
        if snmp_version == "3":
            snmp_version = "v3"
        
        if snmp_version not in ("v1", "v2c", "v3"):
            raise ValueError("SNMP version isn't correct")
        
        #Build the url
        url = f"{self.base_url}/devices"
        #Build payload
        payload = {
            "hostname": hostname,
            "community": community,
            "version": snmp_version
        }
        
        response = requests.request(method="POST", url=url, headers=self.headers, json=payload, verify=self.ssl_verify)
        return response.json()