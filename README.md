# Проект Foodgram
Status of last deployment:
![Status](https://github.com/PentiukPavel/foodgram-project-react/actions/workflows/main.yml/badge.svg)

IP 158.160.46.2

# «Продуктовый помощник»
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 
## Инструкции для деплоя проекта на сервере

### 1) Docker

Установить Docker. Инструкция по установке: https://docs.docker.com/engine/install/ <br>


### 2) Автодеплой

В 'Actions secrets' в настройках проекта на GitHub внести параметры сервера: <br>

```
DOCKER_PASSWORD - Пароль от DockerHub
DOCKER_USERNAME - Логин от DockerHub
HOST - Публичный ip адрес сервера
USER - Пользователь сервера
PASSPHRASE - Если ssh-ключ защищен фразой-паролем
SSH_KEY - Приватный ssh-ключ
```

После успешного commit или pull-request автоматически будет развернут на сервере. <br>

### При первом деплое

Выполнить миграции:

```
sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
```

Собрать статику:

```
sudo docker compose exec backend python manage.py collectstatic --noinput
```

Создать суперпользователя:

```
sudo docker compose exec backend python manage.py createsuperuser
```
Заполнить базу ингредиентами:

```
sudo docker compose exec -T backend python manage.py import_csv 
```

## Системные требования
### Python==3.9

## Стек
### Django
### gunicorn
### PostgreSQL
### nginx
### Docker
### Django REST Framework
### Github Actions
### Яндекс.Облако