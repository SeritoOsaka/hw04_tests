from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test User')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test group description',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_posts_forms_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test form post',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        created_post = Post.objects.get(text='Test form post', group=self.group.id)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.group, self.group)



    def test_posts_forms_edit_post(self):
        form_data = {
            'text': 'New post text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id},
        ), data=form_data)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={'username': self.user.username, 'post_id': self.post.id}))
        edited_post = Post.objects.get(id=self.post.id)
        self.assertEqual(edited_post.text, 'New post text')
        self.assertEqual(edited_post.group, self.group)
        self.assertEqual(edited_post.author, self.user)

