from django.test import TestCase, Client
from ..models import Post, Group
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='first',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostUrlTests.user)
        self.url_status = {
            '/': HTTPStatus.OK,
            '/group/first/': HTTPStatus.OK,
            '/profile/Name/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            f'/profile/{self.user.username}/follow/': HTTPStatus.FOUND,
            f'/profile/{self.user.username}/unfollow/': HTTPStatus.FOUND
        }
        self.link_tuple = (
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
            'posts/follow.html',
            'posts/follow.html',
        )

    def test_urls_not_auth(self):
        for url, status_code in self.url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_auth(self):
        url_status_auth = self.url_status
        url_status_auth[f'/posts/{self.post.pk}/edit/'] = HTTPStatus.OK
        url_status_auth['/create/'] = HTTPStatus.OK

        for url, status_code in url_status_auth.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)
