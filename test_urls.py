from django.test import SimpleTestCase
from django.urls import resolve, reverse


class URLTests(SimpleTestCase):
    """Test all URLs are properly configured"""

    def test_upload_urls(self):
        """Test upload app URLs"""
        url = reverse("upload:home")
        self.assertEqual(resolve(url).app_name, "upload")
        self.assertEqual(resolve(url).url_name, "home")

        url = reverse("upload:upload_file")
        self.assertEqual(resolve(url).app_name, "upload")
        self.assertEqual(resolve(url).url_name, "upload_file")

    def test_browse_urls(self):
        """Test browse app URLs"""
        url = reverse("browse:browse_individuals")
        self.assertEqual(resolve(url).app_name, "browse")
        self.assertEqual(resolve(url).url_name, "browse_individuals")

        url = reverse("browse:individual_detail", args=["I1"])
        self.assertEqual(resolve(url).app_name, "browse")
        self.assertEqual(resolve(url).url_name, "individual_detail")

    def test_hud_urls(self):
        """Test HUD app URLs"""
        url = reverse("hud:display_tree")
        self.assertEqual(resolve(url).app_name, "hud")
        self.assertEqual(resolve(url).url_name, "display_tree")

        url = reverse("hud:hud_family_data")
        self.assertEqual(resolve(url).app_name, "hud")
        self.assertEqual(resolve(url).url_name, "hud_family_data")

    def test_charts_urls(self):
        """Test charts app URLs"""
        url = reverse("charts:adjust_output")
        self.assertEqual(resolve(url).app_name, "charts")
        self.assertEqual(resolve(url).url_name, "adjust_output")

        url = reverse("charts:generate_chart", args=[1, "I1"])
        self.assertEqual(resolve(url).app_name, "charts")
        self.assertEqual(resolve(url).url_name, "generate_chart")

    def test_users_urls(self):
        """Test users app URLs"""
        url = reverse("users:profile")
        self.assertEqual(resolve(url).app_name, "users")
        self.assertEqual(resolve(url).url_name, "profile")

        url = reverse("users:register")
        self.assertEqual(resolve(url).app_name, "users")
        self.assertEqual(resolve(url).url_name, "register")
