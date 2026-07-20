"""
Test file to verify CSRF protection on upload endpoints
"""
import unittest
import json
from django.test import Client
from django.urls import reverse
from django.conf import settings


class CSRFProtectionTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.login(username='testuser', password='testpass123')

    def test_upload_endpoint_csrf_protection(self):
        """Test that upload endpoints are protected with CSRF"""
        # Test that GET requests work
        response = self.client.get(reverse('upload:upload_and_generate'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request without CSRF token should be rejected
        response = self.client.post(
            reverse('upload:upload_and_generate'),
            {'gedcom_file': 'test'},
            HTTP_CONTENT_TYPE: 'multipart/form-data'
        )
        self.assertEqual(response.status_code, 403)  # Should be rejected without CSRF token
        
        # Test POST request with CSRF token should work
        response = self.client.post(
            reverse('upload:upload_and_generate'),
            {'gedcom_file': 'test'},
            HTTP_CONTENT_TYPE: 'multipart/form-data',
            'HTTP_X_CSRFTOKEN': self.client.get('/admin/jsi/')  # Get CSRF token
        )
        self.assertEqual(response.status_code, 302)  # Should be rejected initially (redirect)
        
        # Test delete endpoint without CSRF token should be rejected
        response = self.client.post(
            reverse('users:delete_gedcom_file'),
            {'file_id': '1'},
        )
        self.assertEqual(response.status_code, 403)  # Should be rejected without CSRF token
        response = self.client.post(
            reverse('users:delete_gedcom_file'),
            {'file_id': '1'},
            HTTP_X_CSRFTOKEN': self.client.get('/admin/jsi/')  # Get CSRF token
        )
        self.assertEqual(response.status_code, 200)  # Should succeed with CSRF token

if __name__ == '__main__':
    unittest.main()