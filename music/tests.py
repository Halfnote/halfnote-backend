from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from music.models import Activity, Album, Genre, Review
from music.services import ExternalMusicService

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


DISCOGS_ALBUM = {
    'title': 'OK Computer', 'artist': 'Radiohead', 'year': 1997,
    'genres': ['Rock'], 'styles': ['Alternative Rock'],
    'cover_image': 'https://example.com/cover.jpg', 'discogs_id': '777',
    'tracklist': [{'position': '1', 'title': 'Airbag', 'duration': '4:44', 'artists': [], 'extraartists': []}],
    'credits': [{'name': 'Nigel Godrich', 'role': 'Producer', 'id': 1}],
}


@patch('music.views.get_artist_photo', return_value='https://example.com/artist.jpg')
@patch.object(ExternalMusicService, 'search_artist', return_value=None)
@patch.object(ExternalMusicService, 'get_album_details', return_value=DISCOGS_ALBUM)
class DiscogsImportTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='u', password='pw')

    def assert_saved_in_full(self):
        album = Album.objects.get(discogs_id='777')
        self.assertEqual(
            (album.tracklist, album.credits, album.discogs_genres, album.discogs_styles, album.cover_url),
            (DISCOGS_ALBUM['tracklist'], DISCOGS_ALBUM['credits'], ['Rock'], ['Alternative Rock'],
             'https://example.com/cover.jpg'))

    def test_first_album_view_saves_album_and_returns_serializer_shape(self, *_):
        data = client_for(self.user).get('/api/music/albums/777/').data
        self.assert_saved_in_full()
        self.assertTrue(data['exists_in_db'])
        self.assertEqual(data['album']['cover_url'], 'https://example.com/cover.jpg')
        self.assertEqual(data['album']['tracklist'], DISCOGS_ALBUM['tracklist'])

    def test_first_review_saves_album_in_full(self, *_):
        response = client_for(self.user).post('/api/music/albums/777/review/', {'rating': 9}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assert_saved_in_full()


@patch.object(ExternalMusicService, 'get_artist_details', return_value={
    'discogs_id': '42', 'name': 'Radiohead', 'primary_image_url': 'https://example.com/artist.jpg'})
@patch.object(ExternalMusicService, 'search_artist', return_value='42')
@patch.object(ExternalMusicService, 'get_album_details', return_value=DISCOGS_ALBUM)
class AlbumArtistPhotoTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = client_for(User.objects.create_user(username='u', password='pw'))

    def test_album_photo_comes_from_artist_row_without_refetching(self, *mocks):
        with patch('music.views.get_artist_photo', return_value=None) as photo:
            self.client.get('/api/music/albums/777/')
            self.client.get('/api/music/albums/777/')

        self.assertEqual(photo.call_count, 0)
        self.assertEqual(Album.objects.get(discogs_id='777').artist_photo_url, 'https://example.com/artist.jpg')
        self.assertEqual([m.call_count for m in mocks], [1, 1, 1])


class SearchArtistPhotoTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_photo_fetched_once_per_artist_across_searches(self):
        hits = [{'id': i, 'title': 'Radiohead - Album %d' % i} for i in range(5)]
        with patch('music.views.search_discogs', return_value=hits), \
                patch('music.views.get_artist_photo', return_value='https://example.com/r.jpg') as photo:
            first = APIClient().get('/api/music/search/', {'q': 'radiohead'})
            APIClient().get('/api/music/search/', {'q': 'radiohead ok'})

        self.assertEqual(photo.call_count, 1)
        self.assertEqual({r['artist_photo_url'] for r in first.json()['results']}, {'https://example.com/r.jpg'})


class ReviewConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='pw')
        self.album = Album.objects.create(title='Album', artist='Artist', discogs_id='123')

    def test_review_needs_rating_or_headline(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Review.objects.create(album=self.album, user=self.user, rating=None, headline='')


class CreateReviewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='u', password='pw')
        Album.objects.create(title='Album', artist='Artist', discogs_id='123')

    def post(self, body):
        return client_for(self.user).post('/api/music/albums/123/review/', body, format='json')

    def test_needs_rating_or_headline(self):
        response = self.post({'body': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Add a rating or a headline')

    def test_short_take_without_rating(self):
        response = self.post({'headline': 'Great record'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            (response.data['rating'], response.data['headline'], response.data['body'], response.data['content']),
            (None, 'Great record', '', 'Great record'))

    def test_full_review_content_joins_headline_and_body(self):
        response = self.post({'rating': 8, 'headline': 'Great record', 'body': 'Track 3.\nThe closer.'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'Great record\n\nTrack 3.\nThe closer.')

    def test_rejects_body_without_headline(self):
        response = self.post({'rating': 8, 'body': 'Orphan body'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('body', response.data['fields'])

    def test_rejects_bad_fields(self):
        cases = [
            ({'rating': 11}, 'rating'),
            ({'rating': 8, 'headline': 'x' * 151}, 'headline'),
            ({'rating': 8, 'headline': 'two\nlines'}, 'headline'),
            ({'rating': 8, 'headline': 'h', 'body': 'x' * 5001}, 'body'),
        ]
        for body, field in cases:
            with self.subTest(field=field, body=str(body)[:40]):
                response = self.post(body)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(list(response.data['fields']), [field])

    def test_second_review_of_same_album_is_a_new_review(self):
        self.assertEqual(self.post({'rating': 6}).status_code, 201)
        self.assertEqual(self.post({'rating': 9}).status_code, 201)
        self.assertEqual(Review.objects.filter(user=self.user).count(), 2)


class EditReviewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='u', password='pw')
        album = Album.objects.create(title='Album', artist='Artist', discogs_id='123')
        self.review = Review.objects.create(album=album, user=self.user, rating=7, headline='Head', body='Body')
        self.review.user_genres.add(Genre.objects.get_or_create(name='Rock')[0])

    def put(self, body, user=None):
        return client_for(user or self.user).put(f'/api/music/reviews/{self.review.id}/', body, format='json')

    def test_keys_left_out_keep_their_values(self):
        response = self.put({'rating': 9})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            (response.data['rating'], response.data['headline'], response.data['body']), (9, 'Head', 'Body'))
        self.assertEqual([g['name'] for g in response.data['user_genres']], ['Rock'])

    def test_null_clears_rating_and_empty_body_makes_short_take(self):
        response = self.put({'rating': None, 'body': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.data['rating'], response.data['content']), (None, 'Head'))

    def test_rejects_change_leaving_no_rating_or_headline(self):
        response = self.put({'rating': None, 'headline': '', 'body': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Add a rating or a headline')

    def test_only_owner_can_edit(self):
        other = User.objects.create_user(username='o', password='pw')
        self.assertEqual(self.put({'rating': 1}, other).status_code, 403)


class RepeatReviewStatsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.album = Album.objects.create(title='Album', artist='Artist', discogs_id='123')
        self.a = User.objects.create_user(username='a', password='pw')
        self.b = User.objects.create_user(username='b', password='pw')
        self.minute = 0

    def review(self, user, rating, headline='h'):
        from datetime import timedelta
        from django.utils import timezone
        self.minute += 1
        return Review.objects.create(
            album=self.album, user=user, rating=rating, headline=headline,
            created_at=timezone.now() + timedelta(minutes=self.minute))

    def test_album_average_uses_each_users_latest_rated_review(self):
        self.review(self.a, 4)
        self.review(self.a, 10)
        self.review(self.b, 6)
        self.review(self.b, None)
        data = client_for(self.a).get('/api/music/albums/123/').data
        self.assertEqual((data['average_rating'], data['review_count'], len(data['reviews'])), (8, 2, 4))

    def test_album_card_shows_most_recent_review(self):
        self.review(self.a, 4)
        latest = self.review(self.a, None)
        self.a.favorite_albums.add(self.album)
        card = client_for(self.a).get('/api/accounts/users/a/').data['favorite_albums'][0]
        self.assertEqual((card['user_review_id'], card['user_rating']), (latest.id, None))


class ActivityHeadlineTests(TestCase):
    def test_feed_carries_whole_headline_and_body(self):
        user = User.objects.create_user(username='u', password='pw')
        album = Album.objects.create(title='Album', artist='Artist', discogs_id='123')
        headline = 'x' * 150
        review = Review.objects.create(album=album, user=user, headline=headline, body='More')
        Activity.objects.create(user=user, activity_type='review_created', review=review)
        details = client_for(user).get('/api/music/activity/?type=you').data[0]['review_details']
        self.assertEqual((details['headline'], details['body'], details['rating']), (headline, 'More', None))
