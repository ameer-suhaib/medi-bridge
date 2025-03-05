from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout,authenticate,login
from django.contrib.auth.models import Group
from .decorator import unauthenticated_user

from .forms import CreateUserForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
#views


@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'Admin':
                    return redirect("admin_dashboard")
                elif group == 'Patient':
                    return redirect("patient_dashboard")
                    # return render(request, "login.html")
                else:
                    return redirect('doctor_dashboard')
    return render(request, "login.html")


@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            print('loooo')
            user = form.save()
            group = Group.objects.get(name = 'Patient')
            user.groups.add(group)
            messages.info(request, "Registration Success!!.")
            return redirect(reverse("login"))
    context = {"form":form}
    return render(request, "register.html",context) 


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url='login')
def listing(request):
    return render(request,"listing.html")






# Create your views here.


# def home(request):
#     customers = Customers.objects.all()
#     orders = Orders.objects.all()
#     customer_count = customers.count()
#     order_count = orders.count()

#     context = {
#         "customers": customers,
#         "orders": orders,
#         "customer_count": customer_count,
#         "order_count": order_count
#     }
#     return render(request, "dashboard.html", context)



# def admin_dashboard(request):
#     # Get counts for statistics cards
#     total_customers = Customers.objects.count()
#     total_products = Products.objects.count()
#     total_orders = Orders.objects.count()
    
#     # Calculate total revenue from orders
#     total_revenue = sum(order.product.price for order in Orders.objects.select_related('product').all())

#     # Get recent activities (orders)
#     recent_activities = []
#     recent_orders = Orders.objects.select_related('customer', 'product').order_by('-created_at')[:10]
    
#     for order in recent_orders:
#         status_color = {
#             'Pending': 'warning',
#             'Out of Delivary': 'info',
#             'Delivered': 'success'
#         }.get(order.status, 'secondary')

#         recent_activities.append({
#             'timestamp': order.created_at,
#             'description': f'Order placed for {order.product.name}',
#             'user': order.customer.name,
#             'status': order.status,
#             'status_color': status_color
#         })

#     context = {
#         'total_customers': total_customers,
#         'total_products': total_products,
#         'total_orders': total_orders,
#         'total_revenue': "{:.2f}".format(total_revenue),
#         'recent_activities': recent_activities,
#     }

#     return render(request, "admin_dashboard.html", context)

