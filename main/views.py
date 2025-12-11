from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Warehouse, Item
from django.contrib.auth.decorators import login_required
from .forms import ItemForm, CustomAuthenticationForm
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q




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
            user = form.save()
            login(request, user)  
            return redirect('home') 
    else:
        form = UserCreationForm() 
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def user_logout(request):
     logout(request)
     return redirect('home')
     

@login_required 
def add_warehouse(request):
    if request.method == 'POST':
        name = request.POST.get('warehouse_name')
        address = request.POST.get('address')
        user_id = request.user.id 

        Warehouse.objects.create(
            name=name,
            address=address,
            user_id=user_id
        )
        return redirect('home') 

    return render(request, 'main/add_warehouse.html')


def items_list(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    if warehouse.user != request.user:
        raise PermissionDenied("У вас нет доступа к этому складу")
    
    # 1. Получаем базовый QuerySet предметов для склада
    all_items = Item.objects.filter(warehouse=warehouse)
    
    # 2. ЛОГИКА ПОИСКА
    search_query = request.GET.get('q')
    if search_query:
        # Фильтруем QuerySet по названию, используя icontains (регистронезависимый поиск)
        all_items = all_items.filter(name__icontains=search_query)
        
    # Сортируем QuerySet (важно делать это после фильтрации)
    all_items = all_items.order_by('name')
    
    # 3. ЛОГИКА ПАГИНАЦИИ
    items_per_page = 4 # 4 предмета на страницу
    paginator = Paginator(all_items, items_per_page)
    
    # Получаем номер текущей страницы из GET-параметра 'page'
    page_number = request.GET.get('page', 1)
    
    try:
        # Получаем объект Page для запрошенной страницы
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Если номер страницы не целое число, показываем первую страницу
        page_obj = paginator.page(1)
    except EmptyPage:
        # Если номер страницы вне диапазона, показываем последнюю
        page_obj = paginator.page(paginator.num_pages)
    
    # 4. КОНТЕКСТ
    context = {
        'warehouse': warehouse,
        'page_obj': page_obj, 
        'items': page_obj.object_list, 
        'search_query': search_query or '', # Передаем поисковый запрос обратно в шаблон
    }
    
    return render(request, 'main/items_list.html', context)

def add_item(request, warehouse_id):
    # Эта функция должна обрабатывать только POST-запросы
    if request.method == 'POST':
        # Используем get_object_or_404 для лучшей обработки ошибок
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        
        # Используем имена полей из формы модального окна, которую я вам предоставил (name, description, quantity)
        name = request.POST.get('name')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')

        # Базовая валидация
        if name and quantity:
            try:
                # Преобразование количества в целое число
                quantity = int(quantity)
                
                Item.objects.create(
                    name=name,
                    description=description,
                    quantity=quantity,
                    warehouse=warehouse
                )
                messages.success(request, 'Предмет успешно добавлен!')
            except ValueError:
                messages.error(request, 'Количество должно быть целым числом.')
            except Exception as e:
                messages.error(request, f'Произошла ошибка при добавлении: {e}')
        else:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля (Название и Количество).')

        # После обработки запроса всегда перенаправляем пользователя обратно на страницу списка
        return redirect('items_list', warehouse_id=warehouse_id)
    
    # Если кто-то попытается перейти по этому URL через GET-запрос, перенаправляем его
    return redirect('items_list', warehouse_id=warehouse_id)

def delete_item(request, warehouse_id, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('items_list', warehouse_id=warehouse_id)

def edit_item(request, warehouse_id, item_id):
    """
    Handles the editing of an existing Item.
    Requires both warehouse_id and item_id to ensure the item belongs to the warehouse.
    """
    item = get_object_or_404(Item, pk=item_id, warehouse_id=warehouse_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        
        if form.is_valid():
            form.save()
            return redirect(reverse('items_list', args=[warehouse_id]))
    else:

        form = ItemForm(instance=item)
    return redirect(reverse('items_list', args=[warehouse_id]))