"""Restaurant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('home/', views.home_view),
    path('logout/', views.logout_view, name='logout'),
    path('orderlist/', views.orderlist_view, name='orderlist'),
    path('activities/', views.activities_view, name='activities'),
    path('editmenu/', views.editmenu_view, name='editmenu'),
    path('customers/', views.customers_view, name='customers'),
    path('supply_order/', views.supply_order_view, name='supply_order'),
    path('supply_list/', views.supply_list_view, name='supply_list'),
    path('employee/', views.employee_view, name='employee'),
    path('activity/<int:id>', views.activity_view, name='activity'),

    # ajax views
    path('order/', views.order_view, name='order'),
    path('handle_jobtime/', views.handle_jobtime, name='handlejobtime'),
    path('order_change/', views.order_change_view, name='order_state_change'),
]
