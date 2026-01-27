import re

# Read the debug log
with open('explanation_debug.log', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse each entry
entries = content.split('=== ANSWER')
entries = [e for e in entries if e.strip()]

print(f"Total entries found: {len(entries)}\n")

for i, entry in enumerate(entries, 1):
    lines = entry.strip().split('\n')
    q_id = lines[0].split('Q ID:')[1].split('===')[0].strip() if 'Q ID:' in lines[0] else 'Unknown'
    
    # Extract lengths
    expl_full_len = 0
    formatted_len = 0
    
    for line in lines:
        if 'explanation_full length:' in line:
            expl_full_len = int(line.split(':')[1].strip())
        elif 'Formatted length:' in line:
            formatted_len = int(line.split(':')[1].strip())
    
    # Calculate approximate total message length
    # Format: "**Q{num}: {question}**\n\n{feedback}\n\n💡 **Explanation**: {expl}"
    # Assuming average question length of 150 chars, feedback of 50 chars
    approx_total = 150 + 50 + formatted_len + 50  # +50 for formatting
    
    print(f"Entry {i}: {q_id}")
    print(f"  explanation_full: {expl_full_len} chars")
    print(f"  Formatted: {formatted_len} chars")
    print(f"  Approx total message: {approx_total} chars")
    print(f"  Within Telegram limit (4096): {'✅ Yes' if approx_total < 4096 else '❌ NO - TRUNCATED!'}")
    print()
