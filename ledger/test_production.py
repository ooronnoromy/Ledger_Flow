import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Vehicle


class ProductionTests(TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory)
        self.override = override_settings(MEDIA_ROOT=self.directory)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.owner = get_user_model().objects.create_user('photo-owner')
        self.other = get_user_model().objects.create_user('photo-other')
        self.vehicle = Vehicle.objects.create(
            owner=self.owner, name='Car', plate='Test',
            photo=SimpleUploadedFile('photo.png', b'private-image', content_type='image/png'),
        )
        self.url = self.vehicle.photo.url

    def test_healthcheck(self):
        self.assertEqual(self.client.get('/healthz/').content, b'ok')

    def test_anonymous_media_requires_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_owner_can_read_media_in_production(self):
        self.client.force_login(self.owner)
        with override_settings(DEBUG=False):
            response = self.client.get(self.url, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'private-image')
        self.assertIn('no-store', response['Cache-Control'])

    def test_other_account_cannot_read_media(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_path_traversal_cannot_read_files(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get('/media/../config/settings.py').status_code, 404)
