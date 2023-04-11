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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.urls = {
            "index": '/',
            "group_list": '/group/test_slug/',
            "profile": '/profile/User/',
            "post_detail": f'/posts/{PostsURLTests.post.id}/',
            "post_edit": f'/posts/{PostsURLTests.post.id}/edit/',
            "post_create": '/create/',
        }

    def test_home_url_exist(self):
        response = self.guest_client.get(self.urls["index"])
        self.assertEqual(response.status_code, 200)

    def test_group_list_url_exist(self):
        response = self.guest_client.get(self.urls["group_list"])
        self.assertEqual(response.status_code, 200)

    def test_posts_url_exist(self):
        response = self.guest_client.get(self.urls["post_detail"])
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exist(self):
        response = self.guest_client.get(self.urls["profile"])
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page_url_exist(self):
        response = self.authorized_client.get(
            self.urls["post_edit"]
        )
        self.assertEqual(response.status_code, 200)

    def test_create_post_page_url_exist(self):
        response = self.authorized_client.get(self.urls["post_create"])
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            self.urls["index"]: 'posts/index.html',
            self.urls["group_list"]: 'posts/group_list.html',
            self.urls["profile"]: 'posts/profile.html',
            self.urls["post_detail"]: 'posts/post_detail.html',
            self.urls["post_edit"]: 'posts/post_create.html',
            self.urls["post_create"]: 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
