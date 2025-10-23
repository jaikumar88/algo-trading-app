"""Fix emoji encoding issues in log messages"""
import re

files_to_fix = [
    'src/services/risk_management_service.py',
    'src/services/trade_monitor_service.py'
]

emoji_replacements = [
    ('🛑 STOP LOSS:', '[STOP LOSS]'),
    ('� STOP LOSS:', '[STOP LOSS]'),  # Corrupted emoji
    ('✅ TAKE PROFIT:', '[TAKE PROFIT]'),
    ('📈 New high', '[NEW HIGH]'),
    ('📉 New low', '[NEW LOW]'),
    ('📉 TRAILING STOP:', '[TRAILING STOP]'),
    ('📈 TRAILING STOP:', '[TRAILING STOP]'),
    ('🚨 EMERGENCY SPIKE:', '[EMERGENCY SPIKE]'),
    ('🔍 CHECKING', '[RISK CHECK] CHECKING'),
    ('🔍 Evaluating', '[EVALUATING]'),
    ('📋 Summary:', '[SUMMARY]'),
    ('🛑 TRADE MONITOR STOPPED', '[STOPPED] TRADE MONITOR STOPPED'),
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for emoji, replacement in emoji_replacements:
            content = content.replace(emoji, replacement)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {file_path}")
        else:
            print(f"- No changes needed in {file_path}")
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")

print("\nDone!")
