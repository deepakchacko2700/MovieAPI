import redis
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

r = redis.StrictRedis(host='172.26.169.218', port=6379, db=0, decode_responses=True) # redis connection


class RequestCounterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        r.incr('request_count') # Increment the request counter in Redis

    def process_response(self, request, response):
        return response

# API to get the current request count.
def get_request_count(request):
    count = r.get('request_count')
    return JsonResponse({"requests": int(count) if count else 0})

# API to reset the request count to zero.
def reset_request_count(request):
    r.set('request_count', 0)
    return JsonResponse({"message": "request count reset successfully"})
