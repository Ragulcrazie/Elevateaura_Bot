"""
Ad Service - Monetag Integration
Handles ad display logic, frequency capping, and analytics tracking.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class AdService:
    """
    Manages ad display decisions and tracking.
    """
    
    def __init__(self, db_client=None):
        """Initialize ad service with config and database."""
        self.db = db_client
        self.config = self._load_config()
        self.user_ad_cache = {}  # In-memory cache for last ad times
        
    def _load_config(self) -> dict:
        """Load ad configuration from JSON file."""
        try:
            # Config is in root/config not bot/config
            config_path = Path(__file__).parent.parent.parent / "config" / "ad_config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Ad config loaded successfully from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load ad config: {e}")
            # Return safe defaults if config fails
            return {
                "enabled": False,
                "test_mode": True,
                "test_user_ids": [],
                "premium_skip_ads": True
            }
    
    def _get_ist_now(self) -> datetime:
        """Get current time in IST timezone."""
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(ist_offset)
    
    def _get_ist_date_str(self) -> str:
        """Get current date in IST as YYYY-MM-DD string."""
        return self._get_ist_now().strftime("%Y-%m-%d")
    
    async def should_show_ad(
        self, 
        user_id: int, 
        placement: str,
        user_data: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Determine if an ad should be shown to this user at this placement.
        
        Returns:
            (should_show: bool, reason: str)
        """
        
        # --- CHECK 1: Ad System Enabled ---
        if not self.config.get("enabled", False):
            return False, "ad_system_disabled"
        
        # --- CHECK 2: Test Mode ---
        if self.config.get("test_mode", False):
            test_users = self.config.get("test_user_ids", [])
            if user_id not in test_users:
                return False, "test_mode_user_not_whitelisted"
        
        # --- CHECK 3: Premium Users (CRITICAL - NO ADS FOR PREMIUM) ---
        if self.config.get("premium_skip_ads", True):
            if user_data:
                subscription_status = user_data.get("subscription_status")
                # IMMEDIATE BLOCK: Any premium user gets NO ads, period
                if subscription_status == "premium":
                    logger.info(f"🚫 Premium user {user_id} - ads blocked")
                    return False, "premium_user_no_ads"
                
                # Double-check expiry if status isn't explicitly premium
                expiry_str = user_data.get("subscription_expiry")
                if expiry_str:
                    try:
                        expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                        if expiry_date > self._get_ist_now().replace(tzinfo=None):
                            logger.info(f"🚫 Active subscription for {user_id} - ads blocked")
                            return False, "active_subscription_no_ads"
                    except Exception as e:
                        logger.warning(f"Expiry parse failed for {user_id}: {e}")
        
        # --- CHECK 4: Placement Enabled ---
        placements = self.config.get("placements", {})
        placement_config = placements.get(placement, {})
        
        if not placement_config.get("enabled", False):
            return False, f"placement_{placement}_disabled"
        
        # --- CHECK 5: Cooldown Period ---
        cooldown_minutes = placement_config.get("cooldown_minutes", 5)
        cache_key = f"{user_id}_{placement}"
        
        if cache_key in self.user_ad_cache:
            last_ad_time = self.user_ad_cache[cache_key]
            time_since_last_ad = (self._get_ist_now() - last_ad_time).total_seconds()
            
            if time_since_last_ad < (cooldown_minutes * 60):
                return False, f"cooldown_active_{int(time_since_last_ad)}s"
        
        # --- CHECK 6: Daily Frequency Cap ---
        if self.db and self.db.client:
            try:
                daily_cap = self.config.get("frequency_limits", {}).get("max_ads_per_day", 6)
                today_str = self._get_ist_date_str()
                
                # Query ad impressions for today
                response = self.db.client.from_("ad_impressions") \
                    .select("id") \
                    .eq("user_id", user_id) \
                    .gte("timestamp", f"{today_str} 00:00:00") \
                    .execute()
                
                if response.data and len(response.data) >= daily_cap:
                    return False, f"daily_cap_reached_{len(response.data)}/{daily_cap}"
                    
            except Exception as e:
                # If analytics table doesn't exist yet, log but don't block ads
                logger.warning(f"Could not check daily cap: {e}")
        
        # --- CHECK 7: Global Cooldown Between Any Ads ---
        min_seconds = self.config.get("frequency_limits", {}).get("min_seconds_between_ads", 120)
        
        # Check if ANY ad was shown recently (across all placements)
        recent_ads = [
            (key, time) for key, time in self.user_ad_cache.items() 
            if key.startswith(f"{user_id}_")
        ]
        
        if recent_ads:
            most_recent = max(recent_ads, key=lambda x: x[1])
            time_since = (self._get_ist_now() - most_recent[1]).total_seconds()
            
            if time_since < min_seconds:
                return False, f"global_cooldown_{int(time_since)}s"
        
        # --- ALL CHECKS PASSED ---
        return True, "approved"
    
    async def record_ad_impression(
        self, 
        user_id: int, 
        placement: str,
        success: bool = True
    ) -> bool:
        """
        Record that an ad was shown to the user.
        Updates cache and database.
        """
        
        # Update in-memory cache
        cache_key = f"{user_id}_{placement}"
        self.user_ad_cache[cache_key] = self._get_ist_now()
        
        # Record in database for analytics
        if self.config.get("analytics_enabled", True) and self.db and self.db.client:
            try:
                data = {
                    "user_id": user_id,
                    "placement": placement,
                    "timestamp": self._get_ist_now().isoformat(),
                    "success": success
                }
                
                self.db.client.from_("ad_impressions").insert(data).execute()
                logger.info(f"✅ Ad impression recorded: {user_id} @ {placement}")
                return True
                
            except Exception as e:
                # Don't fail if analytics fails
                logger.warning(f"Ad impression recording failed: {e}")
                return False
        
        return True
    
    def get_monetag_code(self, placement: str) -> Optional[str]:
        """
        Generate the Monetag ad display code for a specific placement.
        Returns JavaScript code to inject.
        """
        
        if not self.config.get("enabled", False):
            return None
        
        publisher_id = self.config.get("monetag_publisher_id", "10557666")
        
        # Prepare In-App Interstitial settings (correct format per Monetag docs)
        in_app_settings = {
            "frequency": 1,      # Show 1 ad
            "capping": 0.016,    # Within ~1 minute window
            "interval": 0,       # No interval between ads
            "timeout": 1,        # 1 second delay before showing
            "everyPage": False   # Session persists
        }
        
        # Generate JavaScript code with CORRECT format
        js_code = f"""
<script>
(function() {{
    try {{
        if (typeof show_{publisher_id} === 'function') {{
            show_{publisher_id}({{
                type: 'inApp',
                inAppSettings: {json.dumps(in_app_settings)}
            }});
            console.log('✅ Monetag In-App ad triggered from backend code');
        }} else {{
            console.warn('❌ Monetag SDK not loaded');
        }}
    }} catch(e) {{
        console.error('Ad display error:', e);
    }}
}})();
</script>
        """.strip()
        
        return js_code
    
    async def get_ad_stats(self, user_id: int, days: int = 7) -> Dict:
        """
        Get ad statistics for a user.
        Returns impression counts by placement.
        """
        
        if not self.db or not self.db.client:
            return {}
        
        try:
            # Calculate start date
            start_date = (self._get_ist_now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            response = self.db.client.from_("ad_impressions") \
                .select("placement") \
                .eq("user_id", user_id) \
                .gte("timestamp", f"{start_date} 00:00:00") \
                .execute()
            
            if not response.data:
                return {}
            
            # Count by placement
            stats = {}
            for record in response.data:
                placement = record.get("placement", "unknown")
                stats[placement] = stats.get(placement, 0) + 1
            
            stats["total"] = len(response.data)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get ad stats: {e}")
            return {}


# Global singleton instance
_ad_service_instance = None

def get_ad_service(db_client=None):
    """Get or create the global AdService instance."""
    global _ad_service_instance
    
    if _ad_service_instance is None:
        _ad_service_instance = AdService(db_client)
    elif db_client and _ad_service_instance.db is None:
        _ad_service_instance.db = db_client
    
    return _ad_service_instance
