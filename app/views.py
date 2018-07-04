from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .models import Employee, Item, ItemInOrder, Customer, Order, ConfigurationModel, Activity
from django.urls import reverse_lazy
from django.http import JsonResponse
import datetime

def getConfig():
	cfg, created = ConfigurationModel.objects.get_or_create(id=1)
	return cfg

def validStateChange(state1, state2):
	if state1 == state2:
		return False
	validChangeDic = {
		'WT': ['RJ', 'CM'],
		'CM': ['RD', 'DV'],
		'RD': ['DV']
	}

	if state1 in validChangeDic and state2 in validChangeDic[state1]:
		return True
	return False

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
	return render(request, 'home.html')

@login_required
def activities_view(request):
	return render(request, 'activities.html')

@login_required
def activity_view(request):
	return render(request, 'activity.html')

@login_required
def order_change_view(request):
	if request.method != 'POST':
		return JsonResponse({}) # handle nothing

	response = {}

	order = Order.objects.get(id=request.POST['order_id'])
	if request.POST['state'] == 'RM': # remove this order
		order.delete()
		response['succeed'] = 'true'
	elif validStateChange(order.state, request.POST['state']): # Can we change the state?
		order.state = request.POST['state']
		order.save()

		if request.POST['state'] == 'CM': # add activity
			totalPrice = 0
			desc = 'فاکتور فروش شماره '+ str(order.id) + '\n\n'
			for item in order.items.all():
				desc += item.item.name + "   " + str(item.number)
				totalPrice += item.item.price*item.number

			Activity.objects.create(type='فروش',
									title='فاکتور فروش شماره '+str(order.id),
									description=desc,
									moneyTrade=totalPrice)

		response['succeed'] = 'true'
	return JsonResponse(response)

@login_required
def orderlist_view(request):
	orders = Order.objects.exclude(state='DV') # dont show delivered orders
	states = ['RD', 'WT', 'RJ', 'CM']
	orders = sorted(orders, key=lambda x: states.index(x.state)) # sort the orders by their states
	return render(request, 'orderlist.html', {'orders':orders, 'orderStartFrom':-getConfig().firstOrderIDToday})

@login_required
def order_view(request):
	if request.method == 'POST':
		items = request.POST['items'].split(',')
		counts = request.POST['counts'].split(',')

		# create the order
		order = Order.objects.create()

		# set the orderer
		if request.POST['customer'] != '':
			customer, created = Customer.objects.get_or_create(name=request.POST['customer'])
			order.orderer = customer
			order.save()

		i = 0
		for itemName in items:
			if itemName == '':
				continue
			item = Item.objects.get(name=itemName)
			itemInOrder = ItemInOrder.objects.create(item=item, order=order, number=int(counts[i]))
			i += 1

		cfg = getConfig()
		if cfg.lastOrderDate == None or order.orderTime.date() > cfg.lastOrderDate.date(): #TODO: reset orders every day
			cfg.firstOrderIDToday = order.id - 1
		cfg.lastOrderDate = order.orderTime
		cfg.save()

		response = {'succeed':'true'}
		return JsonResponse(response)


	items = Item.objects.filter(inMenu=True)
	return render(request, 'order.html', {'items':items})
