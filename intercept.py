# *****************************************************
# intercept.py
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

    IDENTIFIER_KEY = "to"
    FOREGROUND_KEY = "foreground"
    BACKGROUND_KEY = "background"
    URL_KEY = "url"
    METHOD_KEY = "method"
    CONTENT_KEY = "content"
    PRIORITY_KEY = "priority"
    NOTIFICATION_KEY =  "notification"
    CONTENT_AVAILABLE = "content_available"

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 5

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
                request_content_str = flow.request.content.decode("utf-8")
                request_content_json = json.loads(request_content_str)

                cachekey = self.intercept[self.CACHE_KEY] + "_" + request_content_json[self.IDENTIFIER_KEY]

                # dict cache_map
                cache_map = dict()

                # write request to Redis
                raw_cached = self.redis.get(cachekey)
                if raw_cached is not None:
                    ctx.log.info("Entry exists. Overwriting existing entry.")
                    # json cache_map
                    cache_map = json.loads(raw_cached.decode("utf-8")
                                           .replace("'", '"')
                                           .replace("True", "true")
                                           .replace("False", "false"))

                if((self.PRIORITY_KEY in request_content_json) and
                        (self.NOTIFICATION_KEY in request_content_json) and
                        (self.CONTENT_AVAILABLE not in request_content_json)):
                    # firebase request is Foreground
                    ctx.log.info("Firebase foreground request intercepted.")
                    cache_map_fg = dict()
                    cache_map_fg[self.URL_KEY] = flow.request.pretty_url
                    cache_map_fg[self.METHOD_KEY] = flow.request.method
                    cache_map_fg[self.CONTENT_KEY] = request_content_json
                    cache_map[self.FOREGROUND_KEY] = cache_map_fg
                else:
                    # firebase request is Background
                    ctx.log.info("Firebase background request intercepted.")
                    cache_map_bg = dict()
                    cache_map_bg[self.URL_KEY] = flow.request.pretty_url
                    cache_map_bg[self.METHOD_KEY] = flow.request.method
                    cache_map_bg[self.CONTENT_KEY] = request_content_json
                    cache_map[self.BACKGROUND_KEY] = cache_map_bg

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
