from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Warehouse, Item
from django.contrib.auth.decorators import login_required
from .forms import ItemForm
from django.urls import reverse



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
    
    items = Item.objects.filter(warehouse=warehouse)
    return render(request, 'main/items_list.html', {'warehouse': warehouse, 'items': items})

def items_list(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    items = warehouse.items.all()

    if request.method == 'POST':
        name = request.POST.get('item-name')
        description = request.POST.get('item-description')
        quantity = request.POST.get('item-quantity')

        if name and quantity:
            Item.objects.create(
                name=name,
                description=description,
                quantity=quantity,
                warehouse=warehouse
            )
            messages.success(request, 'Предмет успешно добавлен!')
            return redirect('items_list', warehouse_id=warehouse_id)
        else:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')

    return render(request, 'main/items_list.html', {
        'warehouse': warehouse,
        'items': items
    })

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