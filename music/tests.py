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


class ActivityFeedFreshnessTests(TestCase):
    def setUp(self):
        cache.clear()
        self.author = User.objects.create_user(username='author', password='pw')
        self.follower = User.objects.create_user(username='follower', password='pw')
        self.follower.following.add(self.author)
        self.album = Album.objects.create(
            title='Album', artist='Artist', discogs_id='123',
            artist_photo_url='https://example.com/a.jpg',
        )
        self.add_review('old')

    def add_review(self, discogs_id):
        album = Album.objects.create(title=discogs_id, artist='X', discogs_id=discogs_id)
        review = Review.objects.create(album=album, user=self.author, rating=8)
        Activity.objects.create(user=self.author, activity_type='review_created', review=review)

    def feed(self, user, query):
        response = client_for(user).get(f'/api/music/activity/?{query}')
        self.assertEqual(response.status_code, 200)
        return [a['id'] for a in response.data]

    def post_review(self):
        response = client_for(self.author).post('/api/music/albums/123/review/', {'rating': 8}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_new_review_shows_in_authors_feed(self):
        self.assertEqual(len(self.feed(self.author, 'type=you')), 1)
        self.post_review()
        self.assertEqual(len(self.feed(self.author, 'type=you')), 2)

    def test_new_review_shows_in_followers_feed(self):
        self.assertEqual(len(self.feed(self.follower, 'type=friends')), 1)
        self.post_review()
        self.assertEqual(len(self.feed(self.follower, 'type=friends')), 2)

    def test_feed_pages_differ(self):
        self.add_review('x1')
        self.add_review('x2')
        page1 = self.feed(self.follower, 'type=friends&offset=0&limit=2')
        page2 = self.feed(self.follower, 'type=friends&offset=2&limit=2')
        self.assertEqual((len(page1), len(page2)), (2, 1))
