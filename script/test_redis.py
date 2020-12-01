import redis

conn = redis.Redis(host="127.0.0.1",port=6379, password=123456, encoding='utf-8')
conn.set('foo','Bar',ex=10)

result = conn.get("foo")


print(result)
print(conn.keys())
# print(conn.flushall())