from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
# from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from django import forms

from ..models import Group, Post, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.user)
        self.post_text = 'Тестовый пост'

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages_names = {
            reverse('posts:posts_main'): 'posts/index.html',
            reverse(
                'posts:create_post'
            ): 'posts/create_post.html',
            reverse(
                'posts:posts_group_list',
                args=(self.post.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(self.post.author,)
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=(self.post.id,)
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=(self.post.id,)
            ): 'posts/create_post.html',
        }
        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', args=(self.post.id,))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(
            response.context.get('post_obj').text, self.post_text
        )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:posts_main'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post_text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.author_client.get(
            reverse('posts:posts_group_list', args=(self.post.group.slug,)))
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post_text)

    def test_post_profile_pages_show_correct_context(self):
        """Шаблон post_profile сформирован с правильным контекстом."""
        response = (self.author_client.get(
            reverse('posts:profile', args=(self.post.author,))))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post_text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.text_str = 'Тестовый пост' + str(i)
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=cls.text_str,
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.user)

    def test_first_page_index_contains_ten_records(self):
        """Первая страница index сформирована из
        settings.POSTS_ON_PAGE постов.
        """
        response = self.author_client.get(reverse('posts:posts_main'))
        self.assertEqual(len(
            response.context['page_obj']),
            settings.POSTS_ON_PAGE
        )

    def test_second_page_index_contains_three_records(self):
        """Вторая страница index сформирована из 3 постов."""
        posts_count = Post.objects.count() - settings.POSTS_ON_PAGE
        response = self.client.get(reverse('posts:posts_main') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), posts_count)

    def test_first_page_group_list_contains_ten_records(self):
        """Первая страница group_list сформирована из 10 постов."""
        response = (self.author_client.get(
            reverse('posts:posts_group_list', args=(self.post.group.slug,)))
        )
        self.assertEqual(len(
            response.context['page_obj']),
            settings.POSTS_ON_PAGE
        )

    def test_second_page_group_list_contains_three_records(self):
        """Вторая страница group_list сформирована из 3 постов."""
        posts_count = Post.objects.count() - settings.POSTS_ON_PAGE
        response = self.author_client.get(reverse(
            'posts:posts_group_list',
            args=(self.post.group.slug,)) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), posts_count)

    def test_first_page_profile_contains_ten_records(self):
        """Первая страница profile сформирована из 10 постов."""
        response = (self.author_client.get(
            reverse('posts:profile', args=(self.post.author,))))
        self.assertEqual(len(
            response.context['page_obj']),
            settings.POSTS_ON_PAGE
        )

    def test_second_page_profile_contains_three_records(self):
        """Вторая страница profile сформирована из 3 постов."""
        posts_count = Post.objects.count() - settings.POSTS_ON_PAGE
        response = self.author_client.get(reverse(
            'posts:profile',
            args=(self.post.author,)) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), posts_count)


class PostGroupTests(TestCase):
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

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostGroupTests.user)
        self.group_title = 'test-group'

    def test_post_index_correct_pages(self):
        """index Группа указана при создании поста."""
        response = self.author_client.get(reverse('posts:posts_main'))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, self.group_title)

    def test_post_group_list_correct_pages(self):
        """group_list Группа указана при создании поста."""
        response = (self.author_client.get(
            reverse('posts:posts_group_list', args=(self.post.group.slug,)))
        )
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, self.group_title)

    def test_post_profile_correct_pages(self):
        """profile Группа указана при создании поста."""
        response = (self.author_client.get(
            reverse('posts:profile', args=(self.post.author,))))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        self.assertEqual(post_group_0, self.group_title)


class SORLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestPassov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded
        )

    def setUp(self):
        self.user = User.objects.create_user(username='TestPassoff')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_show_index_post_with_image(self):
        """При выводе поста с картинкой изображение передается в context
        поста на главной странице.
        """
        response = self.authorized_client.get(reverse('posts:posts_main'))
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_show_posts_group_list_post_with_image(self):
        """При выводе поста с картинкой изображение передается в context
        поста на страницах группы.
        """
        response = self.authorized_client.get(reverse('posts:posts_group_list',
                                              args=(self.post.group.slug,)))
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_show_profile_post_with_image(self):
        """При выводе поста с картинкой изображение передается в context
        поста на страницах профиля.
        """
        response = self.authorized_client.get(reverse('posts:profile',
                                              args=(self.post.author,)))
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_show_post_detail_post_with_image(self):
        """При выводе поста с картинкой изображение передается в context
        поста на странице поста.
        """
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              args=(self.post.id,)))
        self.assertEqual(response.context['post_obj'].image,
                         self.post.image)

    def test_cahe_index_page_post(self):
        """при удалении записи из базы, она остаётся в response.content
        главной страницы.
        """
        current_post = Post.objects.get(pk=self.post.pk)
        response = self.authorized_client.get(
            reverse('posts:posts_main')
        )
        self.assertEqual(response.context['page_obj'][0], current_post)
        # current_post.delete()
        # current_cache = cache.get('index_page')
        # self.assertContains(response.status_code, current_cache)


class FollowUnfollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestPassov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.text_str = 'Тестовый фолловерский пост' + str(i)
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=cls.text_str,
            )

    def setUp(self):
        self.user1 = User.objects.create_user(username='TestPassoff')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.user2 = User.objects.create_user(username='TtestPpassoff')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.author_client = Client()
        self.author_client.force_login(FollowUnfollowTest.user)

    def author_cant_follow_self(self):
        """автор не может подписываться на себя.
        """
        self.author_client.get(
            reverse('profile_follow', args=(self.post.author,))
        )
        following = Follow.objects.filter(user=self.user)
        self.assertTrue(following.count() == 0)

    def authorized_can_follow_and_unfollow(self):
        """авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок.
        """
        following_count = Follow.objects.filter(user=self.user1).count()
        self.authorized_client.get(
            reverse('profile_follow', args=(self.post.author,))
        )
        self.assertEqual(
            Follow.objects.filter(user=self.user1).count(), following_count + 1
        )
        self.assertEqual(
            Follow.objects.order_by('-id')[0].user, self.user1
        )
        self.assertEqual(
            Follow.objects.order_by('-id')[0].author, FollowUnfollowTest.user
        )
        self.authorized_client.get(
            reverse('profile_unfollow', args=(self.post.author,))
        )
        self.assertEqual(
            Follow.objects.filter(user=self.user1).count(), following_count
        )

    def authorized_can_follow_and_unfollow(self):
        """новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан.
        """
        user2_following_count = Follow.objects.filter(user=self.user2).count()
        self.authorized_client2.get(
            reverse('profile_follow', args=(self.post.author,))
        )
        self.assertEqual(
            Follow.objects.filter(user=self.user2).count(),
            user2_following_count + 1
        )
        self.assertEqual(
            Follow.objects.order_by('-id')[0].user, self.user2
        )
        self.assertEqual(
            Follow.objects.order_by('-id')[0].author, FollowUnfollowTest.user
        )
        user2_response = self.authorized_client2.get(
            reverse('posts:follow_index')
        )
        user1_response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        user2_post_object = user2_response['page_obj'][0]
        user1_post_object = user1_response['page_obj'][0]
        self.assertEqual(
            user2_post_object.text, self.post.text
        )
        self.assertNotEqual(
            user1_post_object.text, self.post.text
        )
