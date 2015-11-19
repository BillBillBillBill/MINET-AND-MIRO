import redis


REDIS_HOST = "localhost"
REDIS_PORT = "6379"

pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
r = redis.Redis(connection_pool=pool)