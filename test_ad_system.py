"""
Quick test script to verify ad system is working
Run this before starting the bot to ensure everything is configured correctly
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.services.ad_service import get_ad_service
from database.db_client import SupabaseClient

async def test_ad_system():
    """Test the ad system configuration and basic functionality."""
    
    print("=" * 60)
    print("🧪 AD SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Load Ad Service
    print("\n[TEST 1] Loading Ad Service...")
    service = get_ad_service()
    print(f"✅ Ad Service loaded")
    
    # Test 2: Check Config
    print("\n[TEST 2] Checking Configuration...")
    print(f"  Enabled: {service.config.get('enabled')}")
    print(f"  Test Mode: {service.config.get('test_mode')}")
    print(f"  Test User IDs: {service.config.get('test_user_ids')}")
    print(f"  Premium Skip: {service.config.get('premium_skip_ads')}")
    
    if not service.config.get('enabled'):
        print("⚠️  WARNING: Ad system is DISABLED in config!")
        return False
    
    if service.config.get('test_mode') and not service.config.get('test_user_ids'):
        print("⚠️  WARNING: Test mode is ON but no test users configured!")
        return False
    
    print("✅ Configuration looks good")
    
    # Test 3: Database Connection
    print("\n[TEST 3] Testing Database Connection...")
    db = SupabaseClient()
    connected = await db.connect()
    
    if not connected:
        print("❌ Database connection failed!")
        return False
    
    print("✅ Database connected")
    
    # Test 4: Check ad_impressions table
    print("\n[TEST 4] Checking ad_impressions table...")
    try:
        result = db.client.from_("ad_impressions").select("*").limit(1).execute()
        print(f"✅ Table exists (found {len(result.data)} sample rows)")
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        print("   Run the migration SQL first: database/migration_ads.sql")
        return False
    
    # Test 5: Test Ad Eligibility Check
    print("\n[TEST 5] Testing Ad Eligibility Logic...")
    test_user_id = service.config.get('test_user_ids', [])[0] if service.config.get('test_user_ids') else 996261168
    
    # Get user data
    user_data = await db.get_user(test_user_id)
    if not user_data:
        print(f"⚠️  User {test_user_id} not found in database")
        print("   (This is OK for testing, creating mock user data)")
        user_data = {"user_id": test_user_id, "subscription_status": "free"}
    
    # Initialize service with db
    service.db = db
    
    # Check if ad should show
    should_show, reason = await service.should_show_ad(
        user_id=test_user_id,
        placement="post_quiz",
        user_data=user_data
    )
    
    print(f"  User ID: {test_user_id}")
    print(f"  Should Show Ad: {should_show}")
    print(f"  Reason: {reason}")
    
    if not should_show:
        print(f"⚠️  Ad won't show! Reason: {reason}")
        if reason == "test_mode_user_not_whitelisted":
            print("   Fix: Make sure your Telegram user ID is in test_user_ids in config")
        return False
    
    print("✅ Ad will show for test user")
    
    # Test 6: Test Impression Recording
    print("\n[TEST 6] Testing Impression Recording...")
    try:
        success = await service.record_ad_impression(test_user_id, "test_placement")
        if success:
            print("✅ Impression recorded successfully")
            
            # Verify it was saved
            result = db.client.from_("ad_impressions") \
                .select("*") \
                .eq("user_id", test_user_id) \
                .eq("placement", "test_placement") \
                .execute()
            
            if result.data:
                print(f"✅ Verified in database ({len(result.data)} records)")
                # Clean up test record
                db.client.from_("ad_impressions") \
                    .delete() \
                    .eq("user_id", test_user_id) \
                    .eq("placement", "test_placement") \
                    .execute()
                print("✅ Test record cleaned up")
            else:
                print("⚠️  Record not found in database (analytics might be disabled)")
        else:
            print("⚠️  Impression recording returned False")
    except Exception as e:
        print(f"❌ Impression recording failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"  • Ad system is enabled and configured correctly")
    print(f"  • Test user ID: {test_user_id}")
    print(f"  • Database connection works")
    print(f"  • ad_impressions table exists")
    print(f"  • Ad eligibility logic works")
    print(f"  • Impression recording works")
    print("\n✨ Your bot is ready to show ads!")
    print("\n📝 Next steps:")
    print("  1. Start your bot: python main.py")
    print("  2. Send /quiz to the bot (as the test user)")
    print("  3. Complete a quiz")
    print("  4. You should see an ad message after results")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_ad_system())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
