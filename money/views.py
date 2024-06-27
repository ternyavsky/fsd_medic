from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
import stripe

# Create your views here.
api_key = "sk_test_51PVDGwHilqN7vT0ttpwGz1Qf8n5dsX6tSGGO0YgyQTqpgv5YWQ5NXs5lfRIA5fxomjXhXvI3NH2RSJhn5xErBwyW00HeSpOtEY"
YOUR_DOMAIN = "http://127.0.0.1:8000/"


stripe.api_key = api_key

class MoneyView(APIView):
    def get(self, request):
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    "price": "price_1PVDQ5HilqN7vT0tAFjvphT5",
                    "quantity": 1,
                },
            ],
            payment_method_types=["card",],
            mode="subscription",
            success_url=YOUR_DOMAIN + "?success=true",
            cancel_url=YOUR_DOMAIN + "?canceled=true",
        )
        return redirect(checkout_session.url, code=303)
