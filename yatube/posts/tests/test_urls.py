from django.test import TestCase, Client
from django.urls import reverse
from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=PostsURLTests.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.urls = {
            "index": '/',
            "group_list": f'/group/{cls.group.slug}/',
            "profile": '/profile/User/',
            "post_detail": f'/posts/{PostsURLTests.post.id}/',
            "post_edit": f'/posts/{PostsURLTests.post.id}/edit/',
            "post_create": '/create/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_names(self):
        urls_names = {
            "index": "/",
            "group_list": reverse("posts:group_list",
                                  args=[PostsURLTests.group.slug]),
            "profile": reverse("posts:profile",
                               args=[PostsURLTests.user.username]),
            "post_detail": reverse("posts:post_detail",
                                   args=[PostsURLTests.post.id]),
            "post_edit": reverse("posts:post_edit",
                                 args=[PostsURLTests.post.id]),
            "post_create": '/create/',
        }
        for name, url in urls_names.items():
            with self.subTest(name=name):
                self.assertEqual(url, PostsURLTests.urls[name])

    def test_redirect_if_not_logged_in(self):
        url = f'/posts/{self.post.id}/edit/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_exist(self):
        urls = [
            (reverse("posts:index"), 200, self.guest_client),
            (reverse("posts:group_list", kwargs={"slug": self.group.slug}),
             200, self.guest_client),
            (reverse("posts:profile", kwargs={"username": self.user.username}),
             200, self.guest_client),
            (reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
             200, self.guest_client),
            (reverse("posts:post_create"), 200, self.authorized_client),
            (reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
             200, self.authorized_client),
        ]
        for url, expected_status_code, client in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status_code)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            (reverse("posts:index"), 'posts/index.html'),
            (reverse("posts:group_list", kwargs={"slug": self.group.slug}),
             'posts/group_list.html'),
            (reverse("posts:profile", kwargs={"username": self.user.username}),
             'posts/profile.html'),
            (reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
             'posts/post_detail.html'),
            (reverse("posts:post_create"), 'posts/post_create.html'),
            (reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
             'posts/post_create.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_redirect_non_author_edit_post(self):
        non_author = User.objects.create_user(username='Non_author')
        non_author_client = Client()
        non_author_client.force_login(non_author)

        response = non_author_client.get(
            reverse('posts:post_edit', args=[self.post.id]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_actual_urls(self):
        urls_names = {
            "index": "/",
            "group_list": reverse("posts:group_list",
                                  args=[PostsURLTests.group.slug]),
            "profile": reverse("posts:profile",
                               args=[PostsURLTests.user.username]),
            "post_detail": reverse("posts:post_detail",
                                   args=[PostsURLTests.post.id]),
            "post_edit": reverse("posts:post_edit",
                                 args=[PostsURLTests.post.id]),
            "post_create": '/create/',
        }
        for name, url in urls_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)
