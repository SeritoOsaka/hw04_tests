from django.test import TestCase, Client

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

    def test_redirect_new_post(self):
        response = self.guest_client.get(self.urls["post_create"], follow=True)
        self.assertRedirects(response,
                             f'/auth/login/?next={self.urls["post_create"]}')

    def test_redirect_post_edit(self):
        response = self.guest_client.get(self.urls["post_edit"], follow=True)
        self.assertRedirects(response,
                             f'/auth/login/?next={self.urls["post_edit"]}')

    def test_post_edit_redirect_for_guest(self):
        url = f'/posts/{self.post.id}/edit/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={url}')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_exist(self):
        for name, url in self.urls.items():
            with self.subTest(name=name):
                if 'profile' in name:
                    client = self.authorized_client
                elif 'create' in name or 'edit' in name:
                    client = self.authorized_client
                    response = client.get(url)
                    self.assertEqual(response.status_code, 200)
                    continue
                else:
                    client = self.guest_client
                response = client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            (self.urls["index"], 'posts/index.html'),
            (self.urls["group_list"], 'posts/group_list.html'),
            (self.urls["profile"], 'posts/profile.html'),
            (self.urls["post_detail"], 'posts/post_detail.html'),
            (self.urls["post_edit"], 'posts/post_create.html'),
            (self.urls["post_create"], 'posts/post_create.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
