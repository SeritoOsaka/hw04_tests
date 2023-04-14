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

    def test_redirect_if_not_logged_in(self):
        urls = [self.urls["post_create"], self.urls["post_edit"]]
        for url in urls:
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_post_edit_redirect_for_guest(self):
        url = f'/posts/{self.post.id}/edit/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_exist(self):
        urls = {
            "index": reverse("posts:index"),
            "group_list": reverse("posts:group_list",
                                  kwargs={"slug": self.group.slug}),
            "profile": reverse("posts:profile",
                               kwargs={"username": self.user.username}),
            "post_detail": reverse("posts:post_detail",
                                   kwargs={"post_id": self.post.id}),
            "post_edit": reverse("posts:post_edit",
                                 kwargs={"post_id": self.post.id}),
            "post_create": reverse("posts:post_create"),
        }
        for name, url in urls.items():
            with self.subTest(name=name):
                client = (self.authorized_client if ('profile' in name
                                                     or 'create' in name
                                                     or 'edit' in name)
                          else self.guest_client)
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

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
