from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test username')
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description',
        )

        cls.post = Post.objects.create(
            text='Привет!',
            author=cls.user,
            group=cls.group,
        )
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            )
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def posts_check_all_fields(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_posts_context(self):
        response_index = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_index.status_code, 200)
        last_post_index = response_index.context['page_obj'][0]
        self.posts_check_all_fields(last_post_index)
        self.assertEqual(last_post_index, self.post)

        response_group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response_group_list.status_code, 200)
        test_group = response_group_list.context['group']
        self.assertEqual(test_group, self.group)
        last_post_group_list = response_group_list.context['page_obj'][0]
        self.posts_check_all_fields(last_post_group_list)
        self.assertEqual(str(last_post_group_list), str(self.post))

    def test_posts_context_post_create_template(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_posts_context_post_edit_template(self):
        response = self.client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertEqual(form['text'].value(), self.post.text)

    def test_posts_context_profile_template(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        context_author = response.context['author']
        self.assertEqual(context_author, self.post.author)

    def test_posts_context_post_detail_template(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        context_post = response.context['post']
        self.assertEqual(context_post, self.post)


class PostsPaginatorViewsTests(TestCase):
    # Это было сделано для того, чтобы легко изменять константы
    POST_COUNT = 13
    POSTS_PER_PAGE = 5

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='Test User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        Post.objects.bulk_create(
            Post(
                text=f'Test post text {count}',
                author=cls.user,
            ) for count in range(cls.POST_COUNT)
        )

    def test_paginator_pages(self):
        paginator = Paginator(Post.objects.all(), self.POSTS_PER_PAGE)
        last_page_posts = self.POST_COUNT % self.POSTS_PER_PAGE or \
            self.POSTS_PER_PAGE
        last_page_num = (self.POST_COUNT + self.POSTS_PER_PAGE - 1) // \
            self.POSTS_PER_PAGE

        page_num = 1
        while True:
            url = reverse('posts:index') + f'?page={page_num}'
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, 200)
            posts_per_page = (self.POSTS_PER_PAGE
                              if page_num != last_page_num
                              else last_page_posts)
            self.assertEqual(
                len(response.context['page_obj'].object_list),
                posts_per_page,
            )
            if not paginator.page(page_num).has_next():
                break
            page_num += 1
