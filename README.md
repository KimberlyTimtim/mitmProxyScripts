# mitmProxyScripts
Python addon scripts for use with mitmproxy

-----

## **Overview** ##

These python scripts are meant to be used along with the `mitmproxy` application.
For this particular case, we are using `mitmproxy` as a **Regular Proxy**.
![Overview](mitmproxy_diagram.png)

After proper installation and setup of `mitmproxy`, we are now able to intercept HTTP/S traffic.
Through the `Intercept` scripts, we can manipulate the requests/responses on the configured URLs to suit our testing.

-----

## **Additional Features** ##

### **Verification Endpoints** ###

To integrate this tool with `Katalon` or other testing suites, we have added endpoints which can be used to intercept specific requests and check the parameters passed in that request. `mitmproxy` intercepts calls to these URLs and stores the values in Redis.

#### **Firebase Calls** ####

Current support is to intercept and check the parameters of Firebase requests. Calls to `http://fcm.googleapis.com/fcm/send` is monitored and details of these calls can be checked via the following endpoint:

```
GET | http://localhost:8585/getFirebaseRequest/<identifier>
```

Sample response:
```
{
    'foreground': {
        'url': 'http: //fcm.googleapis.com/fcm/send',
        'method': 'POST',
        'content': {
            'to': <identifier>,
            'priority': 'high',
            'notification': {
                'title': 'testFirebase',
                'body': 'JUnit: \xc3\xa5\xc3\xa4\xc3\xb6\xc3\x85\xc3\x84\xc3\x96',
                'sound': 'default',
                'icon': 'notification',
                'color': '#00A0D6',
                'click_action': 'com.postnord.NOTIFICATION_ACTION'
            },
            'data': {
                'shipmentid': 'TEST123456789SE',
                'type': 'updated'
            }
        }
    },
    'background': {
        'url': 'http: //fcm.googleapis.com/fcm/send',
        'method': 'POST',
        'content': {
            'to': <identifier>,
            'content_available': True,
            'data': {
                'status': 'N/A',
                'timestamp': 1542270955330,
                'type': 'updated',
                'shipmentid': 'TEST123456789SE'
            }
        }
    }
}
```

### **Maintenance Endpoints** ###

Since we are using Redis for storing the Firebase requests, you can use the ff endpoint for clearing unused Redis entries:

```
DELETE | http://localhost:8585/cleanupRedis/<identifier>
```

-----

## **Usage** ##

### **Environment Setup** ###

1. Place the expected JSON response under the `responses` directory. A sample JSON file is already placed for reference.
2. Place the request URL to be mocked along with the response file under `mappings.json` file. An example mapping has already been placed.

### **Running the Proxy** ##
1. Run `mitmproxy` using the intercept script:
	```
	mitmdump -s intercept.py
	```
2. Try to send a sample request to the request URL in your `mappings.json` file. It should be able to respond using the dummy response JSON file.

### **Running the Endpoint Server** ##
1. Run the server by performing the ff commands:
	```
	python controller.py
	```
2. Send a REST request to the endpoints mentioned above.
