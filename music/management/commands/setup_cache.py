"""
Management command to set up caching infrastructure
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from music.cache_utils import setup_cache_table


class Command(BaseCommand):
    help = 'Set up caching infrastructure for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate cache table even if it exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up caching infrastructure...'))
        
        # Check if we're using database cache
        cache_backend = settings.CACHES['default']['BACKEND']
        
        if 'DatabaseCache' in cache_backend:
            self.stdout.write('Setting up database cache table...')
            try:
                call_command('createcachetable')
                self.stdout.write(
                    self.style.SUCCESS('Database cache table created successfully')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create cache table: {e}')
                )
        
        elif 'RedisCache' in cache_backend:
            self.stdout.write('Using Redis cache - no table setup needed')
            # Test Redis connection
            try:
                from django.core.cache import cache
                cache.set('test_key', 'test_value', 10)
                result = cache.get('test_key')
                if result == 'test_value':
                    self.stdout.write(
                        self.style.SUCCESS('Redis cache connection successful')
                    )
                    cache.delete('test_key')
                else:
                    self.stdout.write(
                        self.style.ERROR('Redis cache test failed')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Redis connection failed: {e}')
                )
        
        else:
            self.stdout.write(f'Using cache backend: {cache_backend}')
        
        self.stdout.write(
            self.style.SUCCESS('Cache setup completed!')
        ) 