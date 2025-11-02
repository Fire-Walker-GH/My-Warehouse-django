from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from .models import Warehouse, Item
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        user_warehouses = Warehouse.objects.filter(user_id=request.user.id)
    else:
        user_warehouses = None

    return render(request, 'main/home.html', {'user_warehouses': user_warehouses})

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            login(request, user)  # Автоматически входим после регистрации
            return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = UserCreationForm()  # Пустая форма для GET-запроса
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def user_logout(request):
     logout(request)
     return redirect('home')
     

@login_required  # Если нужно, чтобы только авторизованные пользователи могли добавлять склады
def add_warehouse(request):
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('warehouse_name')
        address = request.POST.get('address')
        user_id = request.user.id  # Получаем ID текущего пользователя

        # Создаем и сохраняем новый склад в базе данных
        Warehouse.objects.create(
            name=name,
            address=address,
            user_id=user_id
        )
        return redirect('home')  # Перенаправляем на страницу со списком складов

    return render(request, 'main/add_warehouse.html')


def items_list(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    if warehouse.user != request.user:
        raise PermissionDenied("У вас нет доступа к этому складу")
    
    items = Item.objects.filter(warehouse=warehouse)
    return render(request, 'main/items_list.html', {'warehouse': warehouse, 'items': items})
