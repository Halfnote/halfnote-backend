"""
Halfnote Accounts Views
Optimized user authentication and profile management with performance improvements
"""

import secrets

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from . import social
from .models import Identity
from .validators import validate_password, validate_username
from .serializers import UserProfileSerializer, UserFollowSerializer, UserSerializer
from music.models import Review
from music.serializers import AlbumSerializer, ReviewSerializer
from music.views import import_album_from_discogs, validation_error

User = get_user_model()

MAX_FAVORITE_ALBUMS = 4


def auth_response(user, status=200):
    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "needs_onboarding": user.onboarded_at is None,
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "avatar": user.avatar.url if user.avatar else None,
                "avatar_preset": user.avatar_preset,
            },
        },
        status=status,
    )


def field_error(field, message):
    return validation_error({field: [message]})


def placeholder_username():
    while True:
        username = f"user{secrets.token_hex(4)}"
        if not User.objects.filter(username=username).exists():
            return username


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    username = (request.data.get("username") or "").strip().lower()

    try:
        validate_email(email)
    except ValidationError:
        return field_error("email", "Enter a valid email address.")
    try:
        validate_password(password)
    except ValidationError as e:
        return field_error("password", e.messages[0])
    if username:
        try:
            validate_username(username)
        except ValidationError as e:
            return field_error("username", e.messages[0])
        if User.objects.filter(username=username).exists():
            return field_error("username", "taken")
    if User.objects.filter(email__iexact=email).exists():
        return field_error("email", "taken")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username or placeholder_username(),
                email=email,
                password=password,
            )
    except IntegrityError:
        return field_error("email", "taken")
    return auth_response(user, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """`login` is a username or an email; `username` is still accepted from older clients."""
    identifier = (
        (request.data.get("login") or request.data.get("username") or "")
        .strip()
        .lower()
    )
    password = request.data.get("password", "")

    if "@" in identifier:
        user = User.objects.filter(email__iexact=identifier).first()
        identifier = user.username if user else ""

    user = authenticate(username=identifier, password=password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=401)
    return auth_response(user)


class RefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except User.DoesNotExist:
            raise InvalidToken("User no longer exists")


SOCIAL_FIELDS = {
    "apple": ["identity_token", "authorization_code", "nonce"],
    "google": ["id_token"],
}


def find_or_create_social_user(provider, verified, name):
    """Returns (identity, created_user)."""
    identity = (
        Identity.objects.select_related("user")
        .filter(provider=provider, subject=verified.subject)
        .first()
    )
    if identity:
        return identity, False

    # Never joined to an existing account by email: register doesn't verify emails, so a match proves nothing.
    email = verified.email if verified.email_verified else ""
    if User.objects.filter(email__iexact=email).exists():
        email = ""
    user = User(
        username=placeholder_username(), email=email, name=(name or verified.name)[:100]
    )
    user.set_unusable_password()
    user.save()
    return Identity.objects.create(
        user=user, provider=provider, subject=verified.subject, email=verified.email
    ), True


@api_view(["POST"])
@permission_classes([AllowAny])
def social_auth(request, provider):
    data = request.data
    missing = [f for f in SOCIAL_FIELDS[provider] if not data.get(f)]
    if missing:
        return field_error(missing[0], "This field is required.")

    try:
        if provider == "apple":
            verified = social.verify_apple(data["identity_token"], data["nonce"])
        else:
            verified = social.verify_google(data["id_token"])
    except social.InvalidToken:
        return Response({"error": f"Invalid {provider.title()} token"}, status=401)

    try:
        with transaction.atomic():
            identity, created = find_or_create_social_user(
                provider, verified, (data.get("name") or "").strip()
            )
    except IntegrityError:
        # A concurrent request created the same account first.
        identity, created = (
            Identity.objects.select_related("user").get(
                provider=provider, subject=verified.subject
            ),
            False,
        )

    if not identity.user.is_active:
        return Response({"error": "Account disabled"}, status=401)

    if provider == "apple":
        # Every sign-in, because reconnecting Halfnote in Apple ID settings replaces the earlier grant.
        refresh_token = social.apple_refresh_token(data["authorization_code"])
        if refresh_token:
            identity.apple_refresh_token = refresh_token
            identity.save(update_fields=["apple_refresh_token"])

    return auth_response(identity.user, status=201 if created else 200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_me(request):
    try:
        for identity in request.user.identities.filter(provider="apple"):
            social.revoke_apple(identity.apple_refresh_token)
    except social.AppleUnavailable:
        return Response(
            {
                "error": "We couldn't reach Apple to disconnect your account, so it hasn't been deleted. Please try again in a few minutes."
            },
            status=503,
        )
    request.user.delete()
    return Response(status=204)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update user profile"""
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    # Handle profile updates
    data = request.data.copy()

    # Handle file uploads
    if "avatar" in request.FILES:
        data["avatar"] = request.FILES["avatar"]
    if "banner" in request.FILES:
        data["banner"] = request.FILES["banner"]

    serializer = UserProfileSerializer(request.user, data=data, partial=True)
    if not serializer.is_valid():
        return validation_error(serializer.errors)
    try:
        serializer.save()
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": f"Profile update failed: {str(e)}"}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_reviews(request, username):
    """Get reviews by a specific user with optimized queries"""
    user = get_object_or_404(User, username=username)

    # Pagination parameters
    offset = int(request.GET.get("offset", 0))
    limit = min(int(request.GET.get("limit", 20)), 50)  # Cap at 50 items

    # Optimized query with all necessary prefetching
    reviews = (
        Review.objects.filter(user=user)
        .select_related("album", "user", "favorite_song")
        .prefetch_related("user_genres", "likes__user", "comments__user")
        .order_by("-created_at")[offset : offset + limit]
    )

    serializer = ReviewSerializer(reviews, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_profile(request, username):
    """Get public user profile"""
    user = get_object_or_404(User, username=username, onboarded_at__isnull=False)
    data = UserProfileSerializer(user, context={"request": request}).data
    data.pop("email")
    return Response({**data, "cached": False})


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    """Follow or unfollow a user"""
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return Response({"error": "Cannot follow yourself"}, status=400)

    if request.method == "POST":
        request.user.following.add(target_user)
        action = "followed"
    else:  # DELETE
        request.user.following.remove(target_user)
        action = "unfollowed"

    return Response(
        {
            "action": action,
            "target_user": username,
            "following_count": request.user.following.count(),
            "followers_count": target_user.followers.count(),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def user_followers(request, username):
    """Get user's followers with optimized queries"""
    user = get_object_or_404(User, username=username)

    offset = int(request.GET.get("offset", 0))
    limit = min(int(request.GET.get("limit", 20)), 50)  # Cap at 50 items

    # Optimized query with prefetching (avatar is an ImageField, not relational)
    followers = user.followers.prefetch_related("followers", "following")[
        offset : offset + limit
    ]

    serializer = UserFollowSerializer(
        followers, many=True, context={"request": request}
    )

    # Return array directly as expected by frontend
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_following(request, username):
    """Get users that this user follows with optimized queries"""
    user = get_object_or_404(User, username=username)

    offset = int(request.GET.get("offset", 0))
    limit = min(int(request.GET.get("limit", 20)), 50)  # Cap at 50 items

    # Optimized query with prefetching (avatar is an ImageField, not relational)
    following = user.following.prefetch_related("followers", "following")[
        offset : offset + limit
    ]

    serializer = UserFollowSerializer(
        following, many=True, context={"request": request}
    )

    # Return array directly as expected by frontend
    return Response(serializer.data)


# ============================================================================
# MISSING VIEWS THAT FRONTEND EXPECTS
# ============================================================================


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """Unfollow a user (same as DELETE on follow_user)"""
    return follow_user(request, username)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_users(request):
    """Search for users"""
    query = request.GET.get("q", "")
    if not query:
        return Response({"users": []})

    users = User.objects.filter(username__icontains=query, onboarded_at__isnull=False)[
        :20
    ]
    serializer = UserSerializer(users, many=True, context={"request": request})

    return Response({"users": serializer.data})


@api_view(["GET"])
@permission_classes([AllowAny])
def user_genre_stats(request, username):
    """Get genre statistics for a user"""
    user = get_object_or_404(User, username=username)

    # This would typically aggregate genre data from user's reviews
    # For now, return a simple response
    return Response(
        {"user": username, "genres": [], "message": "Genre stats not implemented yet"}
    )


@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def favorite_albums(request):
    """Manage user's favorite albums"""
    if request.method == "GET":
        # Get user's favorite albums
        favorite_albums = request.user.favorite_albums.all()
        serializer = AlbumSerializer(favorite_albums, many=True)
        return Response({"albums": serializer.data})

    elif request.method == "POST":
        discogs_id = request.data.get("discogs_id")
        if not discogs_id:
            return Response({"error": "discogs_id required"}, status=400)
        if (
            request.user.favorite_albums.exclude(discogs_id=discogs_id).count()
            >= MAX_FAVORITE_ALBUMS
        ):
            return field_error(
                "discogs_id",
                f"You can have at most {MAX_FAVORITE_ALBUMS} favourite albums.",
            )
        album = import_album_from_discogs(discogs_id)
        if album is None:
            return field_error("discogs_id", f"unknown album {discogs_id}")
        request.user.favorite_albums.add(album)
        return Response({"message": "Album added to favorites"})

    elif request.method == "PUT":
        discogs_ids = request.data.get("discogs_ids")
        if not isinstance(discogs_ids, list) or not all(
            isinstance(i, str) for i in discogs_ids
        ):
            return field_error("discogs_ids", "Send a list of Discogs IDs.")
        discogs_ids = list(dict.fromkeys(discogs_ids))
        if len(discogs_ids) > MAX_FAVORITE_ALBUMS:
            return field_error(
                "discogs_ids",
                f"You can have at most {MAX_FAVORITE_ALBUMS} favourite albums.",
            )
        albums = []
        for discogs_id in discogs_ids:
            album = import_album_from_discogs(discogs_id)
            if album is None:
                return field_error("discogs_ids", f"unknown album {discogs_id}")
            albums.append(album)
        request.user.favorite_albums.set(albums)
        return Response({"albums": AlbumSerializer(albums, many=True).data})

    elif request.method == "DELETE":
        # Remove album from favorites
        discogs_id = request.data.get("discogs_id")
        if not discogs_id:
            return Response({"error": "discogs_id required"}, status=400)

        from music.models import Album

        album = get_object_or_404(Album, discogs_id=discogs_id)
        request.user.favorite_albums.remove(album)

        return Response({"message": "Album removed from favorites"})


@api_view(["GET"])
@permission_classes([AllowAny])
def user_activity(request, username):
    """Get activity feed for a specific user with optimized queries"""
    user = get_object_or_404(User, username=username)

    from music.models import Activity
    from music.serializers import ActivitySerializer

    # Optimized query with comprehensive prefetching
    activities = (
        Activity.objects.filter(user=user)
        .select_related(
            "user", "target_user", "review__user", "review__album", "comment__user"
        )
        .prefetch_related("review__user_genres", "review__likes", "review__comments")
        .order_by("-created_at")[:20]
    )

    serializer = ActivitySerializer(activities, many=True, context={"request": request})
    return Response(serializer.data)

