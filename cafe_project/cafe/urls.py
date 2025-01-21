from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('reserve-table/', views.reserve_table, name='reserve_table'),
    path('menu/', views.menu, name='menu'),
    path('menus/', views.menus, name='menus'),
    path('product/<int:id>/', views.ProductDetail, name='product'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart, name='add_to_cart'),
    path('cart/add/cooldrink/<int:cool_drink_id>/', views.cart, name='add_cooldrink_to_cart'),
    path('cart/delete/<int:id>/', views.DeleteItem, name='delete'),
    path('cooldrinks/', views.cooldrinks, name='cooldrinks'),
    path('cooldrinks_details/<int:id>/', views.cooldrinks_details, name='cooldrinks_details'),
    path('search/', views.search_view, name='search'),
    path("shakes/<int:id>/",views.Shakes_details,name='shakes'),
    path('ShakeS',views.ShakeS,name='ShakeS'),
]