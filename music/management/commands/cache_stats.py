from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import json


class Command(BaseCommand):
    help = 'Display cache statistics and information'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output stats in JSON format',
        )
        parser.add_argument(
            '--keys',
            action='store_true',
            help='Show cache keys (Redis only)',
        )
    
    def handle(self, *args, **options):
        output_json = options.get('json')
        show_keys = options.get('keys')
        
        try:
            # Check if we're using Redis
            if hasattr(settings, 'CACHES') and settings.CACHES.get('default', {}).get('BACKEND') == 'django_redis.cache.RedisCache':
                stats = self._get_redis_stats(show_keys)
            else:
                stats = self._get_database_stats()
            
            if output_json:
                self.stdout.write(json.dumps(stats, indent=2))
            else:
                self._display_stats(stats)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting cache stats: {str(e)}')
            )
    
    def _get_redis_stats(self, show_keys=False):
        """Get Redis cache statistics"""
        try:
            from django_redis import get_redis_connection
            redis_client = get_redis_connection("default")
            
            # Get Redis info
            redis_info = redis_client.info()
            
            # Get cache keys  
            all_keys = redis_client.keys("*")
            halfnote_keys = [key.decode() if isinstance(key, bytes) else str(key) 
                           for key in all_keys 
                           if (key.decode() if isinstance(key, bytes) else str(key)).startswith('halfnote:')]
            
            # Categorize keys
            key_categories = {}
            for key in halfnote_keys:
                parts = key.split(':')
                category = parts[1] if len(parts) > 1 else 'other'
                if category not in key_categories:
                    key_categories[category] = 0
                key_categories[category] += 1
            
            stats = {
                'cache_type': 'Redis',
                'status': 'Connected',
                'redis_version': redis_info.get('redis_version', 'Unknown'),
                'memory_used': redis_info.get('used_memory_human', 'Unknown'),
                'total_keys': len(all_keys),
                'halfnote_keys': len(halfnote_keys),
                'key_categories': key_categories,
                'uptime_seconds': redis_info.get('uptime_in_seconds', 0),
                'connected_clients': redis_info.get('connected_clients', 0),
            }
            
            if show_keys:
                stats['sample_keys'] = halfnote_keys[:20]  # Show first 20 keys
                if len(halfnote_keys) > 20:
                    stats['sample_keys'].append(f'... and {len(halfnote_keys) - 20} more')
            
            return stats
            
        except Exception as e:
            # Fallback for basic Redis connection test
            try:
                # Test basic cache operations
                cache.set('test_key', 'test_value', 1)
                cache.get('test_key')
                cache.delete('test_key')
                
                return {
                    'cache_type': 'Redis',
                    'status': 'Connected',
                    'redis_version': 'Unknown (limited access)',
                    'memory_used': 'Unknown',
                    'total_keys': 'Unknown',
                    'halfnote_keys': 'Unknown',
                    'note': 'Basic Redis connection verified, but detailed stats unavailable',
                    'error_details': str(e)
                }
            except Exception as cache_error:
                return {
                    'cache_type': 'Redis',
                    'status': 'Error',
                    'error': str(cache_error)
                }
    
    def _get_database_stats(self):
        """Get database cache statistics"""
        from django.db import connection
        
        try:
            with connection.cursor() as cursor:
                # Check if cache table exists
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'cache_table'
                """)
                table_exists = cursor.fetchone()[0] > 0
                
                if not table_exists:
                    return {
                        'cache_type': 'Database',
                        'status': 'Not Setup',
                        'message': 'Run "python manage.py setup_cache" to initialize'
                    }
                
                # Get cache entry count
                cursor.execute("SELECT COUNT(*) FROM cache_table")
                total_entries = cursor.fetchone()[0]
                
                # Get cache size estimation
                cursor.execute("""
                    SELECT pg_size_pretty(pg_total_relation_size('cache_table')) as size
                """)
                table_size = cursor.fetchone()[0]
                
                # Get expired entries
                cursor.execute("SELECT COUNT(*) FROM cache_table WHERE expires < NOW()")
                expired_entries = cursor.fetchone()[0]
                
                return {
                    'cache_type': 'Database',
                    'status': 'Connected',
                    'total_entries': total_entries,
                    'expired_entries': expired_entries,
                    'active_entries': total_entries - expired_entries,
                    'table_size': table_size,
                }
                
        except Exception as e:
            return {
                'cache_type': 'Database',
                'status': 'Error',
                'error': str(e)
            }
    
    def _display_stats(self, stats):
        """Display statistics in a formatted way"""
        self.stdout.write(self.style.SUCCESS('🚀 Cache Statistics'))
        self.stdout.write('=' * 50)
        
        cache_type = stats.get('cache_type', 'Unknown')
        status = stats.get('status', 'Unknown')
        
        if status == 'Error':
            self.stdout.write(self.style.ERROR(f'❌ {cache_type} Cache: {stats.get("error", "Unknown error")}'))
            return
        
        if status == 'Not Setup':
            self.stdout.write(self.style.WARNING(f'⚠️  {cache_type} Cache: {stats.get("message", "Not configured")}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'✅ {cache_type} Cache: {status}'))
        self.stdout.write('')
        
        if cache_type == 'Redis':
            self.stdout.write(f'🔧 Redis Version: {stats.get("redis_version", "Unknown")}')
            self.stdout.write(f'💾 Memory Used: {stats.get("memory_used", "Unknown")}')
            self.stdout.write(f'⏱️  Uptime: {stats.get("uptime_seconds", 0)} seconds')
            self.stdout.write(f'👥 Connected Clients: {stats.get("connected_clients", 0)}')
            self.stdout.write('')
            self.stdout.write(f'🗝️  Total Keys: {stats.get("total_keys", 0)}')
            self.stdout.write(f'🎵 Halfnote Keys: {stats.get("halfnote_keys", 0)}')
            
            categories = stats.get('key_categories', {})
            if categories:
                self.stdout.write('')
                self.stdout.write('📊 Key Categories:')
                for category, count in categories.items():
                    self.stdout.write(f'   • {category}: {count}')
            
            if 'sample_keys' in stats:
                self.stdout.write('')
                self.stdout.write('🔑 Sample Keys:')
                for key in stats['sample_keys']:
                    self.stdout.write(f'   • {key}')
        
        elif cache_type == 'Database':
            self.stdout.write(f'📊 Total Entries: {stats.get("total_entries", 0)}')
            self.stdout.write(f'✅ Active Entries: {stats.get("active_entries", 0)}')
            self.stdout.write(f'❌ Expired Entries: {stats.get("expired_entries", 0)}')
            self.stdout.write(f'💾 Table Size: {stats.get("table_size", "Unknown")}')
        
        self.stdout.write('')
        self.stdout.write('💡 Tip: Use --json flag for machine-readable output')
        self.stdout.write('💡 Tip: Use --keys flag to see sample cache keys (Redis only)') 