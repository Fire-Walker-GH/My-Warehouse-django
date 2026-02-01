from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Warehouse, Item, WarehouseAccess
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import ItemForm, CustomAuthenticationForm, CustomRegistrationForm
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
import json


def home(request):
    if request.user.is_authenticated:
        user_warehouses = Warehouse.objects.filter(user=request.user)
        for warehouse in user_warehouses:
            accesses = WarehouseAccess.objects.filter(warehouse=warehouse).select_related('user')
            users_list = [
                {'id': acc.user.id, 'username': acc.user.username, 'role': acc.get_role_display()}
                for acc in accesses
            ]
            warehouse.shared_users_json = json.dumps(users_list)
            warehouse.shared_count = len(users_list)
        
        shared_accesses = WarehouseAccess.objects.filter(user=request.user).select_related('warehouse', 'warehouse__user')
        shared_warehouses = []
        for access in shared_accesses:
            shared_warehouses.append({
                'warehouse': access.warehouse,
                'role': access.get_role_display(),
                'owner': access.warehouse.user.username
            })
            
        return render(request, 'main/home.html', {
            'user_warehouses': user_warehouses,
            'shared_warehouses': shared_warehouses
        })
    return render(request, 'main/home.html')

def user_register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home') 
    else:
        form = CustomRegistrationForm() 
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

def delete_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id, user_id=request.user.id)
    
    if request.method == 'POST':
        warehouse.delete()
        return redirect('home') 
    
    return redirect('home') 

@login_required
@require_POST
def add_shared_user_to_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    if warehouse.user != request.user:
        return JsonResponse({"status": "error", "message": "У вас нет прав для изменения доступа."}, status=403)

    username = request.POST.get("login")
    role = request.POST.get("role")

    if not username:
        return JsonResponse({"status": "error", "message": "Логин обязателен."}, status=400)

    try:
        target_user = User.objects.get(username=username)
        
        if target_user == request.user:
            return JsonResponse({"status": "error", "message": "Нельзя добавить владельца."}, status=400)
        
        WarehouseAccess.objects.update_or_create(
            warehouse=warehouse,
            user=target_user,
            defaults={"role": role}
        )
        return JsonResponse({"status": "success", "message": f"Пользователь {username} добавлен."})
            
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Пользователь не найден."}, status=404)
    
@login_required
@require_POST
def remove_shared_user(request, warehouse_id, user_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    
 
    if warehouse.user != request.user:
        return JsonResponse({"status": "error", "message": "У вас нет прав."}, status=403)
    
    
    WarehouseAccess.objects.filter(warehouse=warehouse, user_id=user_id).delete()
    
    return JsonResponse({"status": "success"})


def items_list(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    if warehouse.user != request.user:
        raise PermissionDenied("У вас нет доступа к этому складу")
    
    all_items = Item.objects.filter(warehouse=warehouse)
    
    search_query = request.GET.get('q')
    if search_query:
        all_items = all_items.filter(name__icontains=search_query)
        
    all_items = all_items.order_by('name')
    
    items_per_page = 4
    paginator = Paginator(all_items, items_per_page)
    
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'warehouse': warehouse,
        'page_obj': page_obj, 
        'items': page_obj.object_list, 
        'search_query': search_query or '', 
    }
    
    return render(request, 'main/items_list.html', context)

def add_item(request, warehouse_id):
    if request.method == 'POST':
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        
        name = request.POST.get('name')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')

        if name and quantity:
            try:
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

        return redirect('items_list', warehouse_id=warehouse_id)
    
    return redirect('items_list', warehouse_id=warehouse_id)

def delete_item(request, warehouse_id, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('items_list', warehouse_id=warehouse_id)

def edit_item(request, warehouse_id, item_id):
    item = get_object_or_404(Item, pk=item_id, warehouse_id=warehouse_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        
        if form.is_valid():
            form.save()
            return redirect(reverse('items_list', args=[warehouse_id]))
    else:

        form = ItemForm(instance=item)
    return redirect(reverse('items_list', args=[warehouse_id]))