from django.db import migrations

CONTACTS = {
    "phone": "+998 97 260 66 11",
    "email": "yoqubjondeveloper@gmail.com",
    "telegram": "https://t.me/wisdomschooltashkent",
    "facebook": "https://fb.com/WisdomSchoolTashkent",
    "instagram": "https://instagram.com/wisdom.school.uz",
    "address_uz": "Toshkent, Shayxontohur tumani, Beltepa ko‘chasi, 8-tor ko‘cha. Mo‘ljal: Yangi ToshMI, 316-maktab",
    "address_ru": "Ташкент, Шайхонтахурский р-н, ул. Белтепа, 8-й проезд. Ориентир: Новый ТашМИ, школа № 316",
    "address_en": "8th passage, Beltepa Street, Shaykhontohur district, Tashkent. Landmark: New TashMI, School No. 316",
}


def set_contacts(apps, schema_editor):
    SiteSettings = apps.get_model("school", "SiteSettings")
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    settings.address = settings.address or CONTACTS["address_uz"]
    for field, value in CONTACTS.items():
        if not getattr(settings, field):
            setattr(settings, field, value)
    settings.save()


class Migration(migrations.Migration):
    dependencies = [("school", "0001_initial")]
    operations = [migrations.RunPython(set_contacts, migrations.RunPython.noop)]
