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
        cls.num_pages = math.ceil(
            cls.NUM_POSTS_TO_CREATE / settings.VIEW_COUNT)
        cls.TEST_URLS = [INDEX,
                         reverse('posts:group_list',
                                 kwargs={'slug': cls.group.slug}), PROFILE]

    def setUp(self):
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        for url in self.TEST_URLS:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']), settings.VIEW_COUNT)

    def test_second_page_contains_correct_number_of_records(self):
        for url in self.TEST_URLS:
            with self.subTest(url=url):
                if url == INDEX:
                    response = self.authorized_client.get(url + '?page=2')
                    last_page_post = (
                        self.NUM_POSTS_TO_CREATE - settings.VIEW_COUNT
                    )
                else:
                    response = self.authorized_client.get(url + '?page=2')
                    last_page_post = (
                        self.NUM_POSTS_TO_CREATE % settings.VIEW_COUNT
                        or settings.VIEW_COUNT
                    )
                self.assertEqual(len(response.context['page_obj']),
                                 last_page_post)
                self.assertEqual(response.context['page_obj'].number, 2)
