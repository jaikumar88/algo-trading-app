#!/usr/bin/env python3
"""
Fix all API calls in React components to use the proper API service
"""
import os
import re

def fix_component_api_calls():
    """Fix API calls in all React components"""
    
    # Key components to fix
    components_to_fix = [
        'client/src/features/trading/components/Positions.jsx',
        'client/src/features/trading/components/AdminInstruments.jsx', 
        'client/src/features/risk/components/RiskManagement.jsx',
        'client/src/features/trading/components/SystemControl.jsx',
        'client/src/features/trading/components/TradeHistory.jsx',
        'client/src/features/charts/components/MultiSymbolCharts.jsx',
        'client/src/features/charts/components/TradingViewAdvanced.jsx',
    ]
    
    print("🔧 FIXING API CALLS IN REACT COMPONENTS")
    print("=" * 60)
    
    for component_path in components_to_fix:
        if not os.path.exists(component_path):
            print(f"⚠️ {component_path} not found, skipping")
            continue
            
        print(f"📝 Processing {component_path}")
        
        try:
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Add API import if not present
            if "import { apiUrl }" not in content and "from '../../../services/api'" not in content:
                # Find the import section
                import_match = re.search(r"(import.*from ['\"].*['\"])", content)
                if import_match:
                    # Add API import after last import
                    imports_end = content.rfind('import')
                    if imports_end != -1:
                        line_end = content.find('\n', imports_end)
                        if line_end != -1:
                            # Determine correct relative path
                            if '/features/' in component_path:
                                api_import = "import { apiUrl } from '../../../services/api'\n"
                            else:
                                api_import = "import { apiUrl } from './services/api'\n"
                                
                            content = content[:line_end+1] + api_import + content[line_end+1:]
            
            # Replace axios.get('/api/... with axios.get(apiUrl('/api/...
            content = re.sub(
                r"axios\.get\(['\"](/api/[^'\"]+)['\"]", 
                r"axios.get(apiUrl('\1')", 
                content
            )
            
            # Replace axios.post('/api/... with axios.post(apiUrl('/api/...
            content = re.sub(
                r"axios\.post\(['\"](/api/[^'\"]+)['\"]", 
                r"axios.post(apiUrl('\1')", 
                content
            )
            
            # Replace axios.put('/api/... with axios.put(apiUrl('/api/...
            content = re.sub(
                r"axios\.put\(['\"](/api/[^'\"]+)['\"]", 
                r"axios.put(apiUrl('\1')", 
                content
            )
            
            # Replace axios.delete('/api/... with axios.delete(apiUrl('/api/...
            content = re.sub(
                r"axios\.delete\(['\"](/api/[^'\"]+)['\"]", 
                r"axios.delete(apiUrl('\1')", 
                content
            )
            
            if content != original_content:
                with open(component_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Fixed API calls in {os.path.basename(component_path)}")
            else:
                print(f"   ℹ️ No changes needed in {os.path.basename(component_path)}")
                
        except Exception as e:
            print(f"   ❌ Error processing {component_path}: {e}")
    
    print(f"\n🎯 API CALLS FIXED!")
    print("All components now use apiUrl() for proper environment detection")

if __name__ == "__main__":
    fix_component_api_calls()