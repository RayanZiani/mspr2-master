import os

# URLs des 3 APIs pays (via Docker network)
API_URLS = {
    "bresil":   os.getenv("API_BRESIL_URL", "http://api-bresil:8000"),
    "equateur": os.getenv("API_EQUATEUR_URL", "http://api-equateur:8000"),
    "colombie": os.getenv("API_COLOMBIE_URL", "http://api-colombie:8000"),
}

REDIS_URL = os.getenv("REDIS_URL", "redis://redis-siege:6379")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 60))
