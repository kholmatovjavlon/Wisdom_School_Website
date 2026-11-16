from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Single row with the school's contact details, shown across the site."""

    tagline = models.CharField(_("tagline"), max_length=200, blank=True,
                               help_text=_("Leave empty to use the standard text."))
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    phone_secondary = models.CharField(_("second phone"), max_length=50, blank=True)
    email = models.EmailField(_("e-mail"), blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    working_hours = models.CharField(_("working hours"), max_length=255, blank=True)
    map_url = models.URLField(_("map link"), blank=True,
                              help_text=_("Link to the school on Google Maps or Yandex Maps."))
    instagram = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self):
        return str(_("Site settings"))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def social_links(self):
        links = [("Telegram", self.telegram), ("Instagram", self.instagram),
                 ("Facebook", self.facebook), ("YouTube", self.youtube)]
        return [{"name": name, "url": url} for name, url in links if url]

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class CardTone(models.TextChoices):
    LIGHT = "light", _("Light")
    LAVENDER = "lavender", _("Lavender")


class LearningStage(models.Model):
    title = models.CharField(_("title"), max_length=120)
    tagline = models.CharField(_("short tagline"), max_length=120, blank=True,
                               help_text=_("Shown in small capitals, e.g. “A joyful beginning”."))
    summary = models.TextField(_("summary for the home page"), blank=True)
    headline = models.CharField(_("headline"), max_length=200, blank=True)
    description = models.TextField(_("description"), blank=True)
    highlights = models.TextField(_("highlights"), blank=True,
                                  help_text=_("One item per line."))
    tone = models.CharField(_("card colour"), max_length=20, choices=CardTone.choices,
                            default=CardTone.LIGHT)
    order = models.PositiveIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("show on site"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("learning stage")
        verbose_name_plural = _("learning stages")

    def __str__(self):
        return self.title

    @property
    def highlight_list(self):
        return [line.strip() for line in (self.highlights or "").splitlines() if line.strip()]


class Teacher(models.Model):
    name = models.CharField(_("full name"), max_length=150)
    subject = models.CharField(_("subject / role"), max_length=150)
    bio = models.TextField(_("short description"), blank=True)
    photo = models.ImageField(_("photo"), upload_to="teachers/", blank=True)
    tone = models.CharField(_("card colour"), max_length=20, choices=CardTone.choices,
                            default=CardTone.LIGHT)
    order = models.PositiveIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("show on site"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")

    def __str__(self):
        return self.name


class NewsCategory(models.Model):
    name = models.CharField(_("name"), max_length=80)
    slug = models.SlugField(_("slug"), max_length=80, unique=True)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("news category")
        verbose_name_plural = _("news categories")

    def __str__(self):
        return self.name


class PublishedNewsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, published_at__lte=timezone.now())


class NewsPost(models.Model):
    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True, blank=True,
                            help_text=_("Part of the page address. Filled in automatically if left empty."))
    category = models.ForeignKey(NewsCategory, verbose_name=_("category"), on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name="posts")
    excerpt = models.TextField(_("short summary"), blank=True)
    body = models.TextField(_("text"), blank=True,
                            help_text=_("Separate paragraphs with an empty line."))
    image = models.ImageField(_("image"), upload_to="news/", blank=True)
    published_at = models.DateTimeField(_("publication date"), default=timezone.now)
    is_published = models.BooleanField(_("published"), default=True)
    is_featured = models.BooleanField(_("featured story"), default=False,
                                      help_text=_("Shown large at the top of the news page."))

    objects = models.Manager()
    published = PublishedNewsManager()

    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name = _("news post")
        verbose_name_plural = _("news")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title or "", allow_unicode=False)[:180] or "news"
            slug, n = base, 2
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news_detail", kwargs={"slug": self.slug})

    @property
    def paragraphs(self):
        return [p.strip() for p in (self.body or "").split("\n\n") if p.strip()]


class GalleryImage(models.Model):
    image = models.ImageField(_("image"), upload_to="gallery/")
    caption = models.CharField(_("caption"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("order"), default=0)
    is_published = models.BooleanField(_("show on site"), default=True)
    created_at = models.DateTimeField(_("added"), auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = _("gallery photo")
        verbose_name_plural = _("gallery")

    def __str__(self):
        return self.caption or self.image.name


class FAQ(models.Model):
    question = models.CharField(_("question"), max_length=255)
    answer = models.TextField(_("answer"))
    order = models.PositiveIntegerField(_("order"), default=0)
    is_active = models.BooleanField(_("show on site"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("admissions question")
        verbose_name_plural = _("admissions questions (FAQ)")

    def __str__(self):
        return self.question


class EnquiryStatus(models.TextChoices):
    NEW = "new", _("New")
    IN_PROGRESS = "in_progress", _("In progress")
    DONE = "done", _("Done")


class AdmissionEnquiry(models.Model):
    class NextStep(models.TextChoices):
        VISIT = "visit", _("Arrange a school visit")
        CALL = "call", _("Receive a phone call")
        INFO = "info", _("Receive more information")

    parent_name = models.CharField(_("parent / guardian name"), max_length=150)
    email = models.EmailField(_("e-mail"))
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    stage = models.ForeignKey(LearningStage, verbose_name=_("learning stage"), on_delete=models.SET_NULL,
                              null=True, blank=True)
    next_step = models.CharField(_("preferred next step"), max_length=20, choices=NextStep.choices,
                                 blank=True)
    message = models.TextField(_("message"), blank=True)
    consent = models.BooleanField(_("consent to be contacted"), default=False)
    language = models.CharField(_("site language"), max_length=10, blank=True)
    status = models.CharField(_("status"), max_length=20, choices=EnquiryStatus.choices,
                              default=EnquiryStatus.NEW)
    staff_notes = models.TextField(_("staff notes"), blank=True)
    created_at = models.DateTimeField(_("received"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("admissions enquiry")
        verbose_name_plural = _("admissions enquiries")

    def __str__(self):
        return f"{self.parent_name} — {self.created_at:%d.%m.%Y}"


class ContactMessage(models.Model):
    class Subject(models.TextChoices):
        GENERAL = "general", _("General question")
        ADMISSIONS = "admissions", _("Admissions")
        VISIT = "visit", _("School visit")
        OTHER = "other", _("Other")

    name = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("e-mail"))
    subject = models.CharField(_("subject"), max_length=20, choices=Subject.choices)
    message = models.TextField(_("message"))
    consent = models.BooleanField(_("consent to be contacted"), default=False)
    language = models.CharField(_("site language"), max_length=10, blank=True)
    status = models.CharField(_("status"), max_length=20, choices=EnquiryStatus.choices,
                              default=EnquiryStatus.NEW)
    created_at = models.DateTimeField(_("received"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("contact message")
        verbose_name_plural = _("contact messages")

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()}"
