# Wisdom School — сайт wisdomschool.uz

Сайт частной школы Wisdom School (Ташкент) на Django 5.2, свёрстан по макету из Figma.

* Страницы: главная, о школе, обучение, поступление (форма заявки + FAQ), учителя, новости, галерея, контакты (форма), политика конфиденциальности.
* Три языка: узбекский (по умолчанию), русский, английский — `/uz/`, `/ru/`, `/en/`.
* Админка `/admin/`: новости и категории, учителя, ступени обучения, галерея, FAQ, контакты школы, заявки и сообщения (с выгрузкой в Excel/CSV). Тексты в админке вводятся на трёх языках во вкладках.
* SEO: `sitemap.xml`, `robots.txt`, hreflang, Open Graph, schema.org.
* Защита форм от спама (скрытое поле), уведомления о заявках на e-mail (по желанию).

## Локальный запуск

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # поставьте DJANGO_DEBUG=true
python manage.py migrate
python manage.py seed_demo      # демо-контент из макета
python manage.py createsuperuser
python manage.py runserver
```

Тесты: `python manage.py test school`

## Переводы

Тексты интерфейса — в `locale/ru` и `locale/uz` (`django.po`). После правки:
`python manage.py compilemessages` (нужен gettext). Скомпилированные `.mo` лежат в репозитории,
поэтому на хостинге gettext не нужен.

## Установка на хостинг

См. [DEPLOY_RU.md](DEPLOY_RU.md) — пошагово для cPanel «Setup Python App».
