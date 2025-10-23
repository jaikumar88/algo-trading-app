#!/usr/bin/env python3
"""
Update all components to use apiClient instead of axios + apiUrl
"""
import os
import re

def update_component_to_use_api_client(filepath):
    """Update a component to use apiClient"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace axios import with apiClient
    if "import axios from 'axios'" in content:
        # Check if apiUrl or apiClient is already imported
        if "import { apiUrl }" in content:
            content = content.replace(
                "import { apiUrl } from '../../../services/api'",
                "import { apiClient } from '../../../services/api'"
            )
            content = content.replace(
                "import { apiUrl } from '../../services/api'",
                "import { apiClient } from '../../services/api'"
            )
        elif "apiClient" not in content:
            # Add apiClient import after axios
            content = re.sub(
                r"import axios from 'axios'",
                "import axios from 'axios'\nimport { apiClient } from '../../../services/api'",
                content
            )
    
    # Replace axios.get(apiUrl(...)) with apiClient.get(...)
    content = re.sub(
        r"axios\.get\(apiUrl\(['\"]([^'\"]+)['\"]\)",
        r"apiClient.get('\1'",
        content
    )
    
    # Replace axios.post(apiUrl(...)) with apiClient.post(...)
    content = re.sub(
        r"axios\.post\(apiUrl\(['\"]([^'\"]+)['\"]\)",
        r"apiClient.post('\1'",
        content
    )
    
    # Replace axios.put(apiUrl(...)) with apiClient.put(...)
    content = re.sub(
        r"axios\.put\(apiUrl\(['\"]([^'\"]+)['\"]\)",
        r"apiClient.put('\1'",
        content
    )
    
    # Replace axios.delete(apiUrl(...)) with apiClient.delete(...)
    content = re.sub(
        r"axios\.delete\(apiUrl\(['\"]([^'\"]+)['\"]\)",
        r"apiClient.delete('\1'",
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 UPDATING COMPONENTS TO USE apiClient")
    print("=" * 60)
    
    components = [
        'client/src/features/trading/components/Positions.jsx',
        'client/src/features/trading/components/AdminInstruments.jsx',
        'client/src/features/risk/components/RiskManagement.jsx',
        'client/src/features/trading/components/SystemControl.jsx',
        'client/src/features/trading/components/TradeHistory.jsx',
        'client/src/features/charts/components/MultiSymbolCharts.jsx',
        'client/src/features/charts/components/TradingViewAdvanced.jsx',
    ]
    
    updated = 0
    for component in components:
        if os.path.exists(component):
            if update_component_to_use_api_client(component):
                print(f"✅ Updated: {os.path.basename(component)}")
                updated += 1
            else:
                print(f"ℹ️ No changes: {os.path.basename(component)}")
        else:
            print(f"⚠️ Not found: {component}")
    
    print(f"\n✅ Updated {updated} components to use apiClient with ngrok headers")

if __name__ == "__main__":
    main()
