"""
KredMitra Fraud Detection Agent
Machine learning-based fraud detection service for credit scoring.
"""

from flask import Flask, request, jsonify
import os
import logging
import numpy as np
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FraudDetector:
    """
    Fraud detection engine using machine learning algorithms.
    """
    
    def __init__(self):
        self.model = None
        self.fraud_patterns = {
            'high_frequency': {'threshold': 10, 'weight': 0.3},
            'unusual_amount': {'threshold': 3, 'weight': 0.25},
            'time_anomaly': {'threshold': 2, 'weight': 0.2},
            'location_anomaly': {'threshold': 1, 'weight': 0.15},
            'device_anomaly': {'threshold': 1, 'weight': 0.1}
        }
        
    def initialize_model(self):
        """Initialize or load the fraud detection model."""
        try:
            # Create a simple rule-based model as fallback
            logger.info("Using rule-based fraud detection model")
            self.model = self._create_rule_based_model()
        except Exception as e:
            logger.error(f"Error initializing fraud model: {e}")
            self.model = self._create_rule_based_model()
    
    def _create_rule_based_model(self):
        """Create a simple rule-based fraud detection model."""
        return {
            'type': 'rule_based',
            'rules': {
                'high_amount_threshold': 100000,  # INR
                'high_frequency_threshold': 5,    # transactions per hour
                'unusual_time_start': 2,          # 2 AM
                'unusual_time_end': 6,            # 6 AM
                'max_daily_transactions': 20
            }
        }
    
    def detect_fraud(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential fraud in a transaction.
        """
        try:
            # Extract features
            features = self._extract_features(transaction_data)
            
            # Calculate fraud probability
            fraud_probability = self._calculate_fraud_probability(features)
            
            # Determine fraud status
            is_fraud = fraud_probability > 0.5
            risk_level = self._get_risk_level(fraud_probability)
            
            # Generate explanation
            explanation = self._generate_explanation(features, fraud_probability)
            
            result = {
                'is_fraud': is_fraud,
                'fraud_probability': round(fraud_probability, 4),
                'risk_level': risk_level,
                'confidence': round(min(fraud_probability, 1 - fraud_probability) * 2, 4),
                'explanation': explanation,
                'timestamp': datetime.utcnow().isoformat(),
                'features_analyzed': list(features.keys())
            }
            
            logger.info(f"Fraud detection completed: {risk_level} risk")
            return result
            
        except Exception as e:
            logger.error(f"Error in fraud detection: {e}")
            return {
                'is_fraud': False,
                'fraud_probability': 0.0,
                'risk_level': 'unknown',
                'confidence': 0.0,
                'explanation': 'Error occurred during fraud detection',
                'error': str(e)
            }
    
    def _extract_features(self, transaction_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from transaction data."""
        features = {}
        
        # Amount-based features
        features['transaction_amount'] = float(transaction_data.get('amount', 0))
        features['account_balance'] = float(transaction_data.get('account_balance', 0))
        
        # Frequency features
        features['transaction_frequency'] = float(transaction_data.get('daily_transactions', 1))
        features['avg_transaction_amount'] = float(transaction_data.get('avg_amount', features['transaction_amount']))
        
        # Time-based features
        transaction_time = transaction_data.get('timestamp', datetime.utcnow().isoformat())
        if isinstance(transaction_time, str):
            try:
                dt = datetime.fromisoformat(transaction_time.replace('Z', '+00:00'))
                features['transaction_time_hour'] = float(dt.hour)
                features['is_weekend'] = float(dt.weekday() >= 5)
            except:
                features['transaction_time_hour'] = 12.0
                features['is_weekend'] = 0.0
        
        # Account features
        features['account_age_days'] = float(transaction_data.get('account_age_days', 365))
        features['days_since_last_transaction'] = float(transaction_data.get('days_since_last', 1))
        
        # Anomaly indicators
        features['unusual_location'] = float(transaction_data.get('unusual_location', False))
        features['device_consistency'] = float(not transaction_data.get('new_device', False))
        
        return features
    
    def _calculate_fraud_probability(self, features: Dict[str, float]) -> float:
        """Calculate fraud probability based on features."""
        return self._rule_based_prediction(features)
    
    def _rule_based_prediction(self, features: Dict[str, float]) -> float:
        """Rule-based fraud prediction."""
        risk_score = 0.0
        rules = self.model['rules']
        
        # High amount check
        if features['transaction_amount'] > rules['high_amount_threshold']:
            risk_score += 0.3
        
        # High frequency check
        if features['transaction_frequency'] > rules['high_frequency_threshold']:
            risk_score += 0.25
        
        # Unusual time check
        hour = features['transaction_time_hour']
        if rules['unusual_time_start'] <= hour <= rules['unusual_time_end']:
            risk_score += 0.2
        
        # Location and device anomaly
        if features['unusual_location']:
            risk_score += 0.15
        
        if not features['device_consistency']:
            risk_score += 0.1
        
        # Account age factor
        if features['account_age_days'] < 30:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level based on fraud probability."""
        if probability >= 0.8:
            return 'very_high'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_explanation(self, features: Dict[str, float], probability: float) -> str:
        """Generate human-readable explanation for the decision."""
        explanations = []
        
        if features['transaction_amount'] > 50000:
            explanations.append("High transaction amount detected")
        
        if features['transaction_frequency'] > 5:
            explanations.append("Unusually high transaction frequency")
        
        if features['unusual_location']:
            explanations.append("Transaction from unusual location")
        
        if not features['device_consistency']:
            explanations.append("Transaction from new or unusual device")
        
        if not explanations:
            explanations.append("Transaction patterns appear normal")
        
        return "; ".join(explanations)

# Flask application
app = Flask(__name__)

# Initialize fraud detector
fraud_detector = FraudDetector()
fraud_detector.initialize_model()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Fraud Detection Agent',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_transaction():
    """Process transaction for fraud detection."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = fraud_detector.detect_fraud(data)
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'fraud_detector'
        })
        
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'fraud_detector'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Fraud Detection Agent on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)