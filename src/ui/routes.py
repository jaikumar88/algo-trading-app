"""
UI Routes - Web Interface for Trading Dashboard
Serves HTML templates for the trading application
"""
from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Create UI blueprint
ui_bp = Blueprint(
    'ui', 
    __name__, 
    url_prefix='',  # No prefix for main UI routes
    template_folder='../templates',
    static_folder='../static'
)

@ui_bp.route('/dashboard')
def dashboard():
    """Trading dashboard with charts and summaries"""
    logger.info("Serving trading dashboard")
    return render_template('dashboard.html')

@ui_bp.route('/signals')
def signals():
    """Signals management interface"""
    logger.info("Serving signals page")
    return render_template('signals.html')

@ui_bp.route('/trades')
def trades():
    """Active trades management interface"""
    logger.info("Serving trades page")
    return render_template('trades.html')

@ui_bp.route('/rag')
def rag_demo():
    """RAG demo interface (original index.html)"""
    logger.info("Serving RAG demo page")
    return render_template('index.html')

# Default route - redirect to dashboard
@ui_bp.route('/')
def index():
    """Main landing page - show dashboard"""
    logger.info("Redirecting root to dashboard")
    return render_template('dashboard.html')

# API endpoint to get page data
@ui_bp.route('/api/ui/page-data')
def get_page_data():
    """Get basic page data for UI initialization"""
    try:
        return jsonify({
            'status': 'success',
            'app_name': 'RAG Trading System',
            'version': '2.0.0',
            'pages': {
                'dashboard': '/dashboard',
                'signals': '/signals', 
                'rag_demo': '/rag'
            },
            'api_base': '/api'
        })
    except Exception as e:
        logger.error(f"Error getting page data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500