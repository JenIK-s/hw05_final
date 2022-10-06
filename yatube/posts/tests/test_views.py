import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings


from ..models import Group, Post, Comment, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif_1,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='first',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded
        )
        cls.comment_post = Comment.objects.create(
            author=cls.user,
            text='Тестовый текст',
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.pk}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTests.post.pk}
            )
        }

    def post_in_page(self, page_context):
        if 'page_obj' in page_context:
            post = page_context['page_obj'][0]
        else:
            post = page_context['post']
        self.assertEqual(
            post.author,
            PostViewsTests.post.author
        )
        self.assertEqual(
            post.text,
            PostViewsTests.post.text
        )
        self.assertEqual(
            post.group,
            PostViewsTests.post.group
        )
        print(post.image.url)
        self.assertEqual(
            post.comments.last(),
            PostViewsTests.comment_post
        )

    def test_pages_uses_correct_template(self):
        for template, reverse_name in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_show_correct_context(self):
        for url, status_code in self.templates_page_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(status_code)
                page_context = response.context
                self.post_in_page(page_context)

    def test_follow(self):
        follow_count = Follow.objects.count()
        new_author = User.objects.create(username='auth_2')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(follow.author, new_author)
        self.assertEqual(follow.user, PostViewsTests.user)

    def test_unfollow(self):
        follow_count = Follow.objects.count()
        new_author = User.objects.create(username='auth_2')
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': new_author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_in_page(self):
        new_author = User.objects.create(username='auth_2')
        authorized_client = Client()
        authorized_client.force_login(new_author)
        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostViewsTests.user.username}
            )
        )
        follow_response = authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_context = follow_response.context
        self.post_in_page(follow_context)

    def test_unfollow_in_page(self):
        new_author = User.objects.create(username='auth_2')
        authorized_client = Client()
        authorized_client.force_login(new_author)
        response_unfollow = authorized_client.get(
            reverse('posts:follow_index')
        )
        unfollow_context = response_unfollow.context
        self.assertEqual(len(unfollow_context['page_obj']), 0)
