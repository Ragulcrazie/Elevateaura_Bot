"""
Razorpay Service for Payment Processing
"""
import os
import razorpay
from bot.utils.logger import logger
import hmac
import hashlib

class RazorpayService:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not self.key_id or not self.key_secret:
            logger.warning("⚠️ Razorpay keys not found in .env. Payment features will be disabled.")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            logger.info("✅ Razorpay Client Initialized")
    
    def create_payment_link(self, user_id: int, amount: int, description: str, reference_id: str):
        """
        Creates a Razorpay Payment Link.
        
        Args:
            user_id: Telegram user ID
            amount: Amount in paise (₹1 = 100 paise)
            description: Payment description
            reference_id: Unique reference ID
            
        Returns:
            dict with 'short_url' and 'id' if successful, None otherwise
        """
        if not self.client:
            logger.error("Razorpay client not initialized")
            return None
            
        try:
            data = {
                "amount": amount,
                "currency": "INR",
                "description": description,
                "customer": {
                    "name": f"User {user_id}",
                    "contact": "",
                    "email": ""
                },
                "notify": {
                    "sms": False,
                    "email": False
                },
                "reminder_enable": False,
                "notes": {
                    "user_id": str(user_id),
                    "reference_id": reference_id
                },
                "callback_url": f"https://t.me/ElevateAura_Bot",
                "callback_method": "get"
            }
            
            response = self.client.payment_link.create(data)
            logger.info(f"✅ Payment Link Created: {response['short_url']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create payment link: {e}")
            return None
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verifies Razorpay webhook signature for security.
        
        Args:
            payload: Raw webhook body as string
            signature: X-Razorpay-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.key_secret:
            return False
            
        try:
            expected_signature = hmac.new(
                self.key_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def fetch_payment(self, payment_id: str):
        """
        Fetches payment details from Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment details dict if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            logger.error(f"Failed to fetch payment: {e}")
            return None
