from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .models import Employee, Item
from django.urls import reverse_lazy

def login_view(request):
	if request.user.is_authenticated:
		return redirect('/home')

	error = ''
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			employee = authenticate(username=cd['user'], password=cd['pw']) #first try to authenticate
			if employee is not None:
				login(request, employee)
				return redirect('/home')
			else:
				# try manually
				employee = Employee.objects.filter(username=cd['user'], password=cd['pw'])
				if employee.count() != 0:
					login(request, employee[0])
					return redirect('/home')
				else:
					error = 'UserPass'

			return render(request, 'login.html', {'form':form, 'error':error})

		error = 'Form'
		return render(request, 'login.html', {'form':form, 'error':error})

	form = LoginForm()
	return render(request, 'login.html', {'form':form, 'error':error})

@login_required
def logout_view(request):
	logout(request)
	return redirect(reverse_lazy('login'))

@login_required
def home_view(request):
	print(request.user.username)
	return render(request, 'home.html')

@login_required
def order_view(request):
	items = Item.objects.filter(in_menu=True)
	return render(request, 'order.html', {'items':items})
