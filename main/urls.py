from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.user_register, name="register"),
    path('login', views.user_login, name="login"),
    path('logout', views.user_logout, name="logout"),
    path('add_warehouse', views.add_warehouse, name="add_warehouse"),
    path('warehouse/<int:warehouse_id>/items/', views.items_list, name="items_list"),
    path('warehouse/<int:warehouse_id>/items/add/', views.add_item, name="add_item"),
    path('warehouse/<int:warehouse_id>/items/delete/<int:item_id>/', views.delete_item, name="delete_item"),
    path('warehouse/<int:warehouse_id>/items/edit/<int:item_id>/', views.edit_item, name="edit_item"),
]