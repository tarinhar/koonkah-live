from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('item/', views.item, name="item"),
    path('item/create/', views.create_item, name="item-create"),
    path('item/<str:pk>/', views.item_detail, name="item-detail"),
    path('profile/<str:pk>/', views.user_profile, name="user-profile"),
    path('item/<str:pk>/edit/', views.update_item, name="item-update"),
    path('item/<str:pk>/delete/', views.delete_item, name="item-delete"),
    path('category/', views.category, name="category"),
    path('category/create/', views.create_category, name="category-create"),
    path('category/<str:pk>/update/', views.update_category, name="category-update"),
    path('category/<str:pk>/delete/', views.delete_category, name="category-delete"),
    path('search/', views.search, name="search"),
    path('item/<str:pk>/reuse/', views.reuse_item, name="item-reuse"),
    path('about/', views.about, name="about"),
    path('api/credits/', views.credit_list, name='credit-list'),
    path('api/credits/<str:pk>', views.credit_detail, name='credit-detail'),
    
]