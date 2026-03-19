from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gear import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ГОЛОВНІ СТОРІНКИ ---
    path('', views.home, name='home'),
    path('sport/<int:sport_id>/', views.sport_detail, name='sport_detail'),
    path('category/<int:category_id>/', views.category_gear, name='category_gear'),
    path('gear/<int:gear_id>/', views.gear_detail, name='gear_detail'),
    path('search/', views.search_gear, name='search_gear'),
    path('news/', views.news_list, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('calculator/', views.gear_table, name='gear_table'),

    # --- АВТОРИЗАЦІЯ ТА РЕЄСТРАЦІЯ ---
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # --- СТОРІНКА УСПІХУ ---
    path('order-success/', views.order_success, name='order_success'),

    # --- API ---
    path('api/ai-chat/', views.query_openrouter, name='ai_chat'),
    path('api/calculate-gear/', views.calculate_gear_api, name='calculate_gear_api'),
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('api/gear/<int:gear_id>/image/', views.get_gear_image_redirect, name='gear_image'),  # ✅ ДОДАНО

    # --- 🛒 КОШИК ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:gear_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:gear_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),

    # --- 🚀 ШВИДКЕ ЗАМОВЛЕННЯ ---
    path('order/<int:gear_id>/', views.quick_order, name='quick_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)