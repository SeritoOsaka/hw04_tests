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
        cls.templates_url_names_public = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username},
            ),
        }

        cls.templates_url_names_private = {
            'posts/post_create.html': reverse('posts:post_create')
        }

        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.author.username},
            ),
            'posts/post_create.html': reverse('posts:post_create'),
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.no_author_client = Client()
        self.no_author_client.force_login(self.no_author)

    def test_urls_guest_user_private(self):
        for template, reverse_name in self.templates_url_names_private.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_user_public(self):
        for template, reverse_name in self.templates_url_names_public.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_user(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_no_authorized_user(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                if reverse_name == reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id},
                ):
                    response = self.no_author_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.no_author_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)