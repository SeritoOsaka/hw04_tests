from posts.models import Group, Post, User
from django.test import Client, TestCase
from django.urls import reverse


class PostCreateFormTests(TestCase):
    """использовал метод setUp() вместо setUpClass(),
    так как setUpClass() вызывается только один раз для всего класса тестов,
    а не для каждого теста."""
    @classmethod
    def setUp(cls):
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Group description'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostCreateFormTests.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        posts = Post.objects.filter(
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
            text='Test text'
        )
        self.assertEqual(posts.count(), 2)

        for post in posts:
            self.assertEqual(post.text, 'Test text')
            self.assertEqual(post.author, PostCreateFormTests.user)
            self.assertEqual(post.group, PostCreateFormTests.group)

    def test_guest_create_post(self):
        form_data = {
            'text': 'Non authorized test post',
            'group': self.group.pk,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(
            Post.objects.filter(
                text='Non authorized test post'
            ).exists()
        )

    def test_authorized_edit_post(self):
        post_text = Post.objects.filter(pk=self.post.pk)
        form_data = {
            'text': 'Edited post',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertNotEqual(
            post_text,
            Post.objects.filter(pk=self.post.pk)
        )
        self.assertTrue(
            Post.objects.filter(
                text='Edited post',
                author=self.user,
                group=self.group.pk
            ).exists()
        )
