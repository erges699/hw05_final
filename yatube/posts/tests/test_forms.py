import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.group_id = self.group.id
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.uploaded2 = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.upload_to = 'posts/'
        self.image = 'small.gif'

    def test_form_create_post_redirect(self):
        """create_post при отправке валидной формы со страницы
        создания поста.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста',
            'group': self.group_id,
            'image': self.uploaded,
        }
        response = self.author_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.post.author,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.order_by('-id')[0].text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.order_by('-id')[0].group.pk,
            form_data['group']
        )
        self.assertEqual(
            Post.objects.order_by('-id')[0].image.name,
            self.upload_to + form_data['image'].name
        )

    def test_post_edit_show_correct_context(self):
        """post_edit при отправке валидной формы со страницы
        редактирования текста поста.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редакция текста поста',
            'group': self.group_id,
            'image': self.uploaded2,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                group=form_data['group'],
                text=form_data['text'],
                image=self.upload_to + form_data['image'].name,
            ).exists()
        )


class PostCommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostCommentTests.user)

    def test_post_comment_appear(self):
        """после успешной отправки комментарий появляется на странице поста
        """
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий поста',
            'author': self.author_client,
        }
        response = self.author_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(
            Comment.objects.order_by('-id')[0].text,
            form_data['text']
        )
        self.assertEqual(
            Comment.objects.order_by('-id')[0].post.id,
            self.post.id
        )
