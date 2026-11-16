import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

from .models import (
    FAQ,
    AdmissionEnquiry,
    ContactMessage,
    GalleryImage,
    LearningStage,
    NewsCategory,
    NewsPost,
    SiteSettings,
    Teacher,
)

admin.site.site_header = _("Wisdom School — site management")
admin.site.site_title = _("Wisdom School")
admin.site.index_title = _("Site content and enquiries")


def thumb(image, size=60):
    if image:
        return format_html('<img src="{}" style="height:{}px;width:auto;border-radius:2px">', image.url, size)
    return "—"


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        (_("Contacts"), {"fields": ("phone", "phone_secondary", "email", "address", "working_hours", "map_url")}),
        (_("Social networks"), {"fields": ("instagram", "telegram", "facebook", "youtube")}),
        (_("Header"), {"fields": ("tagline",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LearningStage)
class LearningStageAdmin(TabbedTranslationAdmin):
    list_display = ("title", "tagline", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Teacher)
class TeacherAdmin(TabbedTranslationAdmin):
    list_display = ("preview", "name", "subject", "order", "is_active")
    list_display_links = ("preview", "name")
    list_editable = ("order", "is_active")
    search_fields = ("name", "subject")

    @admin.display(description=_("photo"))
    def preview(self, obj):
        return thumb(obj.photo)


@admin.register(NewsCategory)
class NewsCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(NewsPost)
class NewsPostAdmin(TabbedTranslationAdmin):
    list_display = ("preview", "title", "category", "published_at", "is_published", "is_featured")
    list_display_links = ("preview", "title")
    list_filter = ("is_published", "is_featured", "category")
    list_editable = ("is_published", "is_featured")
    search_fields = ("title", "excerpt", "body")
    date_hierarchy = "published_at"
    fields = ("title", "category", "excerpt", "body", "image", "published_at", "is_published", "is_featured", "slug")

    @admin.display(description=_("image"))
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(GalleryImage)
class GalleryImageAdmin(TabbedTranslationAdmin):
    list_display = ("preview", "caption", "order", "is_published")
    list_display_links = ("preview", "caption")
    list_editable = ("order", "is_published")

    @admin.display(description=_("image"))
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(FAQ)
class FAQAdmin(TabbedTranslationAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")


def export_csv(fields):
    @admin.action(description=_("Export selected to CSV (Excel)"))
    def action(modeladmin, request, queryset):
        meta = modeladmin.model._meta
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{meta.model_name}.csv"'
        response.write("﻿")  # BOM so Excel opens UTF-8 correctly
        writer = csv.writer(response, delimiter=";")
        writer.writerow([str(meta.get_field(f).verbose_name) for f in fields])
        for obj in queryset:
            row = []
            for f in fields:
                display = getattr(obj, f"get_{f}_display", None)
                value = display() if display else getattr(obj, f)
                if hasattr(value, "strftime"):
                    value = value.strftime("%d.%m.%Y %H:%M")
                row.append("" if value is None else str(value))
            writer.writerow(row)
        return response

    return action


@admin.action(description=_("Mark as done"))
def mark_done(modeladmin, request, queryset):
    queryset.update(status="done")


@admin.action(description=_("Mark as in progress"))
def mark_in_progress(modeladmin, request, queryset):
    queryset.update(status="in_progress")


@admin.register(AdmissionEnquiry)
class AdmissionEnquiryAdmin(admin.ModelAdmin):
    list_display = ("parent_name", "phone", "email", "stage", "next_step", "status", "created_at")
    list_filter = ("status", "stage", "next_step", "created_at")
    list_editable = ("status",)
    search_fields = ("parent_name", "email", "phone", "message")
    readonly_fields = ("parent_name", "email", "phone", "stage", "next_step", "message", "consent",
                       "language", "created_at")
    fields = readonly_fields + ("status", "staff_notes")
    actions = [mark_in_progress, mark_done,
               export_csv(["created_at", "parent_name", "phone", "email", "stage", "next_step", "message", "status"])]

    def has_add_permission(self, request):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "subject", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "subject", "message", "consent", "language", "created_at")
    fields = readonly_fields + ("status",)
    actions = [mark_in_progress, mark_done,
               export_csv(["created_at", "name", "email", "subject", "message", "status"])]

    def has_add_permission(self, request):
        return False
