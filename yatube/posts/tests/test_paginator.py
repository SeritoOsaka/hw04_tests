from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group

User = get_user_model()

INDEX = reverse('posts:index')
PROFILE = reverse('posts:profile', kwargs={'username': 'User'})


class PaginatorViewsTest(TestCase):
    NUM_POSTS_TO_CREATE = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.num_pages = Paginator(Post.objects.all(),
                                  settings.VIEW_COUNT).num_pages
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )

    def setUp(self):
        self.num_posts = Post.objects.count()
        self.authorized_client = Client()
        posts_to_create = [Post(author=self.user, group=self.group)
                           for _ in range(self.NUM_POSTS_TO_CREATE)]
        Post.objects.bulk_create(posts_to_create)
        self.num_pages = Paginator(Post.objects.all(),
                                   settings.VIEW_COUNT).num_pages

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(INDEX)
        self.assertEqual(len(response.context['page_obj']),
                         settings.VIEW_COUNT)

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.VIEW_COUNT)

        response = self.authorized_client.get(PROFILE)
        self.assertEqual(
            len(response.context['page_obj']), settings.VIEW_COUNT)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(INDEX + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
        self.assertEqual(
            response.context['page_obj'].number, 2)
        self.assertEqual(
            response.context['page_obj'].paginator.num_pages, self.num_pages)

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
