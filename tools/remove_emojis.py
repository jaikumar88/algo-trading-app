"""
Remove all emoji characters from source files
"""
import os


EMOJI_REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[X]',
    '📊': '[CHART]',
    '🔄': '[REFRESH]',
    '⏳': '[WAIT]',
    '🚀': '[START]',
    'ℹ️': '[INFO]',
    '⚠️': '[WARN]',
    '🎯': '[TARGET]',
    '💰': '[MONEY]',
    '📈': '[UP]',
    '📉': '[DOWN]',
}


def remove_emojis_from_file(filepath):
    """Remove emojis from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Check if any changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"[ERROR] Failed to process {filepath}: {e}")
        return False


def main():
    """Remove emojis from all service files"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    files_to_process = [
        'app.py',
        'src/api/webhook.py',
        'src/services/delta_exchange_service.py',
        'src/services/trade_monitor_service.py',
        'src/services/risk_management_service.py',
        'src/services/price_collector_service.py',
        'src/services/trading_service.py',
    ]
    
    print("=" * 80)
    print("REMOVING EMOJI CHARACTERS")
    print("=" * 80)
    print()
    
    modified_count = 0
    
    for file_path in files_to_process:
        full_path = os.path.join(base_dir, file_path)
        
        if os.path.exists(full_path):
            if remove_emojis_from_file(full_path):
                print(f"[MODIFIED] {file_path}")
                modified_count += 1
            else:
                print(f"[SKIPPED]  {file_path} (no emojis)")
        else:
            print(f"[NOT FOUND] {file_path}")
    
    print()
    print("=" * 80)
    print(f"[SUMMARY] Modified {modified_count} files")
    print("=" * 80)


if __name__ == "__main__":
    main()
