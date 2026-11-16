from modeltranslation.translator import TranslationOptions, register

from .models import FAQ, GalleryImage, LearningStage, NewsCategory, NewsPost, SiteSettings, Teacher


@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = ("tagline", "address", "working_hours")


@register(LearningStage)
class LearningStageTR(TranslationOptions):
    fields = ("title", "tagline", "summary", "headline", "description", "highlights")


@register(Teacher)
class TeacherTR(TranslationOptions):
    fields = ("name", "subject", "bio")


@register(NewsCategory)
class NewsCategoryTR(TranslationOptions):
    fields = ("name",)


@register(NewsPost)
class NewsPostTR(TranslationOptions):
    fields = ("title", "excerpt", "body")


@register(GalleryImage)
class GalleryImageTR(TranslationOptions):
    fields = ("caption",)


@register(FAQ)
class FAQTR(TranslationOptions):
    fields = ("question", "answer")
