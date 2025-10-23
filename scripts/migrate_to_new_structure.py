"""
Project Refactoring Migration Script
Reorganizes the RAG Trading System into proper folder structure
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict

# Base paths
ROOT = Path(__file__).parent
BACKEND_SRC = ROOT / "backend" / "src"
FRONTEND = ROOT / "frontend"
DOCS = ROOT / "docs"

# Color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}")
    print(f"{text:^80}")
    print(f"{'=' * 80}{RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def create_folder_structure():
    """Create the new folder structure"""
    print_header("PHASE 1: Creating Folder Structure")
    
    folders = [
        # Backend
        BACKEND_SRC / "api",
        BACKEND_SRC / "services",
        BACKEND_SRC / "models",
        BACKEND_SRC / "database" / "migrations",
        BACKEND_SRC / "tasks",
        BACKEND_SRC / "utils",
        BACKEND_SRC / "config",
        BACKEND_SRC / "schemas",
        ROOT / "backend" / "tests" / "unit",
        ROOT / "backend" / "tests" / "integration",
        ROOT / "backend" / "tests" / "e2e",
        ROOT / "backend" / "scripts",
        ROOT / "backend" / "docs",
        ROOT / "backend" / "requirements",
        
        # Frontend
        FRONTEND / "src" / "features" / "dashboard",
        FRONTEND / "src" / "features" / "trading",
        FRONTEND / "src" / "features" / "charts",
        FRONTEND / "src" / "features" / "signals",
        FRONTEND / "src" / "features" / "settings",
        FRONTEND / "src" / "shared" / "components",
        FRONTEND / "src" / "shared" / "layouts",
        FRONTEND / "src" / "shared" / "ui",
        FRONTEND / "src" / "hooks",
        FRONTEND / "src" / "services",
        FRONTEND / "src" / "utils",
        FRONTEND / "src" / "constants",
        FRONTEND / "src" / "types",
        FRONTEND / "src" / "styles",
        FRONTEND / "public",
        
        # Project docs
        DOCS / "setup",
        DOCS / "guides",
        DOCS / "api",
        DOCS / "architecture",
        
        # Docker
        ROOT / "docker",
    ]
    
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        print_success(f"Created: {folder.relative_to(ROOT)}")
    
    # Create __init__.py files
    init_files = [
        BACKEND_SRC / "api" / "__init__.py",
        BACKEND_SRC / "services" / "__init__.py",
        BACKEND_SRC / "models" / "__init__.py",
        BACKEND_SRC / "database" / "__init__.py",
        BACKEND_SRC / "tasks" / "__init__.py",
        BACKEND_SRC / "utils" / "__init__.py",
        BACKEND_SRC / "config" / "__init__.py",
        BACKEND_SRC / "schemas" / "__init__.py",
        ROOT / "backend" / "tests" / "__init__.py",
    ]
    
    for init_file in init_files:
        init_file.touch()
        print_success(f"Created: {init_file.relative_to(ROOT)}")


def get_file_mappings() -> Dict[str, str]:
    """Define file mappings from old to new locations"""
    return {
        # Backend API files
        "trading_api.py": "backend/src/api/trading.py",
        
        # Backend Services
        "trading.py": "backend/src/services/trading_service.py",
        "price_history_service.py": "backend/src/services/price_service.py",
        "telegram_bot.py": "backend/src/services/telegram_service.py",
        "openai_client.py": "backend/src/services/llm_service.py",
        "gemini_client.py": "backend/src/services/llm_service_gemini.py",
        "vector_store.py": "backend/src/services/vector_service.py",
        
        # Backend Database
        "db.py": "backend/src/database/session.py",
        "models.py": "backend/src/models/base.py",  # Will be split
        
        # Backend Tasks
        "tasks.py": "backend/src/tasks/signal_tasks.py",
        
        # Backend Scripts
        "migrate_db.py": "backend/scripts/migrate_db.py",
        "migrate_postgresql.py": "backend/scripts/migrate_postgresql.py",
        "populate_postgresql.py": "backend/scripts/seed_data.py",
        "create_tables.py": "backend/scripts/create_tables.py",
        "recreate_db.py": "backend/scripts/recreate_db.py",
        "analyze_signals.py": "backend/scripts/analyze_signals.py",
        "process_real_signals.py": "backend/scripts/process_signals.py",
        
        # Backend Tests
        "test_duplicate_prevention.py": "backend/tests/unit/test_duplicate_prevention.py",
        "test_trading_api.py": "backend/tests/unit/test_trading_api.py",
        "test_historical_data.py": "backend/tests/unit/test_historical_data.py",
        "test_dashboard_apis.py": "backend/tests/integration/test_dashboard.py",
        "test_endpoints.py": "backend/tests/integration/test_endpoints.py",
        "test_all_features.py": "backend/tests/e2e/test_all_features.py",
        
        # Check scripts (utils)
        "check_cors.py": "backend/scripts/check_cors.py",
        "check_database.py": "backend/scripts/check_database.py",
        "check_db_structure.py": "backend/scripts/check_db_structure.py",
        "check_signals.py": "backend/scripts/check_signals.py",
        "check_real_data.py": "backend/scripts/check_real_data.py",
        
        # Documentation
        "README.md": "docs/README_OLD.md",
        "HISTORICAL_DATA_GUIDE.md": "docs/guides/historical_data.md",
        "TRADINGVIEW_INTEGRATION.md": "docs/guides/tradingview.md",
        "LIVE_CHART_GUIDE.md": "docs/guides/live_chart.md",
        "TRADING_MANAGEMENT_SYSTEM.md": "docs/guides/trading_management.md",
        "DUPLICATE_TRADE_PREVENTION.md": "docs/guides/duplicate_prevention.md",
        "POSTGRES_SETUP.md": "docs/setup/postgres.md",
        "INSTALLATION_SUCCESS.md": "docs/setup/installation.md",
        "QUICK_START.md": "docs/setup/quick_start.md",
        "ARCHITECTURE_DIAGRAM.txt": "docs/architecture/system_diagram.txt",
        
        # Requirements
        "requirements.txt": "backend/requirements/base.txt",
        
        # Frontend - will handle separately
    }


def move_backend_files():
    """Move backend files to new structure"""
    print_header("PHASE 2: Moving Backend Files")
    
    mappings = get_file_mappings()
    moved_count = 0
    
    for old_path, new_path in mappings.items():
        old_file = ROOT / old_path
        new_file = ROOT / new_path
        
        if old_file.exists():
            # Create parent directory if needed
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file (don't delete original yet, for safety)
            shutil.copy2(old_file, new_file)
            print_success(f"Moved: {old_path} → {new_path}")
            moved_count += 1
        else:
            print_warning(f"File not found: {old_path}")
    
    print(f"\n{GREEN}Moved {moved_count} files{RESET}")


def move_frontend_files():
    """Reorganize frontend files"""
    print_header("PHASE 3: Reorganizing Frontend")
    
    client_src = ROOT / "client" / "src"
    components_dir = client_src / "components"
    
    if not components_dir.exists():
        print_warning("Client components directory not found")
        return
    
    # Feature mapping
    feature_mappings = {
        "Dashboard": "dashboard",
        "TradeHistory": "trading",
        "Positions": "trading",
        "AdminInstruments": "trading",
        "SystemControl": "trading",
        "LiveChart": "charts",
        "HistoricalChart": "charts",
        "TradingViewAdvanced": "charts",
        "TradingViewChart": "charts",
        "Chart": "charts",
        "Signals": "signals",
        "Settings": "settings",
    }
    
    # Move component files
    for component_file in components_dir.glob("*.jsx"):
        component_name = component_file.stem
        
        if component_name in feature_mappings:
            feature = feature_mappings[component_name]
            new_dir = FRONTEND / "src" / "features" / feature / "components"
            new_dir.mkdir(parents=True, exist_ok=True)
            
            new_file = new_dir / component_file.name
            shutil.copy2(component_file, new_file)
            print_success(f"Moved: {component_file.name} → features/{feature}/components/")
            
            # Move corresponding CSS if exists
            css_file = component_file.with_suffix('.css')
            if css_file.exists():
                css_new = new_dir / css_file.name
                shutil.copy2(css_file, css_new)
                print_success(f"Moved: {css_file.name} → features/{feature}/components/")
    
    # Move shared files
    shared_files = ["Layout.jsx", "Layout.css"]
    for filename in shared_files:
        old_file = client_src / filename
        if old_file.exists():
            new_file = FRONTEND / "src" / "shared" / "layouts" / filename
            new_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_file, new_file)
            print_success(f"Moved: {filename} → shared/layouts/")
    
    # Move root files
    root_files = ["App.jsx", "main.jsx", "styles.css", "api.js"]
    for filename in root_files:
        old_file = client_src / filename
        if old_file.exists():
            if filename == "api.js":
                new_file = FRONTEND / "src" / "services" / filename
            elif filename == "styles.css":
                new_file = FRONTEND / "src" / "styles" / "global.css"
            else:
                new_file = FRONTEND / "src" / filename
            
            new_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_file, new_file)
            print_success(f"Moved: {filename} → {new_file.relative_to(FRONTEND / 'src')}")


def create_configuration_files():
    """Create configuration management files"""
    print_header("PHASE 4: Creating Configuration Files")
    
    # Backend config files created in separate function
    print_success("Configuration files will be created in next phase")


def update_documentation():
    """Create updated documentation"""
    print_header("PHASE 5: Updating Documentation")
    
    print_success("Documentation will be updated in next phase")


def create_summary():
    """Create a migration summary"""
    print_header("Migration Summary")
    
    summary = f"""
{GREEN}✅ Folder structure created successfully{RESET}
{GREEN}✅ Backend files reorganized{RESET}
{GREEN}✅ Frontend files reorganized{RESET}

{YELLOW}⚠️  Next Steps:{RESET}
1. Review moved files in new locations
2. Update imports in Python files
3. Update imports in React files
4. Run tests to verify everything works
5. Delete old files after verification

{BLUE}📁 New Structure:{RESET}
- backend/src/      → All Python source code
- frontend/src/     → All React source code
- docs/             → All documentation
- docker/           → Docker configurations

{YELLOW}⚠️  Important:{RESET}
- Original files are preserved (copied, not moved)
- Update imports before deleting originals
- Test thoroughly before committing changes
"""
    
    print(summary)


def main():
    """Main migration function"""
    print_header("RAG Trading System - Project Refactoring")
    print("This script will reorganize your project into a proper structure")
    print("Original files will be copied (not deleted) for safety")
    
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")
    
    try:
        create_folder_structure()
        move_backend_files()
        move_frontend_files()
        create_configuration_files()
        update_documentation()
        create_summary()
        
        print(f"\n{GREEN}{'=' * 80}")
        print(f"{'MIGRATION COMPLETED SUCCESSFULLY':^80}")
        print(f"{'=' * 80}{RESET}\n")
        
    except Exception as e:
        print_error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
