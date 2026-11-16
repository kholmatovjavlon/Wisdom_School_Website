from django.conf import settings
from django.urls import translate_url
from django.utils.translation import gettext_lazy as _

from .models import SiteSettings


MENU = [
    ("about", _("About")),
    ("learning", _("Learning")),
    ("directions", _("Directions")),
    ("teachers", _("Teachers")),
    ("gallery", _("Gallery")),
    ("faq", _("FAQ")),
    ("contact", _("Contacts")),
]


def site(request):
    path = request.get_full_path()
    languages = [
        {"code": code, "name": name, "url": translate_url(path, code)}
        for code, name in settings.LANGUAGES
    ]
    return {
        "menu_items": MENU,
        "site_settings": SiteSettings.load(),
        "language_links": languages,
        "site_url": request.build_absolute_uri("/").rstrip("/"),
    }
