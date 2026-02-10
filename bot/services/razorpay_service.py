import razorpay
import hmac
import hashlib
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logger = logging.getLogger(__name__)

class RazorpayService:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not self.key_id or not self.key_secret:
            logger.warning("⚠️ Razorpay keys not found in .env. Payment features will be disabled.")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_payment_link(self, user_id: int, amount: int, description: str, reference_id: str, callback_url: str = None) -> dict:
        """
        Create a Razorpay Payment Link.
        
        Args:
            user_id: Telegram User ID (used for custome notes)
            amount: Amount in PAISE (e.g. 100 for ₹1)
            description: Description of the payment item
            reference_id: Unique order ID for our system
            callback_url: Optional URL to redirect after payment
            
        Returns:
            dict with 'short_url', 'id', 'status'
        """
        if not self.client:
            logger.error("Razorpay client not initialized.")
            return None

        try:
            # Payment Link Payload
            data = {
                "amount": amount,
                "currency": "INR",
                "accept_partial": False,
                "first_min_partial_amount": 0,
                "description": description,
                "customer": {
                    "name": f"User {user_id}",
                    "contact": "9999999999", # Placeholder, required field
                    "email": "customer@elevateaura.com" # Placeholder
                },
                "notify": {
                    "sms": False,
                    "email": False
                },
                "reminder_enable": False,
                "notes": {
                    "user_id": str(user_id),
                    "internal_ref": reference_id
                },
                "callback_url": callback_url or "https://t.me/ElevateAura_Bot", # Redirect back to bot
                "callback_method": "get"
            }
            
            # Create Link
            response = self.client.payment_link.create(data)
            logger.info(f"✅ Payment Link Created: {response.get('short_url')}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Razorpay Link Creation Failed: {e}")
            return None

    def verify_webhook_signature(self, request_body: str, signature: str) -> bool:
        """
        Verify the webhook signature to ensure authenticity.
        """
        if not self.key_secret:
            return False
            
        try:
            # Use hmac to verify
            # signature is passed in header 'X-Razorpay-Signature'
            generated_signature = hmac.new(
                bytes(self.key_secret, 'utf-8'),
                msg=bytes(request_body, 'utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(generated_signature, signature)
        except Exception as e:
            logger.error(f"Signature Verification Error: {e}")
            return False

    def fetch_payment_status(self, payment_link_id: str):
        """
        Fetch status of a payment link directly from API (Fallback).
        """
        if not self.client:
            return None
            
        try:
            return self.client.payment_link.fetch(payment_link_id)
        except Exception as e:
            logger.error(f"Fetch Status Error: {e}")
            return None
