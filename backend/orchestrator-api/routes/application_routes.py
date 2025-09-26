"""
KredMitra Application Routes
Routes for handling credit application processing and scoring requests.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime
import requests
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Create blueprint
application_bp = Blueprint('application', __name__)

@application_bp.route('/applications', methods=['POST'])
def submit_application():
    """Submit a new credit application for processing."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No application data provided'}), 400
        
        # Validate required fields
        required_fields = ['applicant_id', 'personal_info', 'financial_info']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add processing metadata
        data['application_id'] = f"APP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{data['applicant_id']}"
        data['submitted_at'] = datetime.utcnow().isoformat()
        data['status'] = 'processing'
        
        # Process through the pipeline
        result = process_application_pipeline(data)
        
        return jsonify({
            'success': True,
            'application_id': data['application_id'],
            'result': result,
            'submitted_at': data['submitted_at']
        })
        
    except Exception as e:
        logger.error(f"Error submitting application: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application_bp.route('/applications/<application_id>', methods=['GET'])
def get_application_status(application_id: str):
    """Get the status of a specific application."""
    try:
        # In a real implementation, this would query a database
        # For now, return mock status
        return jsonify({
            'application_id': application_id,
            'status': 'completed',
            'last_updated': datetime.utcnow().isoformat(),
            'processing_stages': {
                'feature_extraction': 'completed',
                'fraud_detection': 'completed',
                'credit_scoring': 'completed',
                'final_decision': 'completed'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting application status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application_bp.route('/score', methods=['POST'])
def calculate_credit_score():
    """Calculate credit score for an applicant."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract features first
        feature_result = call_agent('feature_extractor', data)
        if not feature_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Feature extraction failed',
                'details': feature_result
            }), 500
        
        # Calculate credit score
        features = feature_result['result']['features']
        scoring_result = call_agent('scoring', features)
        
        if not scoring_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Credit scoring failed',
                'details': scoring_result
            }), 500
        
        # Log to blockchain
        log_data = {
            'applicant_id': data.get('applicant_id', 'anonymous'),
            'log_type': 'credit_assessment',
            **scoring_result['result']
        }
        blockchain_result = call_agent('blockchain_logger', log_data)
        
        return jsonify({
            'success': True,
            'credit_score': scoring_result['result'],
            'blockchain_logged': blockchain_result.get('success', False),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating credit score: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application_bp.route('/fraud_check', methods=['POST'])
def check_fraud():
    """Check for potential fraud in application data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Call fraud detection agent
        fraud_result = call_agent('fraud_detector', data)
        
        if not fraud_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Fraud detection failed',
                'details': fraud_result
            }), 500
        
        # Log to blockchain
        log_data = {
            'applicant_id': data.get('applicant_id', 'anonymous'),
            'log_type': 'fraud_detection',
            **fraud_result['result']
        }
        blockchain_result = call_agent('blockchain_logger', log_data)
        
        return jsonify({
            'success': True,
            'fraud_check': fraud_result['result'],
            'blockchain_logged': blockchain_result.get('success', False),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking fraud: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application_bp.route('/guidance', methods=['POST'])
def get_financial_guidance():
    """Get personalized financial guidance."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No query provided'}), 400
        
        # Call RAG coach agent
        guidance_result = call_agent('rag_coach', data)
        
        if not guidance_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Guidance generation failed',
                'details': guidance_result
            }), 500
        
        return jsonify({
            'success': True,
            'guidance': guidance_result['result'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting guidance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application_bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text using Bhashini service."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No translation data provided'}), 400
        
        text = data.get('text')
        source_lang = data.get('source_language', 'en')
        target_lang = data.get('target_language', 'hi')
        
        if not text:
            return jsonify({'error': 'No text provided for translation'}), 400
        
        # Use Bhashini service
        bhashini_service = current_app.bhashini_service
        translation_result = bhashini_service.translate(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translation_result.get('translated_text', text),
            'source_language': source_lang,
            'target_language': target_lang,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def process_application_pipeline(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process application through the complete pipeline."""
    pipeline_results = {}
    
    try:
        # Step 1: Feature Extraction
        logger.info("Starting feature extraction...")
        feature_result = call_agent('feature_extractor', data)
        pipeline_results['feature_extraction'] = feature_result
        
        if not feature_result.get('success'):
            return {'error': 'Feature extraction failed', 'stage': 'feature_extraction'}
        
        # Step 2: Fraud Detection
        logger.info("Starting fraud detection...")
        fraud_result = call_agent('fraud_detector', data)
        pipeline_results['fraud_detection'] = fraud_result
        
        if fraud_result.get('success') and fraud_result['result'].get('is_fraud'):
            # High fraud risk - stop processing
            pipeline_results['final_decision'] = {
                'decision': 'rejected',
                'reason': 'High fraud risk detected',
                'fraud_probability': fraud_result['result'].get('fraud_probability')
            }
            return pipeline_results
        
        # Step 3: Credit Scoring
        logger.info("Starting credit scoring...")
        features = feature_result['result']['features']
        scoring_result = call_agent('scoring', features)
        pipeline_results['credit_scoring'] = scoring_result
        
        if not scoring_result.get('success'):
            return {'error': 'Credit scoring failed', 'stage': 'credit_scoring'}
        
        # Step 4: Final Decision
        credit_score = scoring_result['result']['credit_score']
        risk_level = scoring_result['result']['risk_assessment']['risk_level']
        
        final_decision = make_loan_decision(credit_score, risk_level, data)
        pipeline_results['final_decision'] = final_decision
        
        # Step 5: Blockchain Logging
        logger.info("Logging to blockchain...")
        log_data = {
            'applicant_id': data.get('applicant_id'),
            'log_type': 'loan_decision',
            **final_decision
        }
        blockchain_result = call_agent('blockchain_logger', log_data)
        pipeline_results['blockchain_logging'] = blockchain_result
        
        return pipeline_results
        
    except Exception as e:
        logger.error(f"Pipeline processing error: {e}")
        return {'error': str(e), 'stage': 'pipeline'}

def call_agent(agent_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Call a specific agent service."""
    agent_ports = {
        'fraud_detector': 5001,
        'feature_extractor': 5002,
        'scoring': 5003,
        'rag_coach': 5004,
        'blockchain_logger': 5005
    }
    
    if agent_type not in agent_ports:
        return {'success': False, 'error': f'Unknown agent type: {agent_type}'}
    
    try:
        port = agent_ports[agent_type]
        url = f"http://localhost:{port}/process"
        
        response = requests.post(
            url,
            json=data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Agent {agent_type} returned status {response.status_code}")
            return {
                'success': False,
                'error': f'Agent returned status {response.status_code}',
                'agent_response': response.text
            }
            
    except requests.exceptions.ConnectionError:
        logger.warning(f"Agent {agent_type} is not available")
        return {
            'success': False,
            'error': f'Agent {agent_type} service is not available',
            'fallback_result': create_fallback_result(agent_type, data)
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': f'Agent {agent_type} request timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error calling agent {agent_type}: {str(e)}'
        }

def make_loan_decision(credit_score: int, risk_level: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Make final loan decision based on credit score and other factors."""
    
    loan_amount_requested = application_data.get('loan_amount', 0)
    
    # Decision logic
    if credit_score >= 750:
        decision = 'approved'
        conditions = []
        max_amount = loan_amount_requested
        interest_rate = 8.5
    elif credit_score >= 650:
        decision = 'approved'
        conditions = ['Salary certificate required', 'Co-signer recommended']
        max_amount = min(loan_amount_requested, loan_amount_requested * 0.8)
        interest_rate = 12.0
    elif credit_score >= 550:
        decision = 'conditional_approval'
        conditions = ['Higher down payment required', 'Co-signer mandatory', 'Additional documentation needed']
        max_amount = min(loan_amount_requested, loan_amount_requested * 0.6)
        interest_rate = 16.0
    else:
        decision = 'rejected'
        conditions = ['Credit score too low', 'Consider credit improvement measures']
        max_amount = 0
        interest_rate = 0
    
    return {
        'decision': decision,
        'credit_score': credit_score,
        'risk_level': risk_level,
        'approved_amount': max_amount,
        'interest_rate': interest_rate,
        'conditions': conditions,
        'decision_timestamp': datetime.utcnow().isoformat(),
        'valid_until': (datetime.utcnow().timestamp() + (30 * 24 * 60 * 60))  # 30 days
    }

def create_fallback_result(agent_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create fallback result when agent is unavailable."""
    
    if agent_type == 'fraud_detector':
        return {
            'is_fraud': False,
            'fraud_probability': 0.1,
            'risk_level': 'low',
            'explanation': 'Fallback: Basic fraud check passed'
        }
    elif agent_type == 'feature_extractor':
        return {
            'features': {
                'demographic': {'age': data.get('age', 30)},
                'financial': {'monthly_income': data.get('monthly_income', 50000)},
                'quality': {'completeness_score': 60}
            }
        }
    elif agent_type == 'scoring':
        return {
            'credit_score': 600,
            'credit_rating': 'fair',
            'risk_assessment': {'risk_level': 'medium'},
            'fallback': True
        }
    elif agent_type == 'blockchain_logger':
        return {
            'success': True,
            'storage': 'fallback_cache',
            'note': 'Stored locally, will sync when blockchain is available'
        }
    else:
        return {'fallback': True, 'message': 'Service unavailable'}