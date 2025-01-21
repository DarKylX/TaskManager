import json
from django.core.cache import cache
from django.utils import timezone
from django_redis import get_redis_connection
from django.conf import settings

class PageVisitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)

        try:
            visit_data = {
                'user_id': request.user.id if request.user.is_authenticated else None,
                'path': request.path,
                'visited_at': timezone.now().isoformat(),
                'ip_address': self.get_client_ip(request)
            }

            if settings.USE_REDIS:
                # Используем Redis
                redis_client = get_redis_connection("default")
                redis_client.lpush('page_visits', json.dumps(visit_data))
            else:
                # Fallback для не-Redis окружения
                visits = cache.get('page_visits', [])
                visits.insert(0, visit_data)
                # Ограничиваем размер списка
                visits = visits[:1000]
                cache.set('page_visits', visits)

        except Exception as e:
            print(f"Error logging page visit: {e}")

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
