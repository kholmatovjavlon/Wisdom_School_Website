from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from .forms import AdmissionEnquiryForm, ContactForm
from .models import FAQ, GalleryImage, LearningStage, NewsCategory, NewsPost, Teacher
from .notifications import notify_staff


def stages():
    return LearningStage.objects.filter(is_active=True)


def home(request):
    return render(request, "school/home.html", {
        "nav": "home",
        "stages": stages()[:3],
        "latest_news": NewsPost.published.select_related("category")[:3],
    })


def about(request):
    return render(request, "school/about.html", {"nav": "about"})


def academics(request):
    return render(request, "school/academics.html", {"nav": "academics", "stages": stages()})


def admissions(request):
    if request.method == "POST":
        form = AdmissionEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.language = get_language() or ""
            enquiry.save()
            notify_staff(
                f"New admissions enquiry: {enquiry.parent_name}",
                [
                    f"Name: {enquiry.parent_name}",
                    f"Phone: {enquiry.phone}",
                    f"E-mail: {enquiry.email}",
                    f"Stage: {enquiry.stage or '-'}",
                    f"Next step: {enquiry.get_next_step_display() or '-'}",
                    "",
                    enquiry.message,
                ],
            )
            messages.success(request, _("Thank you! Your enquiry has been received. "
                                        "Our admissions team will contact you soon."))
            return redirect(reverse("admissions") + "#enquiry")
    else:
        form = AdmissionEnquiryForm()
    return render(request, "school/admissions.html", {
        "nav": "admissions",
        "form": form,
        "faqs": FAQ.objects.filter(is_active=True),
    })


def faculty(request):
    return render(request, "school/faculty.html", {
        "nav": "faculty",
        "teachers": Teacher.objects.filter(is_active=True),
    })


def news_list(request):
    posts = NewsPost.published.select_related("category")
    categories = NewsCategory.objects.filter(posts__isnull=False).distinct()
    active = request.GET.get("category", "")
    featured = posts.filter(is_featured=True).first() or posts.first()
    listing = posts
    if active:
        listing = listing.filter(category__slug=active)
    elif featured:
        listing = listing.exclude(pk=featured.pk)
    page = Paginator(listing, 9).get_page(request.GET.get("page"))
    return render(request, "school/news_list.html", {
        "nav": "news",
        "featured": featured if not active else None,
        "page": page,
        "categories": categories,
        "active_category": active,
    })


def news_detail(request, slug):
    post = get_object_or_404(NewsPost.published.select_related("category"), slug=slug)
    more = NewsPost.published.exclude(pk=post.pk).select_related("category")[:3]
    return render(request, "school/news_detail.html", {"nav": "news", "post": post, "more": more})


def gallery(request):
    return render(request, "school/gallery.html", {
        "nav": "gallery",
        "images": GalleryImage.objects.filter(is_published=True),
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.language = get_language() or ""
            msg.save()
            notify_staff(
                f"New message from the website: {msg.name}",
                [f"Name: {msg.name}", f"E-mail: {msg.email}", f"Subject: {msg.get_subject_display()}", "",
                 msg.message],
            )
            messages.success(request, _("Thank you for your message. We will reply as soon as possible."))
            return redirect(reverse("contact") + "#message")
    else:
        form = ContactForm()
    return render(request, "school/contact.html", {"nav": "contact", "form": form})


def privacy(request):
    return render(request, "school/privacy.html", {"nav": ""})


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
