from posts.models import Group, Post, User
from django.test import Client, TestCase
from django.urls import reverse


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
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

    def setUp(cls):
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        initial_posts_count = Post.objects.count()
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
        final_posts = (Post.objects
                       .all()
                       .order_by('-pub_date')
                       [initial_posts_count:])
        self.assertEqual(len(final_posts), 1)
        post = final_posts[0]
        self.assertEqual(post.group, PostCreateFormTests.group)
        self.assertEqual(post.author, PostCreateFormTests.user)
        self.assertEqual(post.text, form_data['text'])

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
                text=form_data['text']
            ).exists()
        )

    def test_authorized_edit_post(self):
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
        edit_post = Post.objects.filter(
            pk=self.post.pk,  # выбираем пост по его id
            text='Edited post',
            author=self.user,
            group=self.group.pk
        ).first()
        self.assertTrue(edit_post is not None)
        self.assertEqual(edit_post.group, self.group)
        self.assertEqual(edit_post.author, self.user)
        self.assertEqual(edit_post.text, form_data['text'])
