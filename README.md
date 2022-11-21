# Django-Stripe-Test

## Проверка тестового задания

### Запуск контейнеров (I вариант)

1) В файле *.env.dev* меняем **STRIPE_PUBLIC_KEY** и **STRIPE_SECRET_KEY** на свои из профиля Stripe.

2) После этого создаем новый образ и запускаем контейнеры командой:

<code>docker-compose up -d --build</code>

3) После применяем migrations

<code>docker-compose exec web python manage.py migrate --noinput</code>

4) После создаем superuser, чтобы иметь доступ к Django admin

<code>docker-compose exec web python manage.py createsuperuser</code>

### Запуск приложения на удаленном сервере (II вариант)

[https://artemusstripe.pythonanywhere.com/](https://artemusstripe.pythonanywhere.com/)

## Функции веб-сервиса

Присутствует реализация как Checkout Session, так и PaymentIntent

/create - отвечает за создание item, discount, tax, order как в локальной базе данных, так и в dashboard Stripe. 

/items - список всех items
/orders - список всех orders
