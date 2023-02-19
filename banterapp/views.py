from django.shortcuts import render, redirect, reverse

from django.core.mail import BadHeaderError, send_mail

from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.forms import UserCreationForm

from django.core.mail import EmailMessage

from django.conf import settings

from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives

from .models import *

from .forms import *

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required

from django.utils.html import strip_tags

import datetime
import json
import requests
import uuid
import os

# Create your views here.

def index(request):
	return render(request, 'banterapp/index.html')


def plan(request):
	return render(request, 'banterapp/index.html')

def otherpayment(request):
    return render(request, 'banterapp/otherpayment.html')


def about(request):
	return render(request, 'banterapp/about.html')

def career(request):
	return render(request, 'banterapp/index.html')

def faq(request):
	return render(request, 'banterapp/faq.html')

def signin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	else:
		if request.method == "POST":
			username= request.POST.get('username')
			password= request.POST.get('password')

			user= authenticate(request, username=username, password=password)

			if user is not None:
				email= User.objects.get(username=username).email
				print(email)
				template= render_to_string('banterapp/loginAlert.html', {'name':username})
				plain_message= strip_tags(template)
				email_message= EmailMultiAlternatives(
					'Login alert on your account!',
					plain_message,
					settings.EMAIL_HOST_USER,
					[email]

					)
				email_message.attach_alternative(template, 'text/html')
				email_message.send()
				login(request, user)
				return redirect('dashboard')

			else:
				messages.error(request, "username or password is incorrect")

	context={}
	return render(request, 'banterapp/signin.html')


def privacy(request):
	return render(request, 'banterapp/privacy.html')

def main_view(request, *args, **kwargs):
	code= str(kwargs.get('ref_code'))

	try:
		client = Client.objects.get(code=code)
		request.session['ref_client'] = client.id
		print('id', client.id)
	except:
		pass
	print(request.session.get_expiry_age())

	return render(request, 'banterapp/main.html')


def signup(request):
	user_check = request.user.is_authenticated
	if user_check:
		return redirect('dashboard')
	client_id= request.session.get('ref_client')
	print('client_id', client_id)
	form = CreateUserForm(request.POST or None)
	if form.is_valid():
		if client_id is not None:
			recommended_by_client= Client.objects.get(id=client_id)
			recommended_by_client_email= recommended_by_client.email_address
			recommended_by_client_name= recommended_by_client.first_name
			username=form.cleaned_data.get('username')

			instance= form.save()
			registered_user= User.objects.get(id=instance.id)
			registered_client= Client.objects.get(user=registered_user)
			registered_client.recommended_by= recommended_by_client.user
			referral_template= render_to_string('banterapp/referalsignupmail.html', {'name':recommended_by_client_name, 'refereed':username})
			plain_message= strip_tags(referral_template)
			email_message= EmailMultiAlternatives(
				'You refered a user using your referral link',
				plain_message,
				settings.EMAIL_HOST_USER,
				[recommended_by_client_email],
				)
			email_message.attach_alternative(referral_template, 'text/html')
			email_message.send()
			registered_client.save()

		else:
			form.save()

		username=form.cleaned_data.get('username')
		password= form.cleaned_data.get('password1')
		password_reminder= password[:1]
		password_reminder_two= password[-1:]
		email= form.cleaned_data.get('email')
		template= render_to_string('banterapp/welcomeEmail.html', {'name':username, 'password':password})
		plain_message= strip_tags(template)
		email_message= EmailMultiAlternatives(
			'Welcome on board to R.M Cooper Hoysteds!',
			plain_message,
			settings.EMAIL_HOST_USER,
			[email],

			)
		email_message.attach_alternative(template, 'text/html')
		email_message.send()
		second_template= render_to_string('banterapp/securityEmail.html', {'name': username, 'password_reminder':password_reminder, 'password_reminder_two':password_reminder_two})
		second_plain_message= strip_tags(second_template)
		second_email_message= EmailMultiAlternatives(
			"Stay updated and discover more with Cooper Hoysteds!",
			second_plain_message,
			settings.EMAIL_HOST_USER,
			[email]
			)
		second_email_message.attach_alternative(second_template, 'text/html')
		second_email_message.send()
		try:
			send_mail(username, "A client with username: {} has just signed up on your site with email: {}".format(username, email),settings.EMAIL_HOST_USER, ['support@cooperhoystedsinvestmentservice.com'])
		except BadHeaderError:
			return HttpResponse("Your account has been created but you can't login at this time. please, try to login later")
		user= authenticate(username=username, password=password)
		login(request, user)
		return redirect('dashboard')
	context={'form':form}
	return render(request, 'banterapp/signup.html', context)

@login_required(login_url='signin')
def dashboard(request):
	if request.user.is_staff:
		return redirect('admindashboard')
	else:
		client= request.user.client
		client_firstname= request.user.username
		client_email= request.user.email
		client_pk= client.pk
		client_deposit= client.deposit
		client_profit= client.profit
		client_bal= client.balance
		client_withdrawal= client.withdrawal
		client_date_joined= client.created
		client_code= client.code
		client.save()
	context={'client': client, 'client_deposit':client_deposit, 'client_bal':client_bal,'client_profit':client_profit, 'client_date_joined':client_date_joined,
	'client_withdrawal':client_withdrawal, 'client_code':client_code }
	return render(request, 'banterapp/dashboard.html', context)

@login_required(login_url='signin')
@staff_member_required
def admindashboard(request):
	clients= Client.objects.all()
	withdrawal_requests= Withdrawal_request.objects.all()
	transactions= Transaction.objects.all()
	clients_total= clients.count()
	withdrawal_requests_total= withdrawal_requests.count()
	transactions_total= transactions.count()
	payment= Payment_id.objects.all()
	context={'clients_total':clients_total, 'withdrawal_requests_total':withdrawal_requests_total, 'transactions_total':transactions_total,
	"clients":clients, 'payment':payment  }
	return render(request, 'banterapp/adminpage.html', context)


def terms(request):
	return render(request, 'banterapp/terms.html')


def realestate(request):
	return render(request, 'banterapp/index.html')


def crypto(request):
	return render(request, 'banterapp/index.html')


def forex(request):
	return render(request, 'banterapp/index.html')


def nft(request):
	return render(request, 'banterapp/index.html')


def contact(request):
	return render(request, 'banterapp/index.html')


def stocks(request):
	return render(request, 'banterapp/index.html')


def agriculture(request):
	return render(request, 'banterapp/index.html')


def gold(request):
	return render(request, 'banterapp/index.html')


def retirement(request):
	return render(request, 'banterapp/index.html')

@login_required(login_url='signin')
def deposit(request):
	if request.method=='POST':
		client= request.user.client
		client_name= client.first_name
		client_email= client.email_address
		#post data to create invoice for payment
		price_amount= request.POST.get('price_amount')
		price_currency= "usd"
		pay_currency= request.POST.get('pay_currency')
		roi= request.Post.get('Portfolio')
		order_id= 'Cooper Hoysteds'
		order_description= "This is a plan subscription"
		if price_amount and pay_currency:
			# Api's url link
			url= 'https://api.nowpayments.io/v1/invoice'
			payload=json.dumps({
				"price_amount": price_amount,
				"price_currency": price_currency,
				"pay_currency": pay_currency,
				"order_id": order_id,
				"order_description": order_description,
				"ipn_callback_url": "https://nowpayments.io",
				"success_url": "https://www.cooperhoystedsinvestmentservice.com/dashboard",
				#our success url will direct us to the get_payment_status view for balance top ups
				"cancel_url": "https://www.cooperhoystedsinvestmentservice.com/dashboard"
			})
			headers={'x-api-key':'NNNYVJS-M8C48DF-GRKD75C-4S3CCV3', 'Content-Type': 'application/json'}
			response= requests.request('POST', url, headers=headers, data=payload)
			res= response.json()
			print(res)
			generated_link= res["invoice_url"]
			generated_payment_id= res["id"]
			#Now get the user and add the payment ID to the database as we will be using it to know their payment status
			Payment_id.objects.create(
				client=client,
				payment_id= generated_payment_id,
				price_amount= price_amount,
				portfolio_returns=roi,
				)
			try:
				send_mail(client_name, "A client with username: {} has created a deposit request with an amount ${}".format(client_name, price_amount),settings.EMAIL_HOST_USER, ['support@cooperhoystedsinvestmentservice.com'])
			except BadHeaderError:
				pass
			return redirect(generated_link)
	context={}
	return render(request, 'banterapp/deposit.html', context)

@login_required(login_url='signin')
def withdrawal(request):
	client= request.user.client
	client_id= client.id
	client_username= request.user.username
	client_email= client.email_address
	client_deposit= client.deposit
	client_withdrawal= client.withdrawal
	minimum_withdrawal= Minimum_withdrawal.objects.all()
	maximum_withdrawal= Maximum_withdrawal.objects.all()
	for i in minimum_withdrawal:
		minimum_withdrawal_amount= i.minimum_withdrawal
	for i in maximum_withdrawal:
		maximum_withdrawal_amount= i.maximum_withdrawal
	print(client_deposit)
	client_profit= client.profit
	client_balance= client.balance
	client_info= Client.objects.filter(id=client_id)
	if request.method =='POST':
		withdrawal_option = request.POST.get('withdrawal_category')
		amount= request.POST.get('amount')
		withdrawal_address= request.POST.get('withdrawal_address')
		crypto= request.POST.get('crypto')
		if withdrawal_option == 'balance' and float(client_balance) > float(minimum_withdrawal_amount):
			client_current_balance= float(client_balance) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if float(client_current_balance) < 0 or float(client_balance) > float(maximum_withdrawal_amount):
				messages.error(request, "The amount requested is greater than your balance or you are exceeding the maximum withdrawal amount")
			else:
				client_update= client_info.update(balance=client_current_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),settings.EMAIL_HOST_USER, ['support@cooperhoystedsinvestmentservice.com'])

				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')

				return HttpResponse('Withdrawal submitted successfully')


		if withdrawal_option == 'balance' and float(client_balance)<= float(minimum_withdrawal_amount):
			messages.error(request, "Your balance is too low for this withdrawal or your request is less than the minimum withdrawal amount")

		if withdrawal_option == 'profit' and float(client_profit) > 10:
			client_profit_balance= float(client_profit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_profit_balance < 0:
				messages.error(request, "Amount requested is greater than profit")
			else:
				client_update= client_info.update(profit= client_profit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),settings.EMAIL_HOST_USER, ['support@cooperhoystedsinvestmentservice.com'])
				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')
				messages.success(request, "Your withdrawal was successfully completed")

		if withdrawal_option == 'profit' and float(client_profit) <=10:
			messages.error(request, "Your profit is too low for this withdrawal" )
	context={}
	return render(request, 'banterapp/withdrawal.html', context)

@login_required(login_url='signin')
def history(request):
	client= request.user.client
	transaction= ''
	bonus= ''
	payment_id= ''
	withdrawal= ''
	total_transaction=''
	try:
		withdrawal= Withdrawal_request.objects.filter(client=client)
		transaction= Transaction.objects.filter(client=client)
		bonus= Bonus.objects.filter(client=client)
		payment_id= Payment_id.objects.filter(client=client)
		total_transaction= float(transaction.count()) + float(bonus.count()) + float(payment_id.count())
	except:
		pass
	context={'withdrawal':withdrawal, 'bonus':bonus, 'payment_id':payment_id,'transaction':transaction, 'total_transaction':total_transaction }
	return render(request, 'banterapp/history.html', context)

@login_required(login_url='signin')
def myreferals(request):
    info= request.user
    client= Client.objects.get(user=info)
    ref_info= client.get_recommended_profiles()
    client_code= client.code
    context={'ref_info': ref_info, 'client_code':client_code}
    return render(request, 'banterapp/referralprofiles.html', context)

@login_required(login_url='signin')
@staff_member_required
def confirm_withdrawal(request):
	withdrawalInfo= Withdrawal_request.objects.all()
	context={'withdrawalInfo': withdrawalInfo}
	return render(request, 'banterapp/confirmwithdrawal.html', context)

@login_required(login_url='signin')
@staff_member_required
def update_withdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	template= render_to_string('banterapp/withdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your withdrawal request has been approved!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	Transaction.objects.create(
		client=client,
		transaction_type='Withdrawal',
		amount= withdrawalInfo_amount,
		status= 'Approved',
		)
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Update withdrawal')

@login_required(login_url='signin')
@staff_member_required
def decline_wihdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_info= Client.objects.filter(id=client_id)
	client_bal= client.balance
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	client_balance_reup= float(client_bal) + float(withdrawalInfo_amount)
	client_withdrawal_reup= float(client_withdrawal) - float(withdrawalInfo_amount)
	client_info_update= client_info.update(balance=client_balance_reup, withdrawal=client_withdrawal_reup)
	template= render_to_string('banterapp/declineWithdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Withdrawal request declined!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	Transaction.objects.create(
		client=client,
		transaction_type='Withdrawal',
		amount= withdrawalInfo_amount,
		status= 'Declined'
		)
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Withdrawal request declined')


@login_required(login_url='signin')
@staff_member_required
def confirm_deposit(request):
	paymentInfo= Payment_id.objects.all()
	context={'paymentInfo': paymentInfo}
	return render(request, 'banterapp/confirmdeposit.html', context)


@login_required(login_url='signin')
@staff_member_required
def update_payment(request, pk):
	payment_info= Payment_id.objects.get(id=pk)
	payment_info_id= payment_info.id
	payment_info_amount= payment_info.price_amount
	payment_info_roi= payment_info.portfolio_returns
	client_id= payment_info.client.id
	client= Client.objects.get(id=client_id)
	client_deposit= client.deposit
	client_pk= client.id
	client_name= client.first_name
	client_email= client.email_address
	print(client_deposit)
	client_info= Client.objects.filter(id=client_pk)
	newClientbal= float(payment_info_amount) + float(client_deposit)
	update_payment= client_info.update(deposit=newClientbal, running_days=0, roi=payment_info_roi)
	template= render_to_string('banterapp/confirmDepositEmail.html', {'name':client_name, 'amount':payment_info_amount})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your deposit was successful!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()

	Transaction.objects.create(
		client=client,
		transaction_type='Deposit',
		amount= payment_info_amount,
		status= 'Approved'
		)
	delete_payment_info= payment_info.delete()
	if update_payment:
		return HttpResponse('deposit confirmed successfully')
	return HttpResponse('Update payment')

@login_required(login_url='signin')
def account_settings(request):

	client= request.user.client

	form=ClientForm(instance=client)

	if request.method=='POST':
		form= ClientForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()

	context= {"form":form}
	return render(request, 'banterapp/account_settings.html', context)

@login_required(login_url='signin')
def create_bonus(request):
	form= BonusForm(request.POST or None)
	if form.is_valid():
		form.save()
		client= form.cleaned_data.get('client')
		transaction_type= form.cleaned_data.get('transaction_type')
		amount= form.cleaned_data.get('amount')
		code= form.cleaned_data.get('code')
		client_email= form.cleaned_data.get('client_email')
		message= form.cleaned_data.get('message')
		template= render_to_string('banterapp/bonusNotification.html', {'message':message, 'amount':amount, 'code':code})
		plain_message= strip_tags(template)
		emailmessage= EmailMultiAlternatives(
			"Congratulations, your bonus code has been created",
			plain_message,
			settings.EMAIL_HOST_USER,
			[client_email],
			)
		emailmessage.attach_alternative(template, 'text/html')
		emailmessage.send()
		try:
			pass
		except BadHeaderError:
			pass
		return HttpResponse('You have successfully created a Bonus for your client')
	context={'form': form}
	return render(request, 'banterapp/create_bonus.html', context)

@login_required(login_url='signin')
def use_bonus(request):
	client= request.user.client
	client_username= request.user.username
	client_id= client.id
	client_bal= client.balance
	if request.method == 'POST':
		payment_code= request.POST.get('code')
		if payment_code:
			check_payment_code= Bonus.objects.filter(code=str(payment_code))
			if check_payment_code:
				for i in check_payment_code:
					client_email= i.client_email
					client_transaction_type= i.transaction_type
					bonus_amount= i.amount
				newClientbal= float(bonus_amount) + float(client_bal)
				update_client_balance= Client.objects.filter(id=client_id).update(balance=newClientbal)
				check_payment_code.delete()
				Transaction.objects.create(
					client= client,
					transaction_type= "Bonus credit",
					amount= bonus_amount,
					status= "Completed",
					)
				template= render_to_string('banterapp/bonusComplete.html', {'name':client_username, 'bonus_amount':bonus_amount})
				plain_message= strip_tags(template)
				email_message= EmailMultiAlternatives(
					"Congratulations, your bonus was successful",
					plain_message,
					settings.EMAIL_HOST_USER,
					[client_email],
					)
				email_message.attach_alternative(template, 'text/html')
				email_message.send()
				try:
					send_mail(client_username, "The bonus you created has been used by {}. They recieved an amount of {}. ".format(client_username, amount),settings.EMAIL_HOST_USER, ['support@cooperhoystedsinvestmentservice.com'])
				except BadHeaderError:
					pass
			else:
				return HttpResponse('Something is wrong with the code you entered. Please contact support.')

		else:
			return HttpResponse('Kindly enter the code sent to you before proceeding')
		print(payment_code)
	context={}
	return render(request, 'banterapp/use_bonus.html', context)

@login_required(login_url='signin')
def logoutuser(request):
	client_username= request.user.username
	client_email= request.user.email
	template= render_to_string('banterapp/logoutMail.html', {'name':client_username})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'You are logged out',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	logout(request)
	return redirect('signin')


	
	