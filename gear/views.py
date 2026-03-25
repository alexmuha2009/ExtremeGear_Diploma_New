from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, FloatField
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Sport, GearCategory, Gear, News, Order, RentalItem, Rental
from django.db.models import FloatField
from django.db.models.functions import Cast
import json
import requests
import stripe
import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from decimal import Decimal

load_dotenv()

TELEGRAM_BOT_TOKEN = '8628245847:AAG3Mlxk2ycbuGVnXg1ouHhzo-j9lqjem6E'
TELEGRAM_CHAT_ID = '1654502612'

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def send_telegram_order(name, phone, items_list, total_price):
    if TELEGRAM_BOT_TOKEN == 'СЮДИ_ВСТАВ_ТОКЕН_БОТА':
        return
    try:
        message = f"🔥 <b>НОВЕ ЗАМОВЛЕННЯ!</b>\n"
        message += f"👤 <b>Клієнт:</b> {name}\n"
        message += f"📞 <b>Телефон:</b> {phone}\n"
        message += f"➖➖➖➖➖➖➖➖➖➖\n"
        message += f"🛒 <b>ТОВАРИ:</b>\n"
        for item in items_list:
            gear_name = item['gear'].name if isinstance(item['gear'], Gear) else item['gear'].name
            quantity = item['quantity']
            message += f"▫️ {gear_name} — {quantity} шт.\n"
        message += f"➖➖➖➖➖➖➖➖➖➖\n"
        message += f"💰 <b>СУМА: {total_price} грн</b>"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Помилка Telegram: {e}")


def send_telegram_rental(name, phone, item_name, start_date, end_date, total_price):
    try:
        message = (
            f"🏍️ <b>НОВА ОРЕНДА!</b>\n"
            f"👤 <b>Клієнт:</b> {name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🎽 <b>Спорядження:</b> {item_name}\n"
            f"📅 <b>З:</b> {start_date}\n"
            f"📅 <b>До:</b> {end_date}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"💰 <b>СУМА: {total_price} грн</b>"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Помилка Telegram оренда: {e}")


def get_chat_id_by_username(username):
    import json, os
    users_file = 'tg_users.json'
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
        return users.get(username.lower().lstrip('@'))
    return None


def send_telegram_to_buyer(telegram_username, name, items_list, total_price):
    if not telegram_username:
        return
    chat_id = get_chat_id_by_username(telegram_username)
    if not chat_id:
        print(f"DEBUG: chat_id не знайдено для {telegram_username}")
        return
    today = datetime.now()
    send_date = (today + timedelta(days=1)).strftime('%d.%m.%Y')
    arrive_date = (today + timedelta(days=4)).strftime('%d.%m.%Y')
    items_text = ""
    for item in items_list:
        gear_name = item['gear'].name
        quantity = item['quantity']
        items_text += f"▫️ {gear_name} — {quantity} шт.\n"
    message = (
        f"✅ <b>Замовлення підтверджено!</b>\n\n"
        f"👤 <b>Клієнт:</b> {name}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🛒 <b>Ваші товари:</b>\n{items_text}"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"💰 <b>Сума:</b> {total_price} грн\n\n"
        f"📅 <b>Дата відправлення:</b> {send_date}\n"
        f"📬 <b>Орієнтовна доставка:</b> {arrive_date}\n\n"
        f"📍 <b>Вкажіть адресу доставки у відповідь на це повідомлення:</b>\n"
        f"Місто: ...\nВідділення НП: ...\nКоментар: ..."
    )
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        print(f"DEBUG Telegram buyer response: {response.status_code}")
    except Exception as e:
        print(f"Помилка надсилання покупцю: {e}")


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin:index')
            next_url = request.GET.get('next')
            if next_url:
                separator = '&' if '?' in next_url else '?'
                return redirect(next_url + separator + 'open_modal=1')
            return redirect('home')
        else:
            messages.error(request, "Невірний логін або пароль")
    return render(request, 'gear/login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if password != password_confirm:
            messages.error(request, "Паролі не збігаються!")
        elif len(password) < 8:
            messages.error(request, "Пароль занадто короткий!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Користувач вже існує!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                separator = '&' if '?' in next_url else '?'
                return redirect(next_url + separator + 'open_modal=1')
            return redirect('home')
    return render(request, 'gear/register.html')


def user_logout(request):
    logout(request)
    return redirect('home')


from django.core.paginator import Paginator


def home(request):
    sports_with_count = Sport.objects.annotate(items_count=Count('gears'))
    sport_id = request.GET.get('sport_id')
    filter_type = request.GET.get('filter')
    selected_sport = None
    if sport_id:
        selected_sport = get_object_or_404(Sport, id=sport_id)
        gear_list = selected_sport.gears.all()
    elif filter_type == 'new':
        gear_list = Gear.objects.filter(in_stock=True).order_by('-id')
    elif filter_type == 'sale':
        gear_list = Gear.objects.filter(in_stock=True, rating__gte=4).order_by('-rating')
    elif filter_type == 'top':
        gear_list = Gear.objects.filter(in_stock=True).order_by('-rating')
    elif filter_type == 'stock':
        gear_list = Gear.objects.filter(in_stock=True)
    else:
        gear_list = Gear.objects.filter(in_stock=True)
    paginator = Paginator(gear_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gear/base.html', {
        'sports': sports_with_count,
        'selected_sport': selected_sport,
        'categories': GearCategory.objects.all(),
        'gear_list': page_obj,
        'page_obj': page_obj,
        'active_filter': filter_type,
    })


def order_success(request):
    return render(request, 'gear/order_success.html')


def gear_detail(request, gear_id):
    gear = get_object_or_404(Gear, id=gear_id)
    return render(request, 'gear/gear_detail.html', {'gear': gear})


def category_gear(request, category_id):
    sports_with_count = Sport.objects.annotate(items_count=Count('gears'))
    category = get_object_or_404(GearCategory, id=category_id)
    return render(request, 'gear/base.html', {
        'categories': GearCategory.objects.all(),
        'sports': sports_with_count,
        'gear_list': Gear.objects.filter(category=category)
    })


def sport_detail(request, sport_id):
    sports_with_count = Sport.objects.annotate(items_count=Count('gears'))
    sport = get_object_or_404(Sport, id=sport_id)
    return render(request, 'gear/base.html', {
        'categories': GearCategory.objects.all(),
        'sports': sports_with_count,
        'selected_sport': sport,
        'gear_list': sport.gears.all()
    })


def news_list(request):
    return render(request, 'gear/news.html', {'news_list': News.objects.all()})


def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    return render(request, 'gear/news_detail.html', {'news_item': news_item})


def search_gear(request):
    sports_with_count = Sport.objects.annotate(items_count=Count('gears'))
    query = request.GET.get('q', '')
    gear_list = Gear.objects.filter(name__icontains=query) if query else []
    return render(request, 'gear/base.html', {
        'categories': GearCategory.objects.all(),
        'sports': sports_with_count,
        'gear_list': gear_list
    })


def gear_table(request):
    return render(request, 'gear/gear_table.html', {'sports': Sport.objects.all()})


def beginners_guide(request):
    return render(request, 'gear/beginners_guide.html')


def add_to_cart(request, gear_id):
    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/gear/{gear_id}/")
    cart = request.session.get('cart', {})
    gear_id_str = str(gear_id)
    if gear_id_str in cart:
        cart[gear_id_str] += 1
    else:
        cart[gear_id_str] = 1
    request.session['cart'] = cart
    return redirect('cart_detail')


def remove_from_cart(request, gear_id):
    cart = request.session.get('cart', {})
    gear_id_str = str(gear_id)
    if gear_id_str in cart:
        cart.pop(gear_id_str)
        request.session['cart'] = cart
    return redirect('cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for gear_id, quantity in cart.items():
        gear = Gear.objects.filter(id=gear_id).first()
        if gear:
            subtotal = gear.price * quantity
            total_price += subtotal
            cart_items.append({'gear': gear, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'gear/cart.html', {'cart_items': cart_items, 'total_price': total_price})


@csrf_exempt
def create_payment_intent(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.method == 'POST':
        try:
            cart = request.session.get('cart', {})
            total_amount = 0
            if cart:
                for gear_id, quantity in cart.items():
                    gear = Gear.objects.filter(id=gear_id).first()
                    if gear:
                        total_amount += int(gear.price * 100)
            else:
                data = json.loads(request.body)
                gear_id = data.get('gear_id')
                gear = get_object_or_404(Gear, id=gear_id)
                total_amount = int(gear.price * 100)
            intent = stripe.PaymentIntent.create(
                amount=total_amount, currency='uah',
                automatic_payment_methods={'enabled': True},
            )
            return JsonResponse({'clientSecret': intent.client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def checkout_cart(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        cart = request.session.get('cart', {})
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        telegram = request.POST.get('telegram', '')
        line_items = []
        items_for_tg = []
        total_amount = 0
        for gear_id, quantity in cart.items():
            gear = Gear.objects.filter(id=gear_id).first()
            if gear:
                Order.objects.create(
                    gear=gear, customer_name=name, customer_phone=phone,
                    customer_email=email, customer_telegram=telegram
                )
                items_for_tg.append({'gear': gear, 'quantity': quantity})
                total_amount += gear.price * quantity
                line_items.append({
                    'price_data': {
                        'currency': 'uah',
                        'product_data': {'name': gear.name},
                        'unit_amount': int(gear.price * 100),
                    },
                    'quantity': quantity,
                })
        if not line_items:
            return redirect('cart_detail')
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'], line_items=line_items, mode='payment',
                success_url=request.build_absolute_uri('/order-success/'),
                cancel_url=request.build_absolute_uri('/cart/'),
            )
            send_telegram_order(name, phone, items_for_tg, total_amount)
            send_telegram_to_buyer(telegram, name, items_for_tg, total_amount)
            request.session['cart'] = {}
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return HttpResponse(f"Помилка Stripe: {str(e)}")
    return redirect('cart_detail')


def quick_order(request, gear_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/register/?next=/gear/{gear_id}/")
        gear = get_object_or_404(Gear, id=gear_id)
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        telegram = request.POST.get('telegram', '')
        Order.objects.create(
            gear=gear, customer_name=name, customer_phone=phone,
            customer_email=email, customer_telegram=telegram
        )
        send_telegram_order(name, phone, [{'gear': gear, 'quantity': 1}], gear.price)
        send_telegram_to_buyer(telegram, name, [{'gear': gear, 'quantity': 1}], gear.price)
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'uah',
                        'product_data': {'name': gear.name},
                        'unit_amount': int(gear.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/order-success/'),
                cancel_url=request.build_absolute_uri('/'),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return HttpResponse(f"Помилка Stripe: {str(e)}")
    return redirect('home')


# ==========================================
# ОРЕНДА СПОРЯДЖЕННЯ
# ==========================================

def rental_list(request):
    sport_id = request.GET.get('sport_id')
    sports = Sport.objects.all()

    items = Gear.objects.filter(
        is_rentable=True,
        in_stock=True,
        price_per_day__isnull=False
    ).distinct()

    selected_sport = None
    if sport_id:
        selected_sport = get_object_or_404(Sport, id=sport_id)
        items = items.filter(sports__id=sport_id).distinct()

    return render(request, 'gear/rental.html', {
        'rental_items': items,
        'sports': sports,
        'selected_sport': selected_sport,
    })


def rental_checkout(request, item_id):
    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/rental/{item_id}/")

    item = get_object_or_404(
        Gear,
        id=item_id,
        is_rentable=True,
        in_stock=True,
        price_per_day__isnull=False
    )

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        telegram = request.POST.get('telegram', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            days = (end - start).days

            if days < 1:
                messages.error(request, "Дата закінчення має бути пізніше дати початку!")
                return redirect(f"/rental/{item_id}/")

            total_price = item.price_per_day * days

            rental = Rental.objects.create(
                gear=item,
                customer_name=name,
                customer_phone=phone,
                customer_email=email,
                customer_telegram=telegram,
                start_date=start,
                end_date=end,
                total_price=total_price,
                status='pending'
            )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'uah',
                        'product_data': {
                            'name': f"Оренда: {item.name} ({days} діб)"
                        },
                        'unit_amount': int(total_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/rental/success/{rental.id}/'),
                cancel_url=request.build_absolute_uri(f'/rental/{item_id}/'),
            )

            rental.stripe_session_id = checkout_session.id
            rental.save()

            send_telegram_rental(
                name,
                phone,
                item.name,
                start_date,
                end_date,
                total_price
            )

            return redirect(checkout_session.url, code=303)

        except Exception as e:
            messages.error(request, f"Помилка: {str(e)}")
            return redirect(f"/rental/{item_id}/")

    return render(request, 'gear/rental_detail.html', {'item': item})


def rental_success(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.status = 'confirmed'
    rental.save()
    return render(request, 'gear/rental_success.html', {'rental': rental})


@csrf_exempt
def rental_price_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            item = get_object_or_404(
                Gear,
                id=item_id,
                is_rentable=True,
                in_stock=True,
                price_per_day__isnull=False
            )

            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            days = (end - start).days

            if days < 1:
                return JsonResponse({'error': 'Невірні дати'}, status=400)

            total = item.price_per_day * days
            return JsonResponse({
                'days': days,
                'price_per_day': float(item.price_per_day),
                'total': float(total)
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Bad request'}, status=400)


# ==========================================
# AI АСИСТЕНТ
# ==========================================

def get_relevant_products(user_message: str, limit=6):
    stop_words = {
        'я', 'мені', 'що', 'як', 'де', 'хочу', 'треба', 'можна',
        'будь', 'ласка', 'порадь', 'підбери', 'знайди', 'є', 'у',
        'в', 'на', 'до', 'це', 'той', 'яка', 'який', 'які', 'для',
        'мене', 'нам', 'нас', 'він', 'вона', 'вони', 'ми', 'ти',
        'про', 'при', 'але', 'або', 'той', 'ця', 'цей', 'так', 'ні',
        'мій', 'потрібен', 'потрібна', 'потрібні', 'потрібно'
    }
    keywords = [w for w in user_message.lower().split() if w not in stop_words and len(w) > 2]
    if not keywords:
        return []
    query = Q()
    for keyword in keywords:
        query |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
    return list(
        Gear.objects.filter(in_stock=True).filter(query)
        .annotate(price_float=Cast('price', FloatField()))
        .values('id', 'name', 'description', 'price_float', 'image_url')
        [:limit]
    )


def render_products_html(products: list) -> str:
    if not products:
        return ""
    html = '<div style="margin-top:16px;">'
    for p in products:
        name = p.get('name', '')
        pid = p.get('id', '')
        description = p.get('description', '') or ''
        html += f"""
<div style="margin-bottom:16px;padding:12px;background:rgba(255,255,255,0.04);border-radius:10px;border:1px solid rgba(174,221,0,0.15);">
  <a href="http://localhost:8000/gear/{pid}/" style="display:inline-flex;align-items:center;gap:12px;text-decoration:none;color:inherit;">
    <img src="http://127.0.0.1:8000/api/gear/{pid}/image/" alt="{name}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;flex-shrink:0;">
    <span style="font-weight:700;font-size:1rem;">{name}</span>
  </a>
  <p style="margin:8px 0 0 0;font-size:0.83rem;color:rgba(255,255,255,0.55);line-height:1.5;">{description}</p>
</div>"""
    html += '</div>'
    return html


def clean_ai_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```html"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


@csrf_exempt
def query_openrouter(request):
    try:
        prompt = ""
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                prompt = data.get('prompt', '')
            except:
                pass
        else:
            prompt = request.GET.get('q', '')

        if not prompt:
            return JsonResponse({'content': "Напишіть, що вас цікавить..."})

        api_key = "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"
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Extreme Gear Store"
        }

        system_instruction = """Ти — консультант магазину екстремального спорядження.
Твоя тема: спортивне спорядження, екіпірування, виживання та екстремальний спорт.

ОБОВ'ЯЗКОВО постав тег в ПЕРШОМУ рядку відповіді:
- [SHOW_PRODUCTS] — якщо людина шукає або просить порадити конкретне спорядження чи товар
- [NO_PRODUCTS] — у всіх інших випадках (травми, поради, техніка, офтопік тощо)

ПРАВИЛА:
1. Запит про підбір/пошук спорядження → [SHOW_PRODUCTS] + 2-3 речення вступу.
2. Запит про спорт, травми, техніку виживання, поради → [NO_PRODUCTS] + розгорнута корисна відповідь.
3. Офтопік → [NO_PRODUCTS] + ввічливо поясни свою спеціалізацію.

Відповідай українською. Повертай ТІЛЬКИ чистий HTML без markdown (без ```html або ```)."""

        data = {
            "model": "nvidia/nemotron-3-nano-30b-a3b:free",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            ai_text = clean_ai_response(ai_text)

            if ai_text.startswith("[SHOW_PRODUCTS]"):
                ai_text = ai_text.replace("[SHOW_PRODUCTS]", "", 1).strip()
                products_from_db = get_relevant_products(prompt, limit=6)
                products_html = render_products_html(products_from_db)
                final_html = ai_text + products_html
            else:
                ai_text = ai_text.replace("[NO_PRODUCTS]", "", 1).strip()
                final_html = ai_text

            return JsonResponse({'content': final_html})
        else:
            return JsonResponse({'content': f"Помилка API: {response.status_code} {response.text[:100]}"})
    except Exception as e:
        return JsonResponse({'content': f"Помилка сервера: {str(e)}"})


@csrf_exempt
def calculate_gear_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            height = int(data.get('height', 170))
            weight = int(data.get('weight', 70))
            temp = int(data.get('temp', -5))
            gender = data.get('gender', 'male')
            sport_id = data.get('sport_id')

            if gender == 'child':
                calculated_size = height - 25
                cloth_advice = "Для дітей обов'язковий повний захист та яскравий одяг для видимості на схилі."
            elif gender == 'female':
                calculated_size = height - 18
                cloth_advice = "Обирайте моделі з урахуванням анатомії та кращого термозахисту."
            else:
                calculated_size = height - 15
                cloth_advice = "Стандартний розмір. Зверніть увагу на жорсткість спорядження."
                if weight > 85:
                    calculated_size += 5

            if temp < -10:
                cloth_advice += " Потрібен надійний теплий захист та якісна термобілизна."
            elif temp < 5:
                cloth_advice += " Оберіть вітрозахисне спорядження з флісовим утепленням."
            else:
                cloth_advice += " Достатньо легкого екіпірування для помірної температури."

            if sport_id:
                products = Gear.objects.filter(sports__id=sport_id, in_stock=True).distinct()[:4]
            else:
                products = Gear.objects.filter(in_stock=True).distinct()[:4]

            products_data = []
            for item in products:
                products_data.append({
                    'id': item.id,
                    'name': item.name,
                    'price': str(item.price),
                    'image_url': item.image.url if item.image else "",
                    'brand': item.brand
                })

            return JsonResponse({
                'calculated_size': f"{calculated_size} см",
                'cloth_info': cloth_advice,
                'products': products_data
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Bad Request'}, status=400)


def get_gear_image_redirect(request, gear_id):
    try:
        gear = get_object_or_404(Gear, id=gear_id)
        if gear.image:
            return redirect(gear.image.url)
        elif gear.image_url:
            return redirect(gear.image_url)
        else:
            return HttpResponse('Картинка не знайдена', status=404)
    except Exception as e:
        return HttpResponse(f'Помилка: {str(e)}', status=500)