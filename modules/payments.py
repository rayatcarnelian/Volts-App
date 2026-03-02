"""
PAYMENTS MODULE
Handles Stripe Checkout and Subscription Management.
Supports Malaysia (MYR) and International (USD).
"""

import os
import streamlit as st
import stripe
from dotenv import load_dotenv

load_dotenv()

class PaymentGateway:
    def __init__(self):
        self.stripe_key = os.getenv("STRIPE_SECRET_KEY")
        self.price_id = os.getenv("STRIPE_PRICE_ID")
        self.is_active = False
        
        if self.stripe_key and self.price_id:
            stripe.api_key = self.stripe_key
            self.is_active = True
            
    def create_checkout_session(self, user_email, price_id=None, success_url=None, cancel_url=None):
        """
        Creates a Stripe Checkout Session.
        Returns the URL to redirect the user to.
        """
        if not self.is_active:
            return None, "Stripe not configured"
            
        target_price = price_id if price_id else self.price_id
            
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=user_email,
                line_items=[
                    {
                        'price': target_price,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
            )
            return checkout_session.url, None
        except Exception as e:
            return None, str(e)
            
    def verify_session(self, session_id):
        """
        Verifies a checkout session with Stripe.
        Returns (is_valid, email, tier_id)
        """
        if not self.is_active:
            return False, None, None
            
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                # Map price ID to Tier if needed, or just return email
                # inferred_tier = "PRO" 
                return True, session.customer_details.email, "PRO"
            return False, None, None
        except Exception as e:
            print(f"Stripe Verification Error: {e}")
            return False, None, None
            
    def is_configured(self):
        """Returns True if Stripe keys are present."""
        return self.is_active
 
# Singleton
gateway = PaymentGateway()
