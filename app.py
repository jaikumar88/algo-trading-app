"""
RAG Trading System - Application Factory
Modern Flask application with Blueprint architecture
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Load .env file first
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.config.settings import get_settings
except ImportError:
    # Fallback if pydantic-settings not installed
    class Settings:
        ENV = os.getenv('ENV', 'development')
        DEBUG = os.getenv('DEBUG', 'True') == 'True'
        SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev_trading.db')
        LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        def get_cors_origins(self):
            return ["http://localhost:5173", "http://localhost:3000"]
    
    def get_settings():
        return Settings()

from src.database.session import init_db
import logging
from logging.handlers import RotatingFileHandler

# Import blueprints
from src.api.trading import trading_bp
from src.api.webhook import webhook_bp
from src.api.chart import chart_bp
from src.api.trading_enhanced import trading_enhanced_bp
from src.api.metrics import metrics_bp
from src.api.historical import historical_bp
from src.api.symbol_sync import symbol_sync_bp
from src.api.performance import performance_bp
from src.api.risk import risk_bp
from src.ui import ui_bp


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Environment name (development, production, testing)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    settings = get_settings()
    app.config['DEBUG'] = settings.DEBUG
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    
    # Setup logging
    setup_logging(app, settings)
    
    # Initialize database
    init_db()
    
    # Configure CORS
    CORS(app, origins=settings.get_cors_origins())
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # API info endpoint (moved from root to avoid conflict with UI)
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'name': 'RAG Trading System',
            'version': '2.0.0',
            'status': 'running',
            'environment': settings.ENV
        })
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'environment': settings.ENV})
    
    app.logger.info(f'[START] Application started in {settings.ENV} mode')
    
    return app


def register_blueprints(app):
    """Register all API blueprints and UI routes"""
    # API blueprints
    app.register_blueprint(trading_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(trading_enhanced_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(historical_bp)
    app.register_blueprint(symbol_sync_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(risk_bp)
    
    # UI blueprint
    app.register_blueprint(ui_bp)


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        return jsonify({'error': str(error)}), 500


def setup_logging(app, settings):
    """Configure application logging - all logs go to file only"""
    # Configure root logger to catch all module logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Capture INFO and above
    
    # Remove any existing handlers to prevent console output
    root_logger.handlers.clear()
    
    # Configure app logger
    app.logger.setLevel(logging.INFO)
    app.logger.handlers.clear()
    
    # Try to add file handler, but don't crash if it fails
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler - all logs go to file with UTF-8 encoding
        log_file = os.path.join(logs_dir, 'app.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10240000,
            backupCount=10,
            encoding='utf-8'  # Force UTF-8 encoding
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        
        root_logger.addHandler(file_handler)
        app.logger.addHandler(file_handler)
        
        # Print startup message to console only
        print(f"[OK] Logging configured - logs saved to: {log_file}")
    except Exception as e:
        # Only print error to console if file logging fails
        print(f"[ERROR] Could not setup file logging: {e}")


if __name__ == '__main__':
    app = create_app()
    settings = get_settings()
    
    # Start trade monitor in background
    try:
        from src.services.trade_monitor_service import get_trade_monitor
        monitor = get_trade_monitor(check_interval=5)  # Check every 5 seconds
        monitor.start()
        app.logger.info("[OK] Trade monitor started")
    except Exception as e:
        app.logger.error(f"Failed to start trade monitor: {e}")
    
    # Start price collector in background
    try:
        from src.services.price_collector_service import get_price_collector
        # Collect price data every 1 second for enabled symbols
        collector = get_price_collector(collection_interval=1)
        collector.start()
        app.logger.info("[OK] Price collector started")
    except Exception as e:
        app.logger.error(f"Failed to start price collector: {e}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=settings.DEBUG
    )
