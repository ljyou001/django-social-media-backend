from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from utils.paginations import EndlessPagination

# 注意要加 '/' 结尾，要不然会产生 301 redirect
# 以防写错，最好在最上面先写好API endpoint
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIVE_API = '/api/tweets/{}/'

class TweetApiTests(TestCase):

    def setUp(self):
        # This function will be executed once before each test function

        # Here you can see how to distinguish anonymous user and logged in user
        # self.anonymous_client = APIClient()
        super(TweetApiTests, self).setUp()
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        # force_authenticate means to request api with a logged in user

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # 必须带 user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # 正常 request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['results']), 2)
        # 检测排序是按照新创建的在前面的顺序来的
        self.assertEqual(response.data['results'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['results'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # 必须登录
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # 必须带 content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)
        # content 不能太短
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        # content 不能太长
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0' * 161
        })
        self.assertEqual(response.status_code, 400)

        # 正常发帖
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrive(self):
        
        # Negative test: provide a non-existed tweet id
        url = TWEET_RETRIVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # Positive test: Check the tweet and comments 
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], tweet.id)
        self.assertEqual(len(response.data['comments']), 0)

        # Positive test: Add some comments
        self.create_comment(self.user1, tweet, "comment1")
        self.create_comment(self.user2, tweet, "comment2")
        self.create_comment(self.user1, self.create_tweet(self.user2), "comment3")
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

    def test_create_with_files(self):
        # Positive test: Create a tweet with without file arrtibute
        # To compatible old version API
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # Positive test: Create a tweet with no file
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my second tweet!',
            'files': []
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # Negative case: Upload file not using the list
        file = SimpleUploadedFile(
            name='selfie.png',
            content=str.encode('a fake photo'),
            content_type='image/png'
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!',
            'files': file,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # Positive case: Upload 1 file
        file = SimpleUploadedFile(
            name='selfie.png',
            content=str.encode('a fake photo'),
            content_type='image/png'
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!',
            'files': [file],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 2)

        # Positive case: Upload multiple files
        file1 = SimpleUploadedFile(
            name='selfie1.png',
            content=str.encode('selfie 1'),
            content_type='image/png'
        )
        file2 = SimpleUploadedFile(
            name='selfie2.png',
            content=str.encode('selfie 2'),
            content_type='image/png'
        )
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'I am uploading 2 files!',
            'files': [file1, file2],
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 4)

        # Positive case: Retrieve the created tweet with photo urls
        retrive_url = TWEET_RETRIVE_API.format(response.data['id'])
        response = self.anonymous_client.get(retrive_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['photo_urls']), 2)
        self.assertEqual('selfie1' in response.data['photo_urls'][0], True)
        self.assertEqual('selfie2' in response.data['photo_urls'][1], True)

        # Negative case: Upload too many files
        files = [
            SimpleUploadedFile(
                name=f'selfie{i}.png',
                content=str.encode(f'selfie{i}'),
                content_type='image/png'
            )
            for i in range(5)
        ]
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'I am uploading too many files',
            'files': files
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 4)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        max_upside_paginate = EndlessPagination.max_upside_paginate

        # Create 2 * page_size of tweets
        # we have created self.tweets1 in setUp 
        for i in range(page_size * 2 - len(self.tweets1)):
            self.tweets1.append(
                self.create_tweet(self.user1, 'tweet{}'.format(i))
            )
        tweets = self.tweets1[::-1]

        # pull the first page
        response = self.user1_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(response.data['results'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[page_size - 1].id)

        # pull the second page
        response = self.user1_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id, 
            'created_at__lt': tweets[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(response.data['results'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['results'][1]['id'], tweets[page_size + 1].id)
        self.assertEqual(response.data['results'][page_size - 1]['id'], tweets[2 * page_size - 1].id)

        # pull the latest tweets
        response = self.user1_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(len(response.data['results']), 0)

        # One new tweets
        new_tweet = self.create_tweet(self.user1, 'a new tweet')
        response = self.user1_client.get(TWEET_LIST_API, {
            'user_id': self.user1.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(response.data['beyond_upside_paginate'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], new_tweet.id)
        
        # # Too many new tweets
        # new_tweets = []
        # for i in range(max_upside_paginate + 2):
        #     new_tweets.append(
        #         self.create_tweet(self.user1, 'new tweet{}'.format(i))
        #     )
        # new_tweets = new_tweets[::-1]
        # response = self.user1_client.get(TWEET_LIST_API, {
        #     'user_id': self.user1.id,
        #     'created_at__gt': tweets[0].created_at,
        # })
        # self.assertEqual(response.data['has_next_page'], True)
        # self.assertEqual(response.data['beyond_upside_paginate'], True)
        # self.assertEqual(len(response.data['results']), page_size)
        # self.assertEqual(response.data['results'][0]['id'], new_tweets[0].id)
        # self.assertEqual(response.data['results'][1]['id'], new_tweets[1].id)
        # self.assertEqual(response.data['results'][page_size - 1]['id'], new_tweets[page_size - 1].id)
        # 
        # WHY DELETED?
        # Current version of cached tweets list pagination does not support max_upside_paginate.