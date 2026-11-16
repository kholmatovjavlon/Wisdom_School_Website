from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(_("about/"), views.about, name="about"),
    path(_("academics/"), views.academics, name="academics"),
    path(_("admissions/"), views.admissions, name="admissions"),
    path(_("faculty/"), views.faculty, name="faculty"),
    path(_("news/"), views.news_list, name="news_list"),
    path(_("news/<slug:slug>/"), views.news_detail, name="news_detail"),
    path(_("gallery/"), views.gallery, name="gallery"),
    path(_("contact/"), views.contact, name="contact"),
    path(_("privacy/"), views.privacy, name="privacy"),
]
