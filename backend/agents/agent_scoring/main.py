"""
KredMitra Credit Scoring Agent
Advanced credit scoring system using multiple algorithms and data sources.
"""

from flask import Flask, request, jsonify
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreditScorer:
    """
    Credit scoring engine that calculates creditworthiness based on multiple factors.
    """
    
    def __init__(self):
        self.scoring_models = {
            'traditional': {
                'weight': 0.4,
                'factors': ['income', 'employment', 'credit_history', 'debt_ratio']
            },
            'alternative': {
                'weight': 0.3,
                'factors': ['digital_footprint', 'transaction_patterns', 'social_connections']
            },
            'behavioral': {
                'weight': 0.3,
                'factors': ['payment_behavior', 'financial_discipline', 'risk_appetite']
            }
        }
        
        self.score_ranges = {
            'excellent': (750, 850),
            'good': (650, 749),
            'fair': (550, 649),
            'poor': (450, 549),
            'very_poor': (300, 449)
        }
        
    def calculate_credit_score(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive credit score for an applicant.
        
        Args:
            applicant_data: Dictionary containing applicant information
            
        Returns:
            Dictionary with credit score and analysis
        """
        try:
            # Calculate individual model scores
            traditional_score = self._calculate_traditional_score(applicant_data)
            alternative_score = self._calculate_alternative_score(applicant_data)
            behavioral_score = self._calculate_behavioral_score(applicant_data)
            
            # Calculate weighted final score
            final_score = (
                traditional_score * self.scoring_models['traditional']['weight'] +
                alternative_score * self.scoring_models['alternative']['weight'] +
                behavioral_score * self.scoring_models['behavioral']['weight']
            )
            
            # Determine credit rating
            credit_rating = self._get_credit_rating(final_score)
            
            # Calculate risk assessment
            risk_assessment = self._assess_risk(final_score, applicant_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(final_score, applicant_data)
            
            result = {
                'credit_score': round(final_score),
                'credit_rating': credit_rating,
                'score_breakdown': {
                    'traditional': round(traditional_score),
                    'alternative': round(alternative_score),
                    'behavioral': round(behavioral_score)
                },
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'score_factors': self._get_score_factors(applicant_data),
                'timestamp': datetime.utcnow().isoformat(),
                'valid_until': (datetime.utcnow() + timedelta(days=90)).isoformat()
            }
            
            logger.info(f"Credit score calculated: {final_score} ({credit_rating})")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating credit score: {e}")
            return {
                'credit_score': 0,
                'credit_rating': 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_traditional_score(self, data: Dict[str, Any]) -> float:
        """Calculate traditional credit score based on standard factors."""
        score = 300  # Base score
        
        # Income factor (0-150 points)
        monthly_income = data.get('monthly_income', 0)
        if monthly_income >= 100000:
            score += 150
        elif monthly_income >= 50000:
            score += 120
        elif monthly_income >= 25000:
            score += 90
        elif monthly_income >= 15000:
            score += 60
        else:
            score += 30
        
        # Employment stability (0-100 points)
        employment_years = data.get('employment_years', 0)
        if employment_years >= 5:
            score += 100
        elif employment_years >= 3:
            score += 80
        elif employment_years >= 1:
            score += 60
        else:
            score += 30
        
        # Credit history (0-120 points)
        credit_history_years = data.get('credit_history_years', 0)
        payment_defaults = data.get('payment_defaults', 0)
        
        if credit_history_years >= 5 and payment_defaults == 0:
            score += 120
        elif credit_history_years >= 3 and payment_defaults <= 1:
            score += 90
        elif credit_history_years >= 1 and payment_defaults <= 2:
            score += 60
        else:
            score += 20
        
        # Debt-to-income ratio (0-80 points)
        debt_to_income = data.get('debt_to_income_ratio', 0)
        if debt_to_income <= 0.2:
            score += 80
        elif debt_to_income <= 0.4:
            score += 60
        elif debt_to_income <= 0.6:
            score += 40
        else:
            score += 10
        
        return min(score, 750)
    
    def _calculate_alternative_score(self, data: Dict[str, Any]) -> float:
        """Calculate alternative credit score using non-traditional data."""
        score = 300  # Base score
        
        # Digital footprint (0-100 points)
        has_smartphone = data.get('has_smartphone', False)
        internet_usage_years = data.get('internet_usage_years', 0)
        social_media_presence = data.get('social_media_presence', False)
        
        if has_smartphone and internet_usage_years >= 3 and social_media_presence:
            score += 100
        elif has_smartphone and internet_usage_years >= 1:
            score += 70
        elif has_smartphone:
            score += 40
        else:
            score += 10
        
        # Transaction patterns (0-120 points)
        monthly_transactions = data.get('monthly_transactions', 0)
        regular_savings = data.get('regular_savings', False)
        digital_payments = data.get('uses_digital_payments', False)
        
        if monthly_transactions >= 50 and regular_savings and digital_payments:
            score += 120
        elif monthly_transactions >= 20 and digital_payments:
            score += 90
        elif monthly_transactions >= 10:
            score += 60
        else:
            score += 20
        
        # Education and profession (0-80 points)
        education_level = data.get('education_level', 'unknown')
        profession_stability = data.get('profession_stability', 'low')
        
        if education_level in ['graduate', 'postgraduate'] and profession_stability == 'high':
            score += 80
        elif education_level in ['graduate', 'undergraduate']:
            score += 60
        elif education_level == 'high_school':
            score += 40
        else:
            score += 20
        
        return min(score, 700)
    
    def _calculate_behavioral_score(self, data: Dict[str, Any]) -> float:
        """Calculate behavioral score based on financial behavior patterns."""
        score = 300  # Base score
        
        # Payment behavior (0-150 points)
        on_time_payments = data.get('on_time_payment_percentage', 0)
        if on_time_payments >= 95:
            score += 150
        elif on_time_payments >= 85:
            score += 120
        elif on_time_payments >= 70:
            score += 90
        elif on_time_payments >= 50:
            score += 60
        else:
            score += 20
        
        # Financial discipline (0-100 points)
        savings_rate = data.get('savings_rate', 0)
        budget_tracking = data.get('tracks_budget', False)
        
        if savings_rate >= 0.2 and budget_tracking:
            score += 100
        elif savings_rate >= 0.1:
            score += 70
        elif savings_rate > 0:
            score += 50
        else:
            score += 20
        
        # Risk management (0-50 points)
        has_insurance = data.get('has_insurance', False)
        emergency_fund = data.get('has_emergency_fund', False)
        
        if has_insurance and emergency_fund:
            score += 50
        elif has_insurance or emergency_fund:
            score += 30
        else:
            score += 10
        
        return min(score, 650)
    
    def _get_credit_rating(self, score: float) -> str:
        """Get credit rating based on score."""
        for rating, (min_score, max_score) in self.score_ranges.items():
            if min_score <= score <= max_score:
                return rating
        return 'unknown'
    
    def _assess_risk(self, score: float, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess lending risk based on score and other factors."""
        if score >= 700:
            risk_level = 'low'
            default_probability = 0.02
        elif score >= 600:
            risk_level = 'medium'
            default_probability = 0.08
        elif score >= 500:
            risk_level = 'high'
            default_probability = 0.20
        else:
            risk_level = 'very_high'
            default_probability = 0.40
        
        # Adjust for additional risk factors
        if data.get('debt_to_income_ratio', 0) > 0.6:
            default_probability *= 1.5
        
        if data.get('employment_years', 0) < 1:
            default_probability *= 1.3
        
        return {
            'risk_level': risk_level,
            'default_probability': round(min(default_probability, 1.0), 4),
            'recommended_interest_rate': self._calculate_interest_rate(score, default_probability),
            'maximum_loan_amount': self._calculate_max_loan(data, score)
        }
    
    def _calculate_interest_rate(self, score: float, default_prob: float) -> float:
        """Calculate recommended interest rate based on risk."""
        base_rate = 8.0  # Base interest rate
        risk_premium = default_prob * 20  # Risk-based premium
        
        if score >= 750:
            rate = base_rate + 1.0
        elif score >= 700:
            rate = base_rate + 2.0
        elif score >= 650:
            rate = base_rate + 4.0
        elif score >= 600:
            rate = base_rate + 6.0
        else:
            rate = base_rate + 10.0
        
        return round(min(rate + risk_premium, 36.0), 2)  # Cap at 36%
    
    def _calculate_max_loan(self, data: Dict[str, Any], score: float) -> int:
        """Calculate maximum recommended loan amount."""
        monthly_income = data.get('monthly_income', 0)
        debt_to_income = data.get('debt_to_income_ratio', 0)
        
        # Available income for new debt
        available_income = monthly_income * (0.6 - debt_to_income)  # Keep DTI under 60%
        
        if available_income <= 0:
            return 0
        
        # Loan multiplier based on credit score
        if score >= 750:
            multiplier = 60  # 60 months
        elif score >= 700:
            multiplier = 48
        elif score >= 650:
            multiplier = 36
        elif score >= 600:
            multiplier = 24
        else:
            multiplier = 12
        
        max_loan = available_income * multiplier
        return int(max_loan)
    
    def _generate_recommendations(self, score: float, data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations for improving credit score."""
        recommendations = []
        
        if score < 650:
            recommendations.append("Focus on making all payments on time to improve payment history")
            recommendations.append("Reduce debt-to-income ratio by paying down existing debts")
        
        if data.get('credit_history_years', 0) < 2:
            recommendations.append("Build credit history by maintaining active credit accounts")
        
        if not data.get('has_emergency_fund', False):
            recommendations.append("Build an emergency fund covering 3-6 months of expenses")
        
        if data.get('savings_rate', 0) < 0.1:
            recommendations.append("Increase savings rate to at least 10% of monthly income")
        
        if not data.get('uses_digital_payments', False):
            recommendations.append("Start using digital payment methods to build transaction history")
        
        if score >= 750:
            recommendations.append("Excellent credit score! You qualify for the best lending rates")
        
        return recommendations
    
    def _get_score_factors(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Get factors that influenced the credit score."""
        factors = {}
        
        # Positive factors
        if data.get('monthly_income', 0) >= 50000:
            factors['income'] = 'positive'
        if data.get('employment_years', 0) >= 3:
            factors['employment_stability'] = 'positive'
        if data.get('on_time_payment_percentage', 0) >= 90:
            factors['payment_history'] = 'positive'
        
        # Negative factors
        if data.get('debt_to_income_ratio', 0) > 0.5:
            factors['debt_level'] = 'negative'
        if data.get('payment_defaults', 0) > 0:
            factors['defaults'] = 'negative'
        if data.get('credit_history_years', 0) < 2:
            factors['credit_history'] = 'negative'
        
        return factors

# Flask application
app = Flask(__name__)

# Initialize credit scorer
credit_scorer = CreditScorer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Credit Scoring Agent',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_application():
    """Process credit scoring request."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = credit_scorer.calculate_credit_score(data)
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'credit_scoring'
        })
        
    except Exception as e:
        logger.error(f"Error processing credit score: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'credit_scoring'
        }), 500

@app.route('/score_range', methods=['GET'])
def get_score_ranges():
    """Get credit score ranges and their meanings."""
    return jsonify({
        'score_ranges': credit_scorer.score_ranges,
        'scoring_models': credit_scorer.scoring_models
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Credit Scoring Agent on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
