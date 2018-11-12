# mitmProxyScripts
Python addon scripts for use with mitmproxy

-----

## **Overview** ##

These python scripts are meant to be used along with the `mitmproxy` application.
For this particular case, we are using `mitmproxy` as a **Regular Proxy**
![Overview](mitmproxy_diagram.png)

After proper installation and setup of `mitmproxy`, we are now able to intercept HTTP/S traffic.
Through the `Intercept` scripts, we can manipulate the requests/responses on the configured URLs to suit our testing.

## **Usage** ##

### **Setup** ###

1. Place the expected JSON response under the `responses` directory. A sample JSON file is already placed for reference.
2. Place the request URL to be mocked along with the response file under `mappings.json` file. An example mapping has already been placed.

### **Execution** ##
1. Run `mitmproxy` using the intercept script:
	```
	mitmdump -s intercept.py
	```
2. Try to send a sample request to the request URL in your `mappings.json` file. It should be able to respond using the dummy response JSON file.
