from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from music.models import Activity, Album, Review

User = get_user_model()


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


class ViewerSpecificFieldTests(TestCase):
    def setUp(self):
        cache.clear()
        self.enterContext(patch('music.views.get_artist_photo', return_value=None))
        self.author = User.objects.create_user(username='author', password='pw')
        self.alice = User.objects.create_user(username='alice', password='pw')
        self.bob = User.objects.create_user(username='bob', password='pw')
        self.album = Album.objects.create(title='Album', artist='Artist', discogs_id='123')
        self.review = Review.objects.create(album=self.album, user=self.author, rating=8)
        Activity.objects.create(user=self.author, activity_type='review_created', review=self.review)

    def get_as(self, user, url):
        response = client_for(user).get(url)
        self.assertEqual(response.status_code, 200)
        return response.data

    def like_as(self, user):
        self.assertEqual(client_for(user).post(f'/api/music/reviews/{self.review.id}/like/').status_code, 200)

    def assert_liked_per_viewer(self, url, pick):
        self.like_as(self.alice)
        self.assertTrue(pick(self.get_as(self.alice, url))['is_liked_by_user'])
        self.assertFalse(pick(self.get_as(self.bob, url))['is_liked_by_user'])

    def test_album_detail(self):
        self.assert_liked_per_viewer('/api/music/albums/123/', lambda d: d['reviews'][0])

    def test_user_reviews(self):
        self.assert_liked_per_viewer('/api/accounts/users/author/reviews/', lambda d: d[0])

    def test_user_activity(self):
        self.assert_liked_per_viewer('/api/accounts/users/author/activity/', lambda d: d[-1]['review_details'])

    def test_review_likes_with_review(self):
        self.assert_liked_per_viewer(
            f'/api/music/reviews/{self.review.id}/likes/?include_review=true', lambda d: d['review'])

    def test_user_profile_is_following(self):
        client_for(self.alice).post('/api/accounts/users/author/follow/')
        self.assertTrue(self.get_as(self.alice, '/api/accounts/users/author/')['is_following'])
        self.assertFalse(self.get_as(self.bob, '/api/accounts/users/author/')['is_following'])

    def test_followers_list_is_following(self):
        client_for(self.alice).post('/api/accounts/users/author/follow/')
        client_for(self.alice).post('/api/accounts/users/bob/follow/')
        client_for(self.bob).post('/api/accounts/users/author/follow/')
        url = '/api/accounts/users/author/followers/'
        as_alice = {u['username']: u['is_following'] for u in self.get_as(self.alice, url)}
        as_author = {u['username']: u['is_following'] for u in self.get_as(self.author, url)}
        self.assertEqual(as_alice['bob'], True)
        self.assertEqual(as_author['bob'], False)
