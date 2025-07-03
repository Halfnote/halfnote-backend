from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_username(value):
    """Validate username format and check for blocked usernames"""
    # List of blocked usernames
    blocked_usernames = {
        'vivek',
        'admin', 'administrator', 'root', 'api', 'www', 'mail', 'ftp',
        'support', 'help', 'info', 'contact', 'about', 'terms', 'privacy',
        'security', 'staff', 'moderator', 'mod', 'null', 'undefined'
    }
    
    if len(value) < 3:
        raise ValidationError(
            _('Username must be at least 3 characters long.')
        )
    if len(value) > 30:
        raise ValidationError(
            _('Username must be at most 30 characters long.')
        )
    if not value.isalnum():
        raise ValidationError(
            _('Username must contain only letters and numbers.')
        )
    if value != value.lower():
        raise ValidationError(
            _('Username must be lowercase only.')
        )
    if value.lower() in blocked_usernames:
        raise ValidationError(
            _('This username is not available. Please choose a different one.')
        )

def validate_password(value):
    """Validate password strength"""
    if len(value) < 8:
        raise ValidationError(
            _('Password must be at least 8 characters long.')
        )
    if not any(c.isupper() for c in value):
        raise ValidationError(
            _('Password must contain at least one uppercase letter.')
        )
    if not any(c.islower() for c in value):
        raise ValidationError(
            _('Password must contain at least one lowercase letter.')
        )
    if not any(c.isdigit() for c in value):
        raise ValidationError(
            _('Password must contain at least one number.')
        )
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in value):
        raise ValidationError(
            _('Password must contain at least one special character.')
        )

def validate_bio(value):
    """Validate bio length"""
    if value and len(value) > 500:
        raise ValidationError(
            _('Bio must be at most 500 characters long.')
        )

def validate_avatar_url(value):
    """Validate avatar URL format"""
    if value and not value.startswith(('http://', 'https://')):
        raise ValidationError(
            _('Avatar URL must start with http:// or https://')
        )

def validate_favorite_genres(value):
    """Validate favorite genres format"""
    if not isinstance(value, list):
        raise ValidationError(
            _('Favorite genres must be a list.')
        )
    if len(value) > 10:
        raise ValidationError(
            _('You can only have up to 10 favorite genres.')
        )
    for genre in value:
        if not isinstance(genre, str):
            raise ValidationError(
                _('Each genre must be a string.')
            )
        if len(genre) > 50:
            raise ValidationError(
                _('Genre name must be at most 50 characters long.')
            ) 