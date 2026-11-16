"""Fill an empty database with the demo content from the Figma design.

Usage:  python manage.py seed_demo
Safe to run more than once: existing records are left untouched.
"""
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from school.models import FAQ, LearningStage, NewsCategory, NewsPost, SiteSettings, Teacher

IMG = Path(settings.BASE_DIR) / "static" / "img"


def attach(instance, field, filename):
    path = IMG / filename
    if path.exists():
        with path.open("rb") as fh:
            getattr(instance, field).save(filename, File(fh), save=False)


STAGES = [
    {
        "tone": "light",
        "title": ("Boshlang‘ich sinflar", "Начальная школа", "Primary years"),
        "tagline": ("Quvonchli boshlanish", "Радостное начало", "A joyful beginning"),
        "summary": (
            "Maqsadli izlanishlar orqali ishonch, qiziquvchanlik va mustahkam poydevor yaratish.",
            "Уверенность, любознательность и прочный фундамент через осмысленные открытия.",
            "Build confidence, curiosity and strong foundations through purposeful discovery.",
        ),
        "headline": ("O‘rganish quvonchini kashf eting.", "Откройте радость учёбы.", "Discover the joy of learning."),
        "description": (
            "O‘qish, yozish, matematika va atrofimizdagi dunyoni o‘rganishda mustahkam boshlanish.",
            "Крепкий старт в чтении, письме, математике и познании окружающего мира.",
            "Strong beginnings in reading, writing, mathematics and the world around us.",
        ),
        "highlights": (
            "Savodxonlik va hisob\nIjodiy izlanish\nIshonch va jamoaga mansublik",
            "Грамотность и счёт\nТворческие открытия\nУверенность и чувство принадлежности",
            "Literacy & numeracy\nCreative exploration\nConfidence & belonging",
        ),
    },
    {
        "tone": "lavender",
        "title": ("O‘rta sinflar", "Средняя школа", "Middle years"),
        "tagline": ("Kengroq dunyo", "Мир шире", "A wider world"),
        "summary": (
            "G‘oyalarni bog‘lash, yangi qiziqishlarni kashf etish va mustaqil fikrlovchiga aylanish.",
            "Связывать идеи, открывать новые интересы и учиться мыслить самостоятельно.",
            "Connect ideas, explore new interests and become an independent thinker.",
        ),
        "headline": ("Bog‘liqliklarni toping. O‘z ovozingizni toping.", "Находите связи. Обретайте свой голос.",
                     "Make connections. Find your voice."),
        "description": (
            "Mustaqillik, hamkorlik va tanqidiy fikrlashni rivojlantiruvchi kengroq fanlar tajribasi.",
            "Более широкий круг предметов, развивающий самостоятельность, сотрудничество и критическое мышление.",
            "A broader subject experience that builds independence, collaboration and critical thinking.",
        ),
        "highlights": (
            "Tillar va gumanitar fanlar\nFan va texnologiya\nSan’at va jismoniy tarbiya",
            "Языки и гуманитарные науки\nНаука и технологии\nИскусство и физкультура",
            "Languages & humanities\nScience & technology\nArts & physical education",
        ),
    },
    {
        "tone": "light",
        "title": ("Yuqori sinflar", "Старшая школа", "Senior years"),
        "tagline": ("Kelajak diqqat markazida", "Фокус на будущее", "A future in focus"),
        "summary": (
            "Bilimlarni chuqurlashtirish, yo‘nalish topish va oldindagi imkoniyatlarga tayyorlanish.",
            "Углублять знания, находить своё направление и готовиться к будущим возможностям.",
            "Deepen knowledge, find direction and prepare for the opportunities ahead.",
        ),
        "headline": ("Chuqur fikrlang. Oldinga qarang.", "Думайте глубже. Смотрите вперёд.", "Think deeply. Look ahead."),
        "description": (
            "Fanlar bo‘yicha chuqur bilim beruvchi va keyingi qadamlarni ongli tanlashga yordam beruvchi ta’lim.",
            "Целенаправленное обучение, развивающее глубокие знания предметов и осознанный выбор следующих шагов.",
            "Focused learning that develops subject expertise and supports informed next steps.",
        ),
        "highlights": (
            "Fanlarni chuqur o‘rganish\nMustaqil ta’lim\nKelajak yo‘llari",
            "Глубина предметов и исследование\nСамостоятельное обучение\nПути в будущее",
            "Subject depth & inquiry\nIndependent learning\nFuture pathways",
        ),
    },
]

TEACHERS = [
    ("teacher-madina.jpg", "light", ("Madina Karimova", "Мадина Каримова", "Madina Karimova"),
     ("Fan va texnologiya", "Наука и технологии", "Science & technology"),
     ("Murakkab g‘oyalarni qiziquvchanlik, tajriba va kashfiyot orqali tushunarli qiladi.",
      "Делает сложные идеи понятными через любопытство, эксперименты и открытия.",
      "Making complex ideas accessible through curiosity, experimentation and discovery.")),
    ("teacher-aziz.jpg", "lavender", ("Aziz Rahimov", "Азиз Рахимов", "Aziz Rahimov"),
     ("Matematika va shaxmat", "Математика и шахматы", "Mathematics & chess"),
     ("Qonuniyatlar, imkoniyatlar va yangi nuqtai nazarlarni ko‘ra oladigan ishonchli muammo yechuvchilarni tarbiyalaydi.",
      "Воспитывает уверенных решателей задач, которые видят закономерности, возможности и новые перспективы.",
      "Developing confident problem-solvers who see patterns, possibilities and new perspectives.")),
    ("teacher-nilufar.jpg", "light", ("Nilufar Saidova", "Нилуфар Саидова", "Nilufar Saidova"),
     ("Tillar va gumanitar fanlar", "Языки и гуманитарные науки", "Languages & humanities"),
     ("O‘quvchilarga o‘z ovozini topish va keng dunyo bilan ongli bog‘lanishga yordam beradi.",
      "Помогает ученикам обрести свой голос и вдумчиво взаимодействовать с миром.",
      "Helping students find their voice and connect thoughtfully with the wider world.")),
]

CATEGORIES = [
    ("learning", ("Ta’lim", "Обучение", "Learning")),
    ("school-life", ("Maktab hayoti", "Школьная жизнь", "School life")),
    ("community", ("Hamjamiyat", "Сообщество", "Community")),
]

NEWS = [
    ("science.jpg", "learning", True,
     ("Kichik tajribalar. Katta kashfiyotlar.", "Маленькие эксперименты. Большие открытия.", "Small experiments. Big discoveries."),
     ("Wisdom’da fanni jonlantiradigan savollar, jamoaviy ish va amaliy fikrlashga yaqindan nazar.",
      "Взгляд изнутри: вопросы, командная работа и практическое мышление, которые оживляют науку в Wisdom.",
      "A closer look at the questions, teamwork and hands-on thinking that bring science to life at Wisdom.")),
    ("chess.jpg", "school-life", False,
     ("Uch yurish oldinga o‘ylash.", "Думать на три хода вперёд.", "Thinking three moves ahead."),
     ("Shaxmat qanday qilib sabr va strategiyani hayot saboqlariga aylantiradi.",
      "Как шахматы превращают терпение и стратегию в уроки для жизни.",
      "How chess turns patience and strategy into lessons for life.")),
    ("campus.jpg", "community", False,
     ("O‘zingizni uydagidek his qiladigan joy.", "Место, где ты свой.", "A place to belong."),
     ("Maktab hamjamiyatining markazidagi kundalik aloqalar.",
      "Повседневные связи, на которых держится школьное сообщество.",
      "The everyday connections at the heart of a school community.")),
    ("students.jpg", "learning", False,
     ("Yaxshiroq savollar. Yorqinroq g‘oyalar.", "Лучшие вопросы. Яркие идеи.", "Better questions. Brighter ideas."),
     ("Sinfda qiziquvchanlik yetakchilik qilganda nima sodir bo‘ladi.",
      "Что происходит, когда в классе ведёт любопытство.",
      "What happens when curiosity leads the way in the classroom.")),
]

FAQS = [
    (("Maktabga tashrifni qanday tashkil qilsam bo‘ladi?", "Как договориться о посещении школы?",
      "How can I arrange a school visit?"),
     ("Ariza shaklini to‘ldiring va keyingi qadam sifatida maktabga tashrifni tanlang. Jamoamiz qulay vaqtni belgilashda yordam beradi.",
      "Заполните форму заявки и выберите посещение школы как следующий шаг. Наша команда поможет подобрать удобное время.",
      "Use the enquiry form and choose a school visit as your preferred next step. Our team will help you plan a suitable time.")),
    (("Farzandim uchun qaysi bosqich mos?", "Какая ступень подойдёт моему ребёнку?",
      "Which learning stage is right for my child?"),
     ("Bu farzandingizning yoshi va avvalgi ta’limiga bog‘liq. Qabul jamoamiz siz bilan suhbatlashib, eng mos variantni tavsiya qiladi.",
      "Это зависит от возраста и предыдущего обучения ребёнка. Приёмная комиссия обсудит с вами детали и подскажет лучший вариант.",
      "It depends on your child’s age and previous learning. Our admissions team will talk it through with you and suggest the best fit.")),
    (("Qabul jarayoni nimalardan iborat?", "Из чего состоит процесс поступления?",
      "What does the admissions process involve?"),
     ("Suhbat, maktabga tashrif, farzandingiz bilan tanishuv va keyingi qadamlar bo‘yicha maslahat.",
      "Разговор, посещение школы, знакомство с ребёнком и рекомендации по следующим шагам.",
      "A conversation, a school visit, getting to know your child and guidance on the next steps.")),
    (("To‘lov va bo‘sh o‘rinlar haqida qanday bilsam bo‘ladi?", "Как узнать о стоимости и свободных местах?",
      "How can I learn about fees and availability?"),
     ("Ariza qoldiring yoki maktabga qo‘ng‘iroq qiling — joriy narxlar va bo‘sh o‘rinlar haqida ma’lumot beramiz.",
      "Оставьте заявку или позвоните в школу — мы расскажем об актуальной стоимости и наличии мест.",
      "Send an enquiry or call the school and we will share current fees and availability.")),
    (("Ariza berishdan oldin kimdir bilan gaplashsam bo‘ladimi?", "Можно ли поговорить с кем-то до подачи заявки?",
      "Can I speak to someone before applying?"),
     ("Albatta. Ariza — bu majburiyat emas, balki suhbatning boshlanishi.",
      "Конечно. Заявка — это не обязательство, а начало разговора.",
      "Of course. An enquiry is a conversation, not a commitment.")),
]


def tr(obj, field, values):
    for lang, value in zip(("uz", "ru", "en"), values):
        setattr(obj, f"{field}_{lang}", value)


class Command(BaseCommand):
    help = "Create demo content (learning stages, teachers, news, FAQ) from the design."

    def handle(self, *args, **options):
        SiteSettings.load()

        if not LearningStage.objects.exists():
            for i, data in enumerate(STAGES):
                stage = LearningStage(order=i, tone=data["tone"])
                for key in ("title", "tagline", "summary", "headline", "description", "highlights"):
                    tr(stage, key, data[key])
                stage.save()
            self.stdout.write("Learning stages created")

        if not Teacher.objects.exists():
            for i, (photo, tone, names, subjects, bios) in enumerate(TEACHERS):
                t = Teacher(order=i, tone=tone)
                tr(t, "name", names)
                tr(t, "subject", subjects)
                tr(t, "bio", bios)
                attach(t, "photo", photo)
                t.save()
            self.stdout.write("Teachers created")

        if not NewsCategory.objects.exists():
            for i, (slug, names) in enumerate(CATEGORIES):
                c = NewsCategory(slug=slug, order=i)
                tr(c, "name", names)
                c.save()
            self.stdout.write("News categories created")

        if not NewsPost.objects.exists():
            now = timezone.now()
            for i, (image, cat, featured, titles, excerpts) in enumerate(NEWS):
                p = NewsPost(category=NewsCategory.objects.get(slug=cat), is_featured=featured,
                             published_at=now - timedelta(days=i * 6))
                tr(p, "title", titles)
                tr(p, "excerpt", excerpts)
                tr(p, "body", excerpts)
                attach(p, "image", image)
                p.save()
            self.stdout.write("News created")

        if not FAQ.objects.exists():
            for i, (questions, answers) in enumerate(FAQS):
                f = FAQ(order=i)
                tr(f, "question", questions)
                tr(f, "answer", answers)
                f.save()
            self.stdout.write("FAQ created")

        self.stdout.write(self.style.SUCCESS("Demo content is ready."))
