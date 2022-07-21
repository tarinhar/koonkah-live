from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
import os
from .models import Category, Item, Reuse, Station, User, Credit
from .forms import ItemForm, ReuseForm, CategoryForm

from .serializers import CreditSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


@api_view(['GET'])
def credit_list(request):
    if request.method == 'GET':
        credit = Credit.objects.all()
        serializer = CreditSerializer(credit, many=True)
        return JsonResponse(serializer.data, safe=False)

    # elif request.method == 'POST':
    #     serializer = CreditSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    #     return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def credit_detail(request, pk):
    user = User.objects.get(employee_id=pk)
    try:
        credit = Credit.objects.get(user=user)
    except Credit.DoesNotExist:
        return JsonResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CreditSerializer(credit)
        return JsonResponse(serializer.data)


def home(request):
    items = Item.objects.filter().order_by('-updated', '-created')[0:4]
    context = {'items': items}
    return render(request, 'base/index.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        # try:
        #     user = User.objects.get(username=username)
        #     print(user)
        # except:
        #     messages.error(request, 'Incorrect username or password.')

        if user is not None:
            if user.is_active:
                login(request, user)

                if request.POST.get('remember') == False:
                    request.session.set_expiry(0)
                # print('Already login to ', user)
                return redirect('home')
            else:
                messages.error(
                    request, 'Your account is inactive. Please contact your administrator.')
        else:
            messages.error(request, 'Incorrect username or password.')

    context = {}
    return render(request, 'base/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('home')


def registerPage(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name').lower()
        last_name = request.POST.get('last_name').lower()
        username = request.POST.get('username').lower()
        employee_id = request.POST.get('employee_id').upper()
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            messages.error(
                request, 'Username already exists, please try another one.')

        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username, first_name=first_name, last_name=last_name, employee_id=employee_id, email=email, password=password)
            credit, created = Credit.objects.get_or_create(user=user)
            messages.success(request, 'Registration completed sucessfully!')
            login(request, user)
            return redirect('home')

    context = {}
    return render(request, 'base/register.html', context)


def item(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    print(q)

    items = Item.objects.all()
    category = Category.objects.all()
    category_name = None

    if q != '':
        items = Item.objects.filter(Q(category__slug__exact=q))
        category = Category.objects.get(slug=q)
        category_name = category.name

    context = {'items': items,
               'category_name': category_name, 'category': category}
    return render(request, 'base/item_page.html', context)


def item_detail(request, pk):
    item = Item.objects.get(id=pk)

    try:
        item_reuse = item.reuse_set.order_by('-updated', '-created')[0]
    except IndexError:
        item_reuse = None

    return render(request, 'base/item_detail.html', {'item': item, 'item_reuse': item_reuse})


def category(request):
    categories = Category.objects.exclude(parent_category__isnull=True)
    context = {'categories': categories, }
    return render(request, 'base/category_page.html', context)


@login_required(login_url='login')
def create_category(request):
    form = CategoryForm()

    if not request.user.is_superuser:
        return HttpResponse('Sorry, you are not athorized to CREATE the object.')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category')
    return render(request, 'base/category_form.html', {'form': form})


@login_required(login_url='login')
def update_category(request, pk):
    category = Category.objects.get(id=pk)
    form = CategoryForm(instance=category)

    if not request.user.is_superuser:
        return HttpResponse('Sorry, you are not athorized to EDIT the object.')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category')
    return render(request, 'base/category_form.html', {'form': form})


@login_required(login_url='login')
def delete_category(request, pk):
    category = Category.objects.get(id=pk)

    if not request.user.is_superuser:
        return HttpResponse('Sorry, you are not athorized to DELETE the object.')

    if request.method == 'POST':
        category.delete()

        return redirect('category')
    return render(request, 'base/category_delete.html', {'obj': category})


@login_required(login_url='login')
def create_item(request):
    page = 'create'
    form = ItemForm()
    stations = Station.objects.all()
    categories = Category.objects.exclude(parent_category__isnull=True)

    if request.method == 'POST' and 'image' in request.FILES:
        # print(request.POST)
        # print(request.FILES)
        category = Category.objects.get(
            name=request.POST.get('category').lower())
        station = Station.objects.get(name=request.POST.get('station').lower())
        is_reusable = request.POST.get('reusable')
        is_reusable = True if is_reusable else False
        item = Item.objects.create(
            name=request.POST.get('name'),
            owner=request.user,
            category=category,
            station=station,
            quantity=request.POST.get('quantity'),
            size=request.POST.get('size'),
            weight=request.POST.get('weight'),
            image=request.FILES['image'],
            reusable=is_reusable,
            description=request.POST.get('description'),
        )
        credit, created = Credit.objects.get_or_create(user=request.user)
        credit.owner_point = User.objects.get(
            username=request.user.username).item_set.count()
        credit.save()
        messages.success(request, 'Your object was successfully created.')
        # return HttpResponseRedirect(reverse('item-detail', args=(item.id,)))
        return redirect('item')

    context = {'form': form, 'categories': categories, 'stations': stations}
    return render(request, 'base/item_form.html', context)


@login_required(login_url='login')
def update_item(request, pk):
    item = Item.objects.get(id=pk)
    # form = ItemForm(instance=item)
    stations = Station.objects.all()
    categories = Category.objects.exclude(parent_category__isnull=True)

    if request.user != item.owner:
        return HttpResponse('Sorry, you are not athorized to EDIT the object.')

    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        if len(request.FILES) != 0:
            if item.image is not None:
                try:
                    os.remove(item.image.path)
                except:
                    pass
            item.image = request.FILES.get('image')

        item.name = request.POST.get('name')
        item.category = Category.objects.get(
            name=request.POST.get('category').lower())
        item.station = Station.objects.get(
            name=request.POST.get('station').lower())
        item.reusable = True if request.POST.get('reusable') else False
        item.quantity = (request.POST.get('quantity'))
        item.weight = request.POST.get('weight')
        item.size = request.POST.get('size')
        item.description = request.POST.get('description')
        item.save()
        messages.success(request, 'Your object was successfully updated.')
        # return HttpResponseRedirect(reverse('item-detail', args=(item.id,)))
        return redirect('item')

    context = {'categories': categories, 'stations': stations, 'item': item}
    return render(request, 'base/item_form.html', context)


@login_required(login_url='login')
def delete_item(request, pk):
    item = Item.objects.get(id=pk)

    if request.user != item.owner:
        return HttpResponse('Sorry, you are not athorized to DELETE the object.')

    if request.method == 'POST':
        if len(item.image) > 0:
            try:
                os.remove(item.image.path)
            except:
                pass
        item.delete()
        credit, created = Credit.objects.get_or_create(user=request.user)
        credit.owner_point = User.objects.get(
            username=request.user.username).item_set.count()
        credit.save()
        messages.success(request, 'Your object was successfully deleted.')
        return redirect('item')

    context = {}
    return render(request, 'base/item_delete.html', context)


def search(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    items = Item.objects.filter(
        Q(category__name__icontains=q) |
        Q(name__icontains=q) |
        Q(owner__first_name__icontains=q) |
        Q(category__name_th__icontains=q)
    )

    item_count = items.count()

    context = {'items': items, 'item_count': item_count, 'text': q}

    return render(request, 'base/search_page.html', context)


@login_required(login_url='login')
def reuse_item(request, pk):
    item = Item.objects.get(id=pk)
    form = ReuseForm(instance=item)
    # print(item)
    # print(form)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity')),
        weight = float(request.POST.get('weight'))
        print('quantity ', quantity, type(quantity))
        print('weight ', weight, type(weight))

        Reuse.objects.create(
            item=item,
            user=request.user,
            quantity=quantity[0],
            weight=weight
        )
        credit, created = Credit.objects.get_or_create(user=request.user)
        credit.reuse_point = User.objects.get(
            username=request.user.username).reuse_set.count()
        credit.save()
        messages.success(request, 'Your object was successfully REUSED.')
        # messages.info(request, 'Pending REUSE Approval.')
        return redirect('item')

    context = {'item': item, 'form': form}
    return render(request, 'base/reuse_page.html', context)


@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    items = Item.objects.filter(owner=user)
    reuses = Reuse.objects.filter(user=user)
    total_score = items.count() + reuses.count()

    context = {'items': items, 'user': user,
               'reuses': reuses, 'total_score': total_score}
    return render(request, 'base/user-profile.html', context)


def about(request):
    return render(request, 'base/about.html')

# form = ItemForm(request.POST, request.FILES)
# if form.is_valid():
#     item = form.save(commit=False)
#     item.owner = request.user
#     item.save()
