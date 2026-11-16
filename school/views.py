from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from .forms import AdmissionEnquiryForm
from .models import FAQ, GalleryImage, LearningStage, NewsCategory, NewsPost, Teacher
from .notifications import notify_staff


def stages():
    return LearningStage.objects.filter(is_active=True)


def _landing(request, form=None, status=200):
    return render(request, "school/home.html", {
        "nav": "home",
        "stages": stages()[:3],
        "teachers": Teacher.objects.filter(is_active=True)[:6],
        "gallery": GalleryImage.objects.filter(is_published=True)[:3],
        "latest_news": NewsPost.published.select_related("category")[:3],
        "faqs": FAQ.objects.filter(is_active=True)[:6],
        "form": form or AdmissionEnquiryForm(),
    }, status=status)


def home(request):
    if request.method == "POST":
        return admissions(request)
    return _landing(request)


def _to_section(anchor):
    def view(request):
        return redirect(reverse("home") + "#" + anchor, permanent=True)
    return view


# The site is a single landing page now; old section pages point to their blocks.
about = _to_section("about")
academics = _to_section("learning")
faculty = _to_section("teachers")
gallery = _to_section("gallery")
contact = _to_section("contact")


def admissions(request):
    if request.method != "POST":
        return redirect(reverse("home") + "#enquiry", permanent=True)
    form = AdmissionEnquiryForm(request.POST)
    if not form.is_valid():
        return _landing(request, form)
    enquiry = form.save(commit=False)
    enquiry.language = get_language() or ""
    enquiry.save()
    notify_staff(
        f"New admissions enquiry: {enquiry.parent_name}",
        [
            f"Name: {enquiry.parent_name}",
            f"Phone: {enquiry.phone}",
            f"Stage: {enquiry.stage or '-'}",
            f"Contact by: {enquiry.get_next_step_display() or '-'}",
        ],
    )
    messages.success(request, _("Thank you! Your enquiry has been received. "
                                "We will call you back soon."))
    return redirect(reverse("home") + "#enquiry")


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
