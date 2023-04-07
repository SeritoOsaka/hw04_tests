from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test title',
            slug='slug',
            description='Test description',
        )
        cls.author = User.objects.create_user(username='Test User')
        cls.no_author = User.objects.create_user(
            username='Non authorized user'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Test Post',
        )
        cls.templates_url_names = {
            'posts/index.html': {
                'url': reverse('posts:index'),
                'authorized': False,
            },
            'posts/group_list.html': {
                'url': reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group.slug},
                ),
                'authorized': False,
            },
            'posts/profile.html': {
                'url': reverse(
                    'posts:profile',
                    kwargs={'username': cls.author.username},
                ),
                'authorized': False,
            },
            'posts/post_create.html': {
                'url': reverse('posts:post_create'),
                'authorized': True,
            },
            'posts/post_edit.html': {
                'url': reverse(
                    'posts:post_edit',
                    kwargs={'post_id': cls.post.id},
                ),
                'authorized': True,
            },
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.no_author_client = Client()

    def test_urls_accessibility(self):
        for template, data in self.templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(data['url'])
                expected_status = (
                    HTTPStatus.OK if not data['authorized']
                    else HTTPStatus.FOUND
                )

                self.assertEqual(response.status_code, expected_status)

                self.authorized_client.login(username=self.author.username,
                                             password='password')
                response = self.authorized_client.get(data['url'])
                expected_status = (
                    HTTPStatus.OK if data['authorized']
                    else HTTPStatus.FOUND
                )
                self.assertEqual(response.status_code, expected_status)

                response = self.no_author_client.get(data['url'])
                expected_status = (
                    HTTPStatus.OK if not data['authorized']
                    or template == 'posts/post_edit.html' else HTTPStatus.FOUND
                )
                self.assertEqual(response.status_code, expected_status)

    def test_urls_use_correct_template(self):
        for template, data in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(data['url'])
                self.assertTemplateUsed(response, template)
