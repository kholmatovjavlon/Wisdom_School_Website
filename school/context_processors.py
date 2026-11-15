from django.conf import settings
from django.urls import translate_url

from .models import SiteSettings


def site(request):
    path = request.get_full_path()
    languages = [
        {"code": code, "name": name, "url": translate_url(path, code)}
        for code, name in settings.LANGUAGES
    ]
    return {
        "site_settings": SiteSettings.load(),
        "language_links": languages,
        "site_url": request.build_absolute_uri("/").rstrip("/"),
    }
