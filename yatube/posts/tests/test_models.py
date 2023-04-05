from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class GroupModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Тестовая группа')

    def test_group_str_title(self):
        group = GroupModelsTest.group
        self.assertEqual(str(group), group.title)

    def test_group_verbose_name(self):
        group = GroupModelsTest.group
        field_verbose = {
            'title': 'Название группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Тестовый пользователь')
        cls.group = Group.objects.create(title='Тестовая группа')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def test_post_str_text(self):
        post = PostModelsTest.post
        text = post.text
        self.assertEqual(str(post), text[:15])

    def test_post_verbose_name(self):
        post = PostModelsTest.post
        field_verbose = {
            'text': 'Текст статьи',
            'pub_date': 'Дата публикации',
            'author': 'Автор статьи',
            'group': 'Группа статей',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )
