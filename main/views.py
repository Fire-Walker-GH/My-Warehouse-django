from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            login(request, user)  # Автоматически входим после регистрации
            return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = UserCreationForm()  # Пустая форма для GET-запроса
    return render(request, 'main/register.html', {'form': form})