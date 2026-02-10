"""
Subscription Service - Handles Premium Expiration Logic
Checks and enforces 30-day subscription validity
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from database.db_client import SupabaseClient

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Manages subscription expiration and status tracking"""
    
    def __init__(self):
        self.db = SupabaseClient()
    
    async def check_and_update_expiration(self, user_id: int) -> Dict:
        """
        Check if user's premium subscription has expired and update status.
        
        Returns dict with:
        - status: 'premium' or 'free'
        - expired: bool (True if was premium but just expired)
        - expires_at: timestamp if premium
        - days_remaining: int if premium
        """
        
        connected = await self.db.connect()
        if not connected:
            logger.error(f"DB connection failed for expiration check: {user_id}")
            return {"status": "free", "expired": False}
        
        try:
            # Get user data
            result = self.db.client.from_("users").select("*").eq("user_id", user_id).execute()
            
            if not result.data or len(result.data) == 0:
                return {"status": "free", "expired": False}
            
            user = result.data[0]
            current_status = user.get('subscription_status', 'free')
            expires_at_str = user.get('subscription_expires_at')
            
            # If status is free, return free
            if current_status == 'free':
                return {"status": "free", "expired": False}
                
            # If premium but NO expiry date, treat as Lifetime/Manual Premium
            if not expires_at_str:
                return {"status": "premium", "expired": False, "days_remaining": 999}
            
            # Parse expiry date
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            except:
                logger.error(f"Invalid expiry date format for user {user_id}: {expires_at_str}")
                return {"status": current_status, "expired": False}
            
            now = datetime.utcnow()
            
            # Check if expired
            if now > expires_at:
                # EXPIRED - downgrade to free
                logger.info(f"⏰ Subscription expired for user {user_id}")
                
                self.db.client.from_("users").update({
                    "subscription_status": "free"
                }).eq("user_id", user_id).execute()
                
                return {
                    "status": "free",
                    "expired": True,  # Just expired
                    "expired_at": expires_at.isoformat()
                }
            else:
                # Still premium
                days_remaining = (expires_at - now).days
                
                return {
                    "status": "premium",
                    "expired": False,
                    "expires_at": expires_at.isoformat(),
                    "days_remaining": days_remaining
                }
        
        except Exception as e:
            logger.error(f"Expiration check failed for {user_id}: {e}")
            return {"status": "free", "expired": False}
    
    async def should_send_expiration_warning(self, user_id: int) -> bool:
        """
        Check if user should receive 24-hour expiration warning.
        Returns True if premium expires in 18-24 hours and warning not sent yet.
        """
        
        connected = await self.db.connect()
        if not connected:
            return False
        
        try:
            result = self.db.client.from_("users").select(
                "subscription_status, subscription_expires_at, expiration_warning_sent"
            ).eq("user_id", user_id).execute()
            
            if not result.data or len(result.data) == 0:
                return False
            
            user = result.data[0]
            
            if user.get('subscription_status') != 'premium':
                return False
            
            if user.get('expiration_warning_sent'):  # Already warned
                return False
            
            expires_at_str = user.get('subscription_expires_at')
            if not expires_at_str:
                return False
            
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            except:
                return False
            
            now = datetime.utcnow()
            hours_remaining = (expires_at - now).total_seconds() / 3600
            
            # Send warning if between 18-24 hours remaining
            if 18 <= hours_remaining <= 24:
                # Mark as warned
                self.db.client.from_("users").update({
                    "expiration_warning_sent": True
                }).eq("user_id", user_id).execute()
                
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Warning check failed for {user_id}: {e}")
            return False
    
    async def reset_warning_flag_on_renewal(self, user_id: int):
        """Reset expiration warning flag when user renews subscription"""
        
        connected = await self.db.connect()
        if not connected:
            return
        
        try:
            self.db.client.from_("users").update({
                "expiration_warning_sent": False
            }).eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Warning flag reset failed for {user_id}: {e}")
