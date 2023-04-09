from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User

NUM_OF_POSTS_1 = 13
NUM_OF_POSTS_2 = 2


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_client = Client()
        # Авторизованный клиент
        cls.user = User.objects.create(username='User')
        cls.second_user = User.objects.create(username='Second_User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client.force_login(cls.second_user)
        # Создал две группы в БД
        cls.group = Group.objects.create(
            title='Первая группа',
            slug='test-slug',
            description='Описание группы'
        )
        cls.second_group = Group.objects.create(
            title='Вторая группа',
            slug='test-slug-new',
            description='Отличная группа от тестовой'
        )
        # Создадим 13 постов в первой группе БД
        for post in range(NUM_OF_POSTS_1):
            cls.post = Post.objects.create(
                text='Записи первой группы',
                author=cls.user,
                group=cls.group
            )

        # Создадим 2 поста во второй группе в БД
        for post in range(NUM_OF_POSTS_2):
            cls.post = Post.objects.create(
                text='Записи второй группы',
                author=cls.second_user,
                group=cls.second_group
            )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'User'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 13}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': 14}): (
                'posts/post_create.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], self.group)
        self.assertIn('page_obj', response.context)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'User'})
        )
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn('post', response.context)
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': (self.post.pk)})
        )
        self.assertIn('post', response.context)
        self.assertIn('posts_count', response.context)

    def test_post_create_page_show_correct_context(self):
        response = self.client.get(reverse('posts:post_create'), follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)))

        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertEqual(form.instance, self.post)

    def test_paginator_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.VIEW_COUNT)

    def test_paginator_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         settings.SECOND_PAGE_COUNT)

    def test_paginator_group_list_contains_two_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-new'})
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TWO_RECORDS_COUNT)

    def test_paginator_profile_contains_two_records(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'Second_User'})
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TWO_RECORDS_COUNT)
