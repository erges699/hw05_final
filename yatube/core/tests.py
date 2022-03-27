from django.test import TestCase

from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        self.template = 'core/404 page_not_found.html'
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, self.template)
