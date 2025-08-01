import sys

from config import settings
import redis


rdb = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

print("rdb", rdb)
print("sys.argv", len(sys.argv))


if len(sys.argv) != 2:
    print("Usage: $0 path-to-emails.txt\n")
    exit(0)

print("file", sys.argv[1])
with open (sys.argv[1], "r") as f:
    print(f)
    i = 0
    for line in f:
        email = line.strip()
        if "#" in email: # or "@" not in line:
            continue
        i += 1
        print("email", email)

        rdb.set(f"blacklist:email:{email}", 1);

        if i > 100:
            pass