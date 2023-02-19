from django.core.management.base import BaseCommand

from greatestinvestapp.models import Client

from django.conf import settings

import requests

import json

import random

from django.db.models import Count, F, Value

class Command(BaseCommand):
	help = 'Top users balance automatically'

	def handle(self, *args, **kwargs):
		print('Script to top up clients automatically')
		for client in Client.objects.annotate(pro= F('deposit') * F('roi') + F('profit'), bal= F('deposit') + F('profit')):
			if float(client.running_days) == 30:
				client.profit= 0
				client.deposit= 0
				client.balance= float(client.balance) + client.bal
				client.save()
				print('You have reached your maximum running days')
			else:
				client.profit= client.pro or 0
				if client.deposit > 0:
					client.running_days= float(client.running_days) + 1
				client.save()
				print('Your topup was successful')
		client= Client.objects.all()
		for i in client:
			print(i.profit)
			print(i.balance)

