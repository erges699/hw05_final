from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
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
        self.user = User.objects.create_user(username='NoNameUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(URLTests.user)
        self.authorized_user_profile = f'/profile/{self.user.username}/'
        self.author_user_profile = f'/profile/{URLTests.user.username}/'
        self.group_slug = f'/group/{URLTests.post.group.slug}/'
        self.post_id = f'/posts/{URLTests.post.id}/'
        self.post_edit_id = f'/posts/{URLTests.post.id}/edit/'

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_access_names = {
            '/': 'posts/index.html',
            self.authorized_user_profile: 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            self.group_slug: 'posts/group_list.html',
            self.post_id: 'posts/post_detail.html',
            self.post_edit_id: 'posts/create_post.html',
        }
        for address, template in template_access_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_have_url_access(self):
        """Проверяем, что автору доступны URL."""
        author_url_access_names = {
            '/': HTTPStatus.OK,
            self.author_user_profile: HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            self.group_slug: HTTPStatus.OK,
            self.post_id: HTTPStatus.OK,
            self.post_edit_id: HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status_codes in author_url_access_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, status_codes)

    def test_authorized_have_url_access(self):
        """Проверяем, что авторизованному доступны URL."""
        authorized_url_access_names = {
            '/': HTTPStatus.OK,
            self.authorized_user_profile: HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            self.group_slug: HTTPStatus.OK,
            self.post_id: HTTPStatus.OK,
            self.post_edit_id: HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status_codes in authorized_url_access_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_codes)

    def test_guest_have_url_access(self):
        """Проверяем, что гостю доступны URL."""
        guest_url_access_names = {
            '/': HTTPStatus.OK,
            self.authorized_user_profile: HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            self.group_slug: HTTPStatus.OK,
            self.post_id: HTTPStatus.OK,
            self.post_edit_id: HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status_codes in guest_url_access_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status_codes)
