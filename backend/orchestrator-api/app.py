"""
KredMitra Orchestrator API
Main Flask application for orchestrating microservices and handling credit scoring requests.
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import logging
from datetime import datetime
import requests
import json
from typing import Dict, Any, List

# Import routes
from routes.application_routes import application_bp

# Import services
from services.bhashini_service import BhashiniService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    
    # Enable CORS for all domains and routes
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"]
        }
    })
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'kredmitra-secret-key-dev')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.config['BHASHINI_API_KEY'] = os.environ.get('BHASHINI_API_KEY', '')
    
    # Register blueprints
    app.register_blueprint(application_bp, url_prefix='/api/v1')
    
    # Initialize services
    bhashini_service = BhashiniService(app.config.get('BHASHINI_API_KEY'))
    app.bhashini_service = bhashini_service
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'KredMitra Orchestrator API',
            'version': '1.0.0'
        })
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint with API information."""
        return jsonify({
            'message': 'KredMitra Orchestrator API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api/v1',
                'applications': '/api/v1/applications',
                'score': '/api/v1/score',
                'translate': '/api/v1/translate'
            },
            'documentation': 'https://github.com/Nisanth-2025/KredMitra'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # Orchestration endpoint for agent communication
    @app.route('/api/v1/orchestrate', methods=['POST'])
    def orchestrate_agents():
        """
        Orchestrate communication between different agents.
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            agent_type = data.get('agent_type')
            payload = data.get('payload', {})
            
            if not agent_type:
                return jsonify({'error': 'Agent type is required'}), 400
            
            # Agent service URLs (can be configured via environment variables)
            agent_urls = {
                'fraud_detector': os.environ.get('FRAUD_DETECTOR_URL', 'http://localhost:5001'),
                'feature_extractor': os.environ.get('FEATURE_EXTRACTOR_URL', 'http://localhost:5002'),
                'scoring': os.environ.get('SCORING_URL', 'http://localhost:5003'),
                'rag_coach': os.environ.get('RAG_COACH_URL', 'http://localhost:5004'),
                'blockchain_logger': os.environ.get('BLOCKCHAIN_LOGGER_URL', 'http://localhost:5005')
            }
            
            if agent_type not in agent_urls:
                return jsonify({'error': f'Unknown agent type: {agent_type}'}), 400
            
            # Forward request to appropriate agent
            agent_url = agent_urls[agent_type]
            
            try:
                response = requests.post(
                    f"{agent_url}/process",
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    return jsonify({
                        'success': True,
                        'agent_type': agent_type,
                        'result': response.json()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'agent_type': agent_type,
                        'error': f'Agent returned status {response.status_code}'
                    }), response.status_code
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"Agent {agent_type} is not available")
                return jsonify({
                    'success': False,
                    'agent_type': agent_type,
                    'error': 'Agent service is not available',
                    'fallback_result': {
                        'status': 'service_unavailable',
                        'message': f'{agent_type} service is currently unavailable'
                    }
                })
            except requests.exceptions.Timeout:
                return jsonify({
                    'success': False,
                    'agent_type': agent_type,
                    'error': 'Agent request timed out'
                }), 504
                
        except Exception as e:
            logger.error(f"Error in orchestrate_agents: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting KredMitra Orchestrator API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )