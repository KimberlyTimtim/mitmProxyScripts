# *****************************************************
# Intercept.py
# Created by: k.timtim
# 
# Subclass of Intercept class of mitmproxy.
# Allows intercept and modification of HTTP requests/responses.
# *****************************************************
from mitmproxy import flowfilter
from mitmproxy import ctx
from util import Util
import json
from urllib.parse import urlparse

# global constants
MAPPINGS_KEY = "mappings"

class Intercept:

    # class constants
    REQUEST_URL_KEY = "request_url"
    RESPONSE_FILE_KEY = "response_file"
    RESP_BODY_KEY = "response_body"
    RESP_STATUS_KEY = "status_code"
    RESP_REASON_KEY = "reason"

    def __init__(self, domain):
        self.intercept = domain

    def response(self, flow):
        ctx.log.info("================ ACTUAL REQUEST ================")
        ctx.log.info("HOST: %s" % flow.request.host)
        ctx.log.info("PATH: %s" % flow.request.path)
        
        ctx.log.info("================ COMPARE =======================")
        ctx.log.info("INTERCEPT URL: %s" % self.intercept[self.REQUEST_URL_KEY])
        
        parsed = urlparse(self.intercept[self.REQUEST_URL_KEY])
        req_host = parsed.netloc
                
        if len(parsed.query) > 0:
            req_path = parsed.path + "?" + parsed.query
        else:
            req_path = parsed.path
        
        ctx.log.info("HOST: %s" % req_host)
        ctx.log.info("PATH: %s" % req_path)
                
        # intercept only selected requests
        #if ( (flow.request.host in self.intercept[self.REQUEST_URL_KEY]) and (flow.request.path in self.intercept[self.REQUEST_URL_KEY]) ):
        if ( (flow.request.host == req_host) and (flow.request.path == req_path) ):
           flow.intercept()
           
           # perform response modifications
           # load from file
           with open(self.intercept[self.RESPONSE_FILE_KEY]) as json_data:
               response_map = json.load(json_data)
           
           # setting response body
           flow.response.content = json.dumps(response_map[self.RESP_BODY_KEY]).encode('utf-8')
           
           # setting status code
           flow.response.status_code = response_map[self.RESP_STATUS_KEY]
           
           # setting status reason
           flow.response.reason = response_map[self.RESP_REASON_KEY]
           
           flow.resume()
           ctx.log.info("================ MOCKED RESPONSE ================")
           ctx.log.info("%s" % flow.response.content)
           ctx.log.info("=================================================")

# Load mapping from Util class
util = Util()
mapping_list = util.loadReqResMappingFromFile()[MAPPINGS_KEY]

# add Intercept object to addons for each mapping
addons = []
for mapping in mapping_list:
    addons.append(Intercept(mapping))