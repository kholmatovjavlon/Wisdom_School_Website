import shutil
import tempfile

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from school.models import AdmissionEnquiry, ContactMessage, LearningStage, NewsPost


TEST_MEDIA = tempfile.mkdtemp(prefix="wisdom-test-media-")


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class PagesTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=open("/dev/null", "w"))

    def test_all_pages_in_all_languages(self):
        names = ["home", "about", "academics", "admissions", "faculty", "news_list", "gallery", "contact", "privacy"]
        for lang in ("uz", "ru", "en"):
            with translation.override(lang):
                for name in names:
                    url = reverse(name)
                    with self.subTest(url=url):
                        self.assertEqual(self.client.get(url).status_code, 200)

    def test_translated_content(self):
        with translation.override("ru"):
            response = self.client.get(reverse("home"))
        self.assertContains(response, "Любознательные умы.")
        self.assertContains(response, "Начальная школа")

    def test_news_detail_and_filter(self):
        post = NewsPost.objects.first()
        with translation.override("en"):
            self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 200)
            response = self.client.get(reverse("news_list") + "?category=community")
        self.assertContains(response, "A place to belong.")

    def test_root_redirects_to_language(self):
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_sitemap_and_robots(self):
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
        self.assertContains(self.client.get("/robots.txt"), "Sitemap:")


@override_settings(ADMISSIONS_NOTIFY_EMAILS=["admissions@example.com"])
class FormsTest(TestCase):
    def setUp(self):
        self.stage = LearningStage.objects.create(title="Primary years")

    def test_admission_enquiry_saved_and_notified(self):
        with translation.override("ru"):
            url = reverse("admissions")
        response = self.client.post(url, {
            "parent_name": "Dilnoza", "email": "d@example.com", "phone": "+998 90 123 45 67",
            "stage": self.stage.pk, "next_step": "visit", "message": "Hello", "consent": "on",
        })
        self.assertEqual(response.status_code, 302)
        enquiry = AdmissionEnquiry.objects.get()
        self.assertEqual(enquiry.language, "ru")
        self.assertEqual(len(mail.outbox), 1)

    def test_enquiry_requires_consent_and_fields(self):
        response = self.client.post(reverse("admissions"), {"parent_name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AdmissionEnquiry.objects.exists())

    def test_honeypot_blocks_bots(self):
        self.client.post(reverse("contact"), {
            "name": "Bot", "email": "b@example.com", "subject": "general", "message": "spam",
            "consent": "on", "website": "http://spam",
        })
        self.assertFalse(ContactMessage.objects.exists())

    def test_contact_message_saved(self):
        response = self.client.post(reverse("contact"), {
            "name": "Aziz", "email": "a@example.com", "subject": "general", "message": "Question", "consent": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
