from django import forms
from .models import Item 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль',
                               min_length=6, 
                               max_length=12,
                               widget=forms.PasswordInput)

class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Логин', 
                               help_text='*Не менее 2 символов и не более 30', 
                               min_length=2, 
                               max_length=30, )
    
    password1 = forms.CharField(label='Пароль', 
                                help_text='*Не менее 6 символов и не более 12', 
                                min_length=6, 
                                max_length=12,
                                widget=forms.PasswordInput)
    
    password2 = forms.CharField(label='Подтверждение пароля', 
                                help_text='*Повторите пароль', 
                                min_length=6, 
                                max_length=12,
                                widget=forms.PasswordInput)
    
    error_messages = {
        'password_mismatch': 'Пароли не совпадают!',
    }