import requests
from flask import flash, redirect
from flask_login import login_required, current_user
from .models import Cart, Order, Product, db


API_URL = 'https://api.novaposhta.ua/v2.0/json/'

class NovaPoshtaAPI:
      def __init__(self, api_key):
            self.api_key = api_key
       
        
      def get_city_ref(self, city_name):
            data = {
                  "apiKey": self.api_key,
                  "modelName": "Address",
                  "calledMethod": "getCities",
                  "methodProperties": {}
            }
            response = requests.post(API_URL, json=data)
            cities = response.json().get('data', [])
            for city in cities:
                  if city['Description'] == city_name:
                        return city['Ref']
            return None

      def create_order(self, recipient_name, recipient_phone, city, address, cost):
            data = {
                  "apiKey": self.api_key,
                  "modelName": "InternetDocument",
                  "calledMethod": "save",
                  "methodProperties": {
                  "PayerType": "Recipient",
                  "PaymentMethod": "Cash",
                  "CargoType": "Cargo",
                  "Weight": "2",
                  "ServiceType": "WarehouseWarehouse",
                  "SeatsAmount": "1",
                  "Description": "Goods",
                  "Cost": cost,
                  "CitySender": "8d5a980d-391c-11dd-90d9-001a92567626",
                  "SenderAddress": "8d5a980d-391c-11dd-90d9-001a92567626",
                  "ContactSender": "1",
                  "SendersPhone": "380660000000",
                  "RecipientCityName": city,
                  "RecipientAddressName": address,
                  "RecipientName": recipient_name,
                  "RecipientType": "PrivatePerson",
                  "RecipientsPhone": recipient_phone,
                  "CityRecipient": city
            }
            }
            response = requests.post(API_URL, json=data)
            return response.json()