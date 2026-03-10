from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Sport, GearCategory, Gear, News, Order
import json
import requests
import stripe 
import re

# ==========================================
# 👇 НАЛАШТУВАННЯ TELEGRAM ТА STRIPE
# ==========================================
TELEGRAM_BOT_TOKEN = 'СЮДИ_ВСТАВ_ТОКЕН_БОТА' 
TELEGRAM_CHAT_ID = 'СЮДИ_ВСТАВ_СВІЙ_ID'

import os
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def send_telegram_order(name, phone, items_list, total_price):
    if TELEGRAM_BOT_TOKEN == 'СЮДИ_ВСТАВ_ТОКЕН_БОТА': return
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

# --- 🔑 АВТОРИЗАЦІЯ ТА РЕЄСТРАЦІЯ ---

def user_login(request):
    # 🔥 ПЕРЕВІРКА: Якщо користувач вже увійшов, не показуємо йому вікно входу
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
    # 🔥 ПЕРЕВІРКА: Якщо користувач вже увійшов, не показуємо форму реєстрації
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

# --- ГОЛОВНІ СТОРІНКИ ---

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
            cart_items.append({
                'gear': gear,
                'quantity': quantity,
                'subtotal': subtotal
            })
        
    return render(request, 'gear/cart.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })

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
                amount=total_amount,
                currency='uah',
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
        
        line_items = []
        items_for_tg = []
        total_amount = 0

        for gear_id, quantity in cart.items():
            gear = Gear.objects.filter(id=gear_id).first()
            if gear:
                Order.objects.create(
                    gear=gear, 
                    customer_name=name, 
                    customer_phone=phone, 
                    customer_email=email
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

        if not line_items: return redirect('cart_detail')

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/order-success/'),
                cancel_url=request.build_absolute_uri('/cart/'),
            )
            send_telegram_order(name, phone, items_for_tg, total_amount)
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
        
        Order.objects.create(
            gear=gear, 
            customer_name=name, 
            customer_phone=phone, 
            customer_email=email
        )
        send_telegram_order(name, phone, [{'gear': gear, 'quantity': 1}], gear.price)

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

@csrf_exempt
def query_openrouter(request):
    try:
        prompt = ""
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                prompt = data.get('prompt', '')
            except: pass
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

        system_instruction = (
            "Ти — досвідчений інструктор та гід для початківців у світі екстремального спорту. "
            "Твоя мета — давати МАКСИМАЛЬНО РОЗГОРНУТІ, детальні та зрозумілі пояснення. "
            "Розкладай усе по поличках. Використовуй списки. Пояснюй терміни. "
            "Форматуй відповідь HTML тегами."
        )

        data = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            ai_text = ai_text.replace("\n", "<br>")
            return JsonResponse({'content': ai_text})
        else:
            return JsonResponse({'content': f"⚠️ Помилка API: {response.status_code}"})
    except Exception as e:
        return JsonResponse({'content': f"⚠️ Помилка сервера: {str(e)}"})

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
                if weight > 85: calculated_size += 5

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