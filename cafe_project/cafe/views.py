from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TableReservationForm
from django.contrib import messages
from .models import TableReservation,Shakes
from collections import defaultdict
from datetime import datetime
from django.http import HttpResponse
from cafe.models import Cart, CartItem, Product,CoolDrinks
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

         # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register') 
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  # Replace 'home' with your app's home page
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def home(request):
    return render(request,"home.html")


@login_required
def reserve_table(request):
    # Check if the user has an existing reservation
    if request.user.is_authenticated:
        existing_reservation = TableReservation.objects.filter(user=request.user).first()

        if existing_reservation:
            # Check if the existing reservation has expired
            if existing_reservation.is_expired():
                existing_reservation.delete()  # Remove expired reservation
                messages.error(request, "Your previous reservation has expired. Please reserve again.")
                return redirect('reserve_table')

            # If not expired, inform the user
            messages.info(request, "You already have a reservation. No need to reserve again.")
            return redirect('menu')

    # Handle new reservation
    if request.method == 'POST':
        form = TableReservationForm(request.POST)
        if form.is_valid():
            table_number = form.cleaned_data['table_number']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # Check if the table is already reserved
            existing_reservation = TableReservation.objects.filter(
                table_number=table_number,
                date=date,
                time=time
            ).first()

            if existing_reservation:
                messages.error(request, f"Table {table_number} is already reserved at this time.")
                return redirect('reserve_table')

            # Save the reservation and associate with the user
            reservation = form.save(commit=False)
            if request.user.is_authenticated:
                reservation.user = request.user
            reservation.save()

            messages.success(request, "Table reserved successfully!")
            return redirect('menu')
    else:
        form = TableReservationForm()

    return render(request, 'reserve_table.html', {'form': form})


def menus(request):
    return render(request,'menus.html')

def menu(request):
    m=Product.objects.all()
    return render(request,'menu.html',{'m':m})

def ProductDetail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(price__gte=product.price - 100, price__lte=product.price + 100).exclude(id=id)    
    return render(request, 'product.html', {'product': product, 'related_products': related_products})

def cooldrinks(request):
    c=CoolDrinks.objects.all()
    return render(request,'cooldrinks.html',{'c':c})

def cooldrinks_details(request, id):
    cd = get_object_or_404(CoolDrinks, id=id)
    
    # Fetch related cool drinks (example: drinks within the same price range)
    related_cool_drinks = CoolDrinks.objects.filter(price__gte=cd.price - 100, price__lte=cd.price + 100).exclude(id=id)
    
    return render(request, 'product.html', {'cd': cd, 'related_cool_drinks': related_cool_drinks})
def ShakeS(request):
    s=Shakes.objects.all()
    return render(request,'shakes.html',{'s':s})

def Shakes_details(request,id):
    sd=get_object_or_404(Shakes,id=id)
    related_shakes = Shakes.objects.filter(price__gte=sd.price - 100, price__lte=sd.price + 100).exclude(id=id)
    return render(request,'product.html',{'sd':sd})


@login_required
# Adding a product to the cart
@login_required
def cart(request, product_id=None, cool_drink_id=None,shakes_id=None):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to add items to the cart.")
        return redirect('login')

    # Check if the user has a table reservation
    reservation_exists = TableReservation.objects.filter(user=request.user).exists()
    if not reservation_exists:
        messages.error(request, "You need to reserve a table before adding products to the cart.")
        return redirect('reserve_table')

    cart, created = Cart.objects.get_or_create(user=request.user)

    # Handle adding a product to the cart
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Handle adding a cool drink to the cart
    elif cool_drink_id:
        cool_drink = get_object_or_404(CoolDrinks, id=cool_drink_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, cool_drink=cool_drink)

    elif shakes_id:
        shake=get_object_or_404(Shakes,id=shakes_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, shake=shake)

    # If the item already exists, increment its quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"'{cart_item.product.title if cart_item.product else cart_item.cool_drink.title}' added to your cart.")
    return redirect('cart')


# Viewing the cart
def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to view your cart.")
        return redirect('login')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        items = []
        total = 0
    else:
        items = cart.items.all()
        total = sum(item.total_price() for item in items)
    
    return render(request, 'cart.html', {'cart_items': items, 'total': total})


def DeleteItem(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to remove items.")
        return redirect('login')

    # Get the cart item for the authenticated user
    cart_item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    cart_item.delete()

    messages.success(request, "Item removed from the cart.")
    return redirect('cart')



# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def search_view(request):
    query = request.GET.get('q')  # Get the search term from the query parameter
    results = Product.objects.filter(    Q(title__icontains=query)  | Q(price__icontains=query)
    ) if query else []
    return render(request, 'search.html', {'query': query, 'results': results})






def cart_count_processor(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()
    return {'cart_count': cart_count}


