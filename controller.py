from bottle import route, run, json_loads
import redis
import json

ROUTE_ENGINE_FIREBASE_CALL = "/getFirebaseRequest"


class CacheService:
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 5
    REDIS_CACHED_REQ_KEY = "firebase_req"

    def __init__(self):
        self.redis = redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_PORT, db=self.REDIS_DB)

    def getfirebaserequest(self):
        cached = self.redis.get(self.REDIS_CACHED_REQ_KEY)

        if cached is not None:
            return cached.decode('utf8').replace('"', '\\"').replace("'", '"')
        else:
            return dict()


@route(ROUTE_ENGINE_FIREBASE_CALL)
def firebaserequest():
    cacheservice = CacheService()
    print(cacheservice.getfirebaserequest())
    print(type(cacheservice.getfirebaserequest()))
    return json_loads(cacheservice.getfirebaserequest())


run(host='localhost', port=8585, debug=True)
