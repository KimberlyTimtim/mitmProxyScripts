# *****************************************************
# controller.py
# Created by: k.timtim
#
# Endpoints for accessing stored requests for automated test verification.
# *****************************************************

from bottle import route, run, json_loads
import redis

# server constants
ROUTE_HOST = 'localhost'
ROUTE_PORT = 8585

# route constants
ROUTE_ENGINE_FIREBASE_CALL = "/getFirebaseRequest/"
ROUTE_REDIS_CLEANUP = "/cleanupRedis/"


class FirebaseReqCacheService:
    # redis connection configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 5

    # redis cache constants
    REDIS_CACHED_REQ_KEY = "firebase_req_"

    def __init__(self):
        self.redis = redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_PORT, db=self.REDIS_DB)

    # Retrieves cached Firebase Request parameters (URL, method, body) for a specific identifier (key)
    def getfirebaserequest(self, key):
        cached = self.redis.get(self.REDIS_CACHED_REQ_KEY + key)

        if cached is not None:
            return cached.decode("utf-8")\
                .replace("'", '"')\
                .replace("True", "true")\
                .replace("False", "false")
        else:
            return dict()

    # Removed cached Firebase Request parameters (URL, method, body) for a specific identifier (key)
    def firebaserequestcleanup(self, key):
        return self.redis.delete(self.REDIS_CACHED_REQ_KEY + key)


firebasecacheservice = FirebaseReqCacheService()


# GET endpoint for retrieving Firebase Request parameters
@route(ROUTE_ENGINE_FIREBASE_CALL + "<key>")
def firebaserequest(key):
    return json_loads(firebasecacheservice.getfirebaserequest(key))


# POST endpoint for removing cached Firebase Request parameters
@route(ROUTE_REDIS_CLEANUP + "<key>", method="DELETE")
def rediscleanup(key):
    response = dict()
    response["delete_result"] = str(firebasecacheservice.firebaserequestcleanup(key))
    return response


run(host=ROUTE_HOST, port=ROUTE_PORT, debug=True)
