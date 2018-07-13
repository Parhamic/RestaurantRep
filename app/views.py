from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .models import Employee, Item, ItemInOrder, Customer, Order, ConfigurationModel, Activity, SupplyOrder
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.core import serializers
from jalali_date import datetime2jalali, date2jalali
import datetime

def getConfig():
	cfg, created = ConfigurationModel.objects.get_or_create(id=1)
	return cfg

def getNow():
	return timezone.localtime(timezone.now())

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
			employee = authenticate(username=cd['user'], password=cd['pw']) #first, try to authenticate
			if employee is not None:
				login(request, employee)
				return redirect('/home')
			else:
				# try manually TODO:remove later
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
	activities = reversed(Activity.objects.all())
	return render(request, 'activities.html',{'activities':activities})

@login_required
def activity_view(request, id):
	activity = Activity.objects.get(id=id)
	return render(request, 'activity.html',{'activity': activity})

@login_required
def orderlist_view(request):
	orders = Order.objects.exclude(state='DV') # dont show delivered orders
	states = ['RD', 'WT', 'RJ', 'CM']
	orders = sorted(orders, key=lambda x: states.index(x.state)) # sort the orders by their states
	return render(request, 'orderlist.html', {'orders':orders, 'orderStartFrom':-getConfig().firstOrderIDToday})

@login_required
def editmenu_view(request):
	if request.method == 'POST':
		response = {}
		item, created = Item.objects.get_or_create(name=request.POST['itemName'])
		if request.POST['remove'] == 'true':
			item.delete()
		else:
			item.name = request.POST['newName']
			item.price = request.POST['itemPrice']
			item.inMenu = (request.POST['inMenu'] == 'true')
			item.save()
		response['succeed'] = 'true'
		return JsonResponse(response)

	items = Item.objects.all()
	return render(request, 'editmenu.html', {'items':items})

# AJAX Views
@login_required
def handle_jobtime(request):
	if request.method != 'POST':
		return JsonResponse({}) # handle nothing
	employee = request.user
	response = {}
	if employee.workBegan is None:
		employee.workBegan = getNow()
		employee.save()
		response['work'] = 1
	else:
		Activity.objects.create(type='گزارش کارمند',
								title=' ساعت کاری آقا/خانم '+employee.first_name + ' ' + employee.last_name,
								description='در تاریخ ' + date2jalali(getNow().date()).strftime('%y/%m/%d') + 'آقا/خانم '+employee.first_name + ' ' + employee.last_name + 'از ساعت '+employee.workBegan.strftime('%H:%M') + ' تا ساعت '+ getNow().strftime('%H:%M') + ' مشغول به کار بودند.',
								moneyTrade=0)
		employee.workBegan = None
		employee.save()
		response['work'] = 0
	return JsonResponse(response)
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
				desc += item.item.name + "   " + str(item.number) + '\n'
				totalPrice += item.item.price*item.number

			Activity.objects.create(type='فروش',
									title='فاکتور فروش شماره '+str(order.id),
									description=desc,
									moneyTrade=totalPrice)

		response['succeed'] = 'true'
	return JsonResponse(response)

@login_required
def customers_view(request):
	if request.method == 'POST':
		response = {}
		customer = Customer.objects.get(name=request.POST['customer'])
		if request.POST['action'] == 'change':
			customer.isVIP = (request.POST['isVIP'] == 'true')
			customer.save()
		elif request.POST['action'] == 'remove':
			customer.delete()
			response['succeed'] = 'true'
		return JsonResponse(response)
	customers = Customer.objects.all()
	return render(request, 'customers.html',{'customers':customers})

@login_required
def supply_order_view(request):
	if request.method == 'POST':
		name = request.POST['supply_name']
		amount = request.POST['supply_amount']
		SupplyOrder.objects.create(name=name, amount=amount)
	return render(request, 'supply_order.html')

@login_required
def supply_list_view(request):
	if request.method == 'POST':
		id = request.POST['supply_id']
		supply = SupplyOrder.objects.get(id=id)
		supply.price = request.POST['supply_price']
		supply.save()

	supplies = SupplyOrder.objects.all()
	return render(request, 'supply_list.html', {'supplies':supplies})

@login_required
def employee_view(request):
	if request.method == 'POST':
		response = {}
		action = request.POST['action']
		if action == 'remove':
			Employee.objects.get(username=request.POST['employee_name']).delete()
			response['succeed'] = 'true'
		elif action == 'changeSalary':
			employee = Employee.objects.get(username=request.POST['employee_name'])
			if request.POST['salary']:
				employee.salary = request.POST['salary']
			if request.POST['workStart']:
				employee.workStart = request.POST['workStart']
			else:
				employee.workStart = None
			if request.POST['workEnd']:
				employee.workEnd = request.POST['workEnd']
			else:
				employee.workEnd = None
			employee.save()
		elif action == 'add':
			fullName = request.POST['employee_name']
			employee = Employee.objects.create(username=fullName,
												first_name=fullName.split(' ')[0],
												last_name=''.join(x + ' ' for x in fullName.split(' ')[1:]),
												salary=request.POST['employee_salary'],
												jobTitle=request.POST['employee_job_title'],
												workStart=request.POST['employee_work_start'],
												workEnd=request.POST['employee_work_end']
												)
			permissions = request.POST['employee_perms']
			perm_names = Employee.Meta.permissions
			i = 0
			for perm in permissions:
				employee.user_permissions.add(Permission.objects.get(name=perm_names[i][0]))
				i += 1
			employee.save()
			response['succeed'] = 'true'

		return JsonResponse(response)

	employees = Employee.objects.all()
	return render(request, 'employee.html',{'employees':employees})


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
		if cfg.lastOrderDate == None or order.orderTime.date() > cfg.lastOrderDate.date(): #TODO: reset orders' id every day
			cfg.firstOrderIDToday = order.id - 1
		cfg.lastOrderDate = order.orderTime
		cfg.save()

		response = {'succeed':'true'}
		return JsonResponse(response)

	customers = Customer.objects.all()
	customers = serializers.serialize("json", customers)
	items = Item.objects.filter(inMenu=True)
	return render(request, 'order.html', {'items':items, 'customers':customers})
