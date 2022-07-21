from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Category, Reuse, Item, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email', 'password1', 'password2']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'employee_id', 'avatar']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
        exclude = ['is_active', 'status', 'label']


class ReuseForm(ModelForm):
    class Meta:
        model = Reuse
        fields = '__all__'


# class StationForm(ModelForm):
#     class Meta:
#         model = Station
#         fields = '__all__'
