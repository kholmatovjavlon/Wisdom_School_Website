# Установка сайта на хостинг ahost.uz (cPanel → Setup Python App)

Инструкция рассчитана на аккаунт `wisdoms1`, где уже работает Python-приложение
`feedback.wisdomschool.uz` из `/home/wisdoms1/feedback_bot`. Новый сайт ставится
**рядом** с ним в отдельную папку и не трогает поддомены.

> ⚠️ Всё, что меняет основной домен `wisdomschool.uz`, делайте только после резервной
> копии (шаг 1) и проверки поддоменов (шаг 2).

## 1. Резервная копия текущего сайта

1. cPanel → **File Manager** → откройте `/home/wisdoms1/`.
2. Выделите папку `public_html` → **Compress** → Zip → имя `public_html_backup_ГГГГ-ММ-ДД.zip`.
3. Скачайте архив себе на компьютер (правый клик → Download).
4. Дополнительно: cPanel → **Backup** → «Download a Home Directory Backup».

## 2. Проверка поддоменов (crm, star, feedback)

cPanel → **Domains**. Посмотрите колонку **Document Root** для
`crm.wisdomschool.uz`, `star.wisdomschool.uz`, `feedback.wisdomschool.uz`.

* Если папки поддоменов лежат **вне** `public_html` (например `/home/wisdoms1/crm.wisdomschool.uz`) — всё в порядке, сайт их не затронет.
* Если папка поддомена лежит **внутри** `public_html` (например `public_html/crm`), то настройки
  Python-приложения из `public_html/.htaccess` будут действовать и на него. Тогда в начало файла
  `.htaccess` **в папке этого поддомена** добавьте строку:

  ```
  PassengerEnabled off
  ```

  (для `feedback`, который сам является Python-приложением, эту строку **не** добавляйте —
  у него свои настройки Passenger). После запуска сайта обязательно откройте все три поддомена и
  убедитесь, что они работают.

## 3. Загрузка кода

Через cPanel → **Terminal** (или SSH):

```bash
cd /home/wisdoms1
git clone https://github.com/kholmatovjavlon/Wisdom_School_Website.git wisdom_site
```

Если терминала нет: cPanel → **Git Version Control** → Create → Clone URL как выше,
Repository Path `/home/wisdoms1/wisdom_site`.

## 4. База данных (по желанию MySQL)

По умолчанию используется SQLite (файл `db.sqlite3` в папке сайта) — для школьного сайта этого достаточно.
Если хотите MySQL: cPanel → **MySQL Databases** → создайте базу `wisdoms1_site`, пользователя
`wisdoms1_site`, дайте ему **ALL PRIVILEGES** на базу. Django 5.2 требует MariaDB 10.5+ или MySQL 8.0.11+.

## 5. Создание Python-приложения

cPanel → **Setup Python App** → **Create Application**:

| Поле | Значение |
|---|---|
| Python version | **3.11** (или новее, если есть) |
| Application root | `wisdom_site` |
| Application URL | `wisdomschool.uz` (пустой путь) |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |

Нажмите **Create**. Вверху страницы появится команда для входа в виртуальное окружение, вида:

```bash
source /home/wisdoms1/virtualenv/wisdom_site/3.11/bin/activate && cd /home/wisdoms1/wisdom_site
```

## 6. Настройки (.env)

В папке `/home/wisdoms1/wisdom_site` создайте файл `.env` по образцу `.env.example`:

```ini
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=длинная-случайная-строка-50+-символов
DJANGO_ALLOWED_HOSTS=wisdomschool.uz,www.wisdomschool.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://wisdomschool.uz,https://www.wisdomschool.uz
DB_ENGINE=sqlite
# для MySQL:
# DB_ENGINE=mysql
# DB_NAME=wisdoms1_site
# DB_USER=wisdoms1_site
# DB_PASSWORD=пароль
# Уведомления о заявках на почту (необязательно):
# ADMISSIONS_NOTIFY_EMAILS=info@wisdomschool.uz
# EMAIL_HOST=mail.wisdomschool.uz
# EMAIL_HOST_USER=noreply@wisdomschool.uz
# EMAIL_HOST_PASSWORD=пароль-почтового-ящика
```

Секретный ключ можно получить командой (после шага 7):
`python -c "import secrets; print(secrets.token_urlsafe(50))"`

## 7. Установка зависимостей и подготовка

В Terminal выполните команду из шага 5, затем:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser        # логин и пароль для админки
python manage.py seed_demo              # демо-контент из макета (можно пропустить)
```

## 8. Освобождение public_html

Passenger обрабатывает запросы, только если в `public_html` нет файла с таким же именем.
Старый `index.html` / `index.php` перехватит главную страницу, поэтому **после резервной копии**:

1. Создайте папку `/home/wisdoms1/old_site/`.
2. Перенесите в неё старые файлы сайта из `public_html`.
3. **Не переносите**: `.htaccess` (его дописал Setup Python App), `.well-known` (SSL),
   `cgi-bin` и папки поддоменов, если они лежат внутри `public_html`.

## 9. Запуск и проверка

cPanel → Setup Python App → **Restart**. Проверьте:

* https://wisdomschool.uz — откроется `/uz/` (узбекская версия), переключатель UZ / RU / EN вверху;
* https://wisdomschool.uz/admin/ — вход по логину из шага 7;
* форму заявки на странице «Qabul» — заявка появится в админке в разделе «Заявки на поступление»;
* поддомены crm, star, feedback.

## Обновление сайта

```bash
source /home/wisdoms1/virtualenv/wisdom_site/3.11/bin/activate && cd /home/wisdoms1/wisdom_site
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt     # или Restart в Setup Python App
```

## Откат

1. Setup Python App → удалите приложение `wisdom_site` (код и база останутся в папке).
2. Верните старые файлы из `/home/wisdoms1/old_site/` в `public_html` (или распакуйте архив из шага 1).

## Где хранится содержимое

* Фото, загруженные через админку: `/home/wisdoms1/wisdom_site/media/`
* База SQLite: `/home/wisdoms1/wisdom_site/db.sqlite3` — включайте обе папки в резервные копии.
