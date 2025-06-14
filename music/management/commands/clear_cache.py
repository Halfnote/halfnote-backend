from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Clear all cache entries'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            help='Clear cache entries matching this pattern (Redis only)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )
    
    def handle(self, *args, **options):
        pattern = options.get('pattern')
        confirm = options.get('confirm')
        
        if not confirm:
            if pattern:
                confirm_msg = f"Are you sure you want to clear cache entries matching '{pattern}'? [y/N]: "
            else:
                confirm_msg = "Are you sure you want to clear ALL cache entries? [y/N]: "
            
            response = input(confirm_msg)
            if response.lower() not in ['y', 'yes']:
                self.stdout.write(self.style.WARNING('Cache clear cancelled.'))
                return
        
        try:
            # Check if we're using Redis
            if hasattr(settings, 'CACHES') and settings.CACHES.get('default', {}).get('BACKEND') == 'django_redis.cache.RedisCache':
                self._clear_redis_cache(pattern)
            else:
                self._clear_database_cache()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing cache: {str(e)}')
            )
    
    def _clear_redis_cache(self, pattern=None):
        """Clear Redis cache entries"""
        try:
            if pattern:
                # Clear specific pattern
                from django_redis import get_redis_connection
                redis_client = get_redis_connection("default")
                
                # Get all keys matching pattern
                keys = redis_client.keys(f"*{pattern}*")
                if keys:
                    redis_client.delete(*keys)
                    self.stdout.write(
                        self.style.SUCCESS(f'Cleared {len(keys)} cache entries matching pattern "{pattern}"')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'No cache entries found matching pattern "{pattern}"')
                    )
            else:
                # Clear all cache
                cache.clear()
                self.stdout.write(
                    self.style.SUCCESS('Successfully cleared all cache entries (Redis)')
                )
        except Exception as e:
            # Fallback to basic cache clear
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS(f'Cache cleared (fallback method). Note: {str(e)}')
            )
    
    def _clear_database_cache(self):
        """Clear database cache entries"""
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all cache entries (Database)')
        ) 