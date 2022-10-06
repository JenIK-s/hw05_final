from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

from django.conf import settings

User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='name')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='first',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый т',
            group=cls.group
        )

    def test_verbose_name(self):
        post = PostModelTests.post
        field_verboses = {
            'text': 'text',
            'group': 'group'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = PostModelTests.post
        field_help_texts = {
            'text': '',
            'group': ''
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_object_name_group_post(self):
        group = PostModelTests.group
        post = PostModelTests.post
        self.assertEqual(str(post), post.text[:settings.COUNT_POSTS])
        self.assertEqual(str(group), group.title)
