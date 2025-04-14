from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from accounts.models import UserProfile, List, ListItem
from music.serializers import AlbumSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'bio', 'avatar_url', 'followers_count', 'following_count', 
                  'reviews_count', 'is_following', 'created_at')
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.profile in obj.followers.all()
        return False
    
    def update(self, instance, validated_data):
        # Update User model fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class ListItemSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    album_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ListItem
        fields = ('id', 'album', 'album_id', 'notes', 'order')
        
    def create(self, validated_data):
        album_id = validated_data.pop('album_id')
        list_instance = validated_data.pop('list')
        return ListItem.objects.create(
            album_id=album_id,
            list=list_instance,
            **validated_data
        )


class ListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = serializers.SerializerMethodField()
    albums_count = serializers.SerializerMethodField()
    
    class Meta:
        model = List
        fields = ('id', 'title', 'description', 'user', 'list_type', 
                  'items', 'albums_count', 'created_at', 'updated_at')
        
    def get_items(self, obj):
        # Only return items if detailed=True is passed in the context
        if self.context.get('detailed', False):
            items = obj.listitem_set.all().order_by('order')
            return ListItemSerializer(items, many=True, context=self.context).data
        return []
    
    def get_albums_count(self, obj):
        return obj.albums.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 