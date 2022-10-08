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
            '/': (
                'posts/index.html',
                HTTPStatus.OK
            ),
            '/group/first/': (
                'posts/group_list.html',
                HTTPStatus.OK
            ),
            '/profile/Name/': (
                'posts/profile.html',
                HTTPStatus.OK
            ),
            f'/posts/{self.post.pk}/': (
                'posts/post_detail.html',
                HTTPStatus.OK
            ),
            f'/posts/{self.post.pk}/edit/': (
                'posts/create_post.html',
                HTTPStatus.FOUND
            ),
            '/create/': ('posts/create_post.html', HTTPStatus.FOUND),
            f'/profile/{self.user.username}/follow/': (
                'posts/follow.html',
                HTTPStatus.FOUND
            ),
            f'/profile/{self.user.username}/unfollow/': (
                'posts/follow.html',
                HTTPStatus.FOUND
            )
        }

    def test_urls_not_auth(self):
        for url, status_code in self.url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                status_code = status_code[1]
                self.assertEqual(response.status_code, status_code)

    def test_urls_auth(self):
        self.url_status[f'/posts/{self.post.pk}/edit/'] = (
            'posts/create_post.html',
            HTTPStatus.OK
        )
        self.url_status['/create/'] = ('posts/create_post.html', HTTPStatus.OK)
        for url, status_code in self.url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                status_code = status_code[1]
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        count = 0
        for reverse_name, template in self.url_status.items():
            if count == 6:
                break
            else:
                count += 1
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    template = template[0]
                    self.assertTemplateUsed(response, template)
