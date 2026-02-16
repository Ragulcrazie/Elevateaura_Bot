import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

def check_stats():
    print("🔄 Connecting to Supabase...")
    try:
        # Standard synchronous client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch data
        # Using .select("*") and .contains() for JSONB
        # This returns a postgrest.APIResponse object
        response = supabase.table('users').select("*").contains("metadata", '{"acquisition_source": "google_ads"}').execute()
        
        users = response.data
        count = len(users)
        
        print("\n" + "="*40)
        print(f"📊 GOOGLE ADS CAMPAIGN STATS")
        print("="*40)
        print(f"✅ Total Users Acquired: {count}")
        
        if count > 0:
            print("\n📝 Recent Users:")
            print(f"{'Name':<20} | {'Date':<12} | {'Campaign'}")
            print("-" * 50)
            
            # Sort by date
            users.sort(key=lambda x: x.get('metadata', {}).get('acquisition_date', ''), reverse=True)
            
            for u in users[:10]:
                meta = u.get('metadata', {}) or {}
                # Handle possible missing fields
                first = u.get('first_name') or ""
                last = u.get('last_name') or ""
                full = (first + " " + last).strip() or u.get('full_name') or "Unknown"
                
                date = meta.get('acquisition_date', 'N/A')
                camp = meta.get('acquisition_campaign', 'N/A')
                print(f"{full[:18]:<20} | {date:<12} | {camp}")
        else:
            print("\nℹ️ No users found yet.")
            print("   (This is expected if you just started the campaign)")
            
        print("="*40 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_stats()
