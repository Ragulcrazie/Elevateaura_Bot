#!/usr/bin/env python3
"""
Verification script to confirm all changes are in place.
Run this on both local and Render to verify code synchronization.
"""

import os
import sys

def check_file_contains(filepath, search_string, description):
    """Check if a file contains a specific string."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NOT FOUND")
                return False
    except FileNotFoundError:
        print(f"❌ {description} - FILE NOT FOUND: {filepath}")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("=" * 80)
    print("DEPLOYMENT VERIFICATION - Full Explanation Fix")
    print("=" * 80)
    print()
    
    checks = []
    
    # Check 1: quiz.py uses explanation_full only
    checks.append(check_file_contains(
        'bot/handlers/quiz.py',
        'ALWAYS use explanation_full, NEVER use short explanation',
        'Check 1: quiz.py - Always use explanation_full'
    ))
    
    # Check 2: Markdown error handling
    checks.append(check_file_contains(
        'bot/handlers/quiz.py',
        'except Exception as markdown_error:',
        'Check 2: quiz.py - Markdown error handling'
    ))
    
    # Check 3: Debug logging
    checks.append(check_file_contains(
        'bot/handlers/quiz.py',
        "with open('explanation_debug.log', 'a', encoding='utf-8') as f:",
        'Check 3: quiz.py - Debug logging'
    ))
    
    # Check 4: Auto-kill old instances
    checks.append(check_file_contains(
        'main.py',
        'import psutil',
        'Check 4: main.py - psutil import'
    ))
    
    checks.append(check_file_contains(
        'main.py',
        'Found old bot instance',
        'Check 5: main.py - Auto-kill logic'
    ))
    
    # Check 6: psutil in requirements
    checks.append(check_file_contains(
        'requirements.txt',
        'psutil',
        'Check 6: requirements.txt - psutil dependency'
    ))
    
    print()
    print("=" * 80)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("✅ Code is synchronized and ready!")
        return 0
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total})")
        print("❌ Code may not be synchronized!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
