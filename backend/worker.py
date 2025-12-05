import redis
from rq import Worker, Queue

listen = ["default"]

redis_conn = redis.Redis(host="localhost", port=6379, db=0)

if __name__ == "__main__":
    # Create queues bound to this redis connection
    queues = [Queue(name, connection=redis_conn) for name in listen]

    # Create a worker with these queues and the same connection
    worker = Worker(queues, connection=redis_conn)
    worker.work()
