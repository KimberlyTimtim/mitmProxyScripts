# *****************************************************
# Intercept.py
# Created by: k.timtim
# 
# Subclass of Intercept class of mitmproxy.
# Allows intercept and modification of HTTP requests/responses.
# *****************************************************

from mitmproxy import ctx
from mitmproxy import http
from util import Util
import json
import redis

# global constants
INT_REQ_MAPPINGS_KEY = "intercept_request_mappings"
INT_RES_MAPPINGS_KEY = "intercept_response_mappings"
TYPE_KEY = "type"
TYPE_REQUEST = "request"
TYPE_RESPONSE = "response"


class Intercept:

    # class constants
    REQUEST_URL_KEY = "request_url"
    RESPONSE_FILE_KEY = "response_file"
    RESP_BODY_KEY = "response_body"
    RESP_STATUS_KEY = "status_code"
    RESP_REASON_KEY = "reason"
    CACHE_KEY = "cache_key"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

    def __init__(self, domain):
        self.intercept = domain
        self.redis = redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_PORT, db=self.REDIS_DB)
    
    def request(self, flow: http.HTTPFlow) -> None:
        ctx.log.info("REQUESTED: %s" % flow.request.pretty_url)
        ctx.log.info("COMPARED:  %s" % self.intercept[self.REQUEST_URL_KEY])

        if flow.request.pretty_url == self.intercept[self.REQUEST_URL_KEY]:
            if self.intercept[TYPE_KEY] == TYPE_RESPONSE:
                response_file = self.intercept[self.RESPONSE_FILE_KEY]
                if flow.request.pretty_url == "http://lbc-lb-as.idp.posten.se:53080/ntt-service-rest/api/shipmentinfo.json?key=notifiertest@gmail.com&keyType=email&time=2590000":
                    mockcount = self.redis.get('shipmentmock:count')
                    if mockcount == b'1':
                        response_file = "responses/shipment-provider-response-added.json"
                        self.redis.delete('shipmentmock:count')
                    else:
                        response_file = "responses/shipment-provider-response.json"
                        self.redis.set('shipmentmock:count', '1')
                # load stub response from file
                with open(response_file) as json_data:
                    response_map = json.load(json_data)

                # parse stub response body
                stub_response = json.dumps(response_map[self.RESP_BODY_KEY]).encode('utf-8')
                # parse stub response code
                stub_status_code = response_map[self.RESP_STATUS_KEY]

                # construct response object
                flow.response = http.HTTPResponse.make(
                    200,
                    stub_response,
                    {"Content-Type": "application/json"}
                )
            elif self.intercept[TYPE_KEY] == TYPE_REQUEST:
                ctx.log.info("Firebase Request Intercepted: Writing to Redis...")
                cachekey = self.intercept[self.CACHE_KEY]

                # write request to Redis
                if self.redis.get(cachekey) is not None:
                    ctx.log.info("Overwriting existing entry.")

                cache_map = dict()
                cache_map['url'] = flow.request.pretty_url
                cache_map['method'] = flow.request.method
                cache_map['content'] = flow.request.content.decode("utf-8")

                # set redis entry, expiry is 7 days (604800 seconds)
                self.redis.set(cachekey, cache_map, 604800)
                ctx.log.info("Redis write successful.")


# Load mapping from Util class
util = Util()

res_mapping_list = util.loadReqResMappingFromFile()[INT_RES_MAPPINGS_KEY]

# add Intercept object to addons for each mapping
addons = []
for res_mapping in res_mapping_list:
    res_mapping[TYPE_KEY] = TYPE_RESPONSE
    addons.append(Intercept(res_mapping))

req_mapping_list = util.loadReqResMappingFromFile()[INT_REQ_MAPPINGS_KEY]

# add Intercept object to addons for each mapping
for req_mapping in req_mapping_list:
    req_mapping[TYPE_KEY] = TYPE_REQUEST
    addons.append(Intercept(req_mapping))
