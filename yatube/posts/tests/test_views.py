from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.test_user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)
        self.guest_client = Client()

    def test_post_context(self):
        response_index = self.authorized_client.get(reverse('posts:index'))
        test_object_index = response_index.context.get('page_obj')[0]

        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        test_object_group = response_group.context['page_obj'][0]

        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username})
        )
        test_object_profile = response_profile.context.get('page_obj')[0]

        with self.subTest(msg='Test index page'):
            self.assertEqual(test_object_index, self.post)

        with self.subTest(msg='Test group page'):
            self.assertEqual(test_object_group, self.post)

        with self.subTest(msg='Test profile page'):
            self.assertEqual(test_object_profile, self.post)

    def test_post_detail_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        test_post = response.context['post']
        test_post_count = response.context['posts_count']
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post_count, self.post.author.posts.count())

    def test_edit_post_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )

        self.assertTrue(response.context['is_edit'])
        self.assertEqual(response.context.get('form').instance, self.post)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_create_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create'))

        self.assertIsInstance(response.context.get('form'), PostForm)
