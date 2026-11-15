from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import NewsPost


class StaticSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["home", "about", "academics", "admissions", "faculty", "news_list", "gallery", "contact"]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return NewsPost.published.all()

    def lastmod(self, obj):
        return obj.published_at
