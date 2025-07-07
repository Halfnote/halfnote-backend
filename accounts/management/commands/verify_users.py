"""
Management command to verify specific users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Verify specific users by giving them verified checkmarks'

    def add_arguments(self, parser):
        parser.add_argument(
            'usernames',
            nargs='+',
            type=str,
            help='Usernames to verify'
        )
        parser.add_argument(
            '--unverify',
            action='store_true',
            help='Remove verification instead of adding it',
        )

    def handle(self, *args, **options):
        usernames = options['usernames']
        unverify = options['unverify']
        
        action = 'Removing verification from' if unverify else 'Verifying'
        self.stdout.write(f'{action} users: {", ".join(usernames)}')
        
        verified_count = 0
        not_found_count = 0
        
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                if unverify:
                    user.is_verified = False
                    action_word = 'unverified'
                else:
                    user.is_verified = True
                    action_word = 'verified'
                
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {username} has been {action_word}')
                )
                verified_count += 1
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ User "{username}" not found')
                )
                not_found_count += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {verified_count} users')
        )
        if not_found_count > 0:
            self.stdout.write(
                self.style.ERROR(f'{not_found_count} users not found')
            ) 