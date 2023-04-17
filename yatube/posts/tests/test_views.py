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
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}),
        ]
        for url in urls:
            with self.subTest(msg=f'Test {url} page'):
                response = self.authorized_client.get(url)
                page_obj = response.context.get('page_obj')[0]
                self.assertEqual(page_obj, self.post)

    def test_post_detail_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
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

    def test_post_does_not_appear_on_other_group_pages(self):
        group1 = Group.objects.create(title='Group 1', slug='group-1')
        group2 = Group.objects.create(title='Group 2', slug='group-2')
        post1 = Post.objects.create(author=self.user,
                                    text='Post 1',
                                    group=group1)
        post2 = Post.objects.create(author=self.user,
                                    text='Post 2',
                                    group=group2)

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'group-1'})
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0], post1)

        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'group-2'}))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0], post2)
