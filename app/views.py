from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

def login_view(request):
	if request.user.is_authenticated:
		return redirect('/home')

	error = ''
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			employee = authenticate(username=cd['user'], password=cd['pw'])
			if employee is not None:
				login(request, employee)
				return redirect('/home')
			else:
				error = 'UserPass'

			return render(request, 'login.html', {'form':form, 'error':error})

		error = 'Form'
		return render(request, 'login.html', {'form':form, 'error':error})

	form = LoginForm()
	return render(request, 'login.html', {'form':form, 'error':error})


@login_required
def home_view(request):
	print(request.user.username)
	return render(request, 'home.html')
