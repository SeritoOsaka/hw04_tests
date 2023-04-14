import math
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()

INDEX = reverse('posts:index')
PROFILE = reverse('posts:profile', kwargs={'username': 'User'})


class PaginatorViewsTest(TestCase):

    @classmethod
    @transaction.atomic
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.NUM_POSTS_TO_CREATE = 13
        posts_to_create = []
        for _ in range(cls.NUM_POSTS_TO_CREATE):
            posts_to_create.append(Post(author=cls.user, group=cls.group))
        Post.objects.bulk_create(posts_to_create)

    def setUp(self):
        self.authorized_client = Client()
        self.num_pages = math.ceil(
            self.NUM_POSTS_TO_CREATE / settings.VIEW_COUNT)

    def test_first_page_contains_ten_records(self):
        urls = [INDEX,
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                PROFILE]

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), settings.VIEW_COUNT)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(INDEX + '?page=2')
        num_posts_on_page = len(response.context['page_obj'])
        num_pages = response.context['page_obj'].paginator.num_pages
        self.assertEqual(
            num_posts_on_page,
            min(settings.VIEW_COUNT,
                self.NUM_POSTS_TO_CREATE - settings.VIEW_COUNT)
        )
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(num_pages, math.ceil(
            self.NUM_POSTS_TO_CREATE / settings.VIEW_COUNT))

        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
        self.assertEqual(
            response.context['page_obj'].number, 2)
        self.assertEqual(
            response.context['page_obj'].paginator.num_pages, self.num_pages)

        response = self.authorized_client.get(PROFILE + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
        self.assertEqual(
            response.context['page_obj'].number, 2)
        self.assertEqual(
            response.context['page_obj'].paginator.num_pages, self.num_pages)
