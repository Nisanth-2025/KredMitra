"""
KredMitra Feature Extraction Agent
Extracts and processes features from various data sources for credit assessment.
"""

from flask import Flask, request, jsonify
import os
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Feature extraction engine that processes raw data into structured features
    for credit scoring and risk assessment.
    """
    
    def __init__(self):
        self.feature_categories = {
            'demographic': ['age', 'gender', 'marital_status', 'dependents', 'education'],
            'financial': ['income', 'expenses', 'assets', 'liabilities', 'savings'],
            'employment': ['job_type', 'employment_duration', 'company_size', 'salary_stability'],
            'behavioral': ['transaction_patterns', 'payment_history', 'spending_habits'],
            'digital': ['digital_footprint', 'device_usage', 'online_behavior'],
            'social': ['references', 'community_connections', 'social_validation']
        }
        
    def extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured features from raw applicant data.
        
        Args:
            raw_data: Raw data from various sources
            
        Returns:
            Dictionary with extracted and processed features
        """
        try:
            extracted_features = {}
            
            # Extract demographic features
            extracted_features['demographic'] = self._extract_demographic_features(raw_data)
            
            # Extract financial features
            extracted_features['financial'] = self._extract_financial_features(raw_data)
            
            # Extract employment features
            extracted_features['employment'] = self._extract_employment_features(raw_data)
            
            # Extract behavioral features
            extracted_features['behavioral'] = self._extract_behavioral_features(raw_data)
            
            # Extract digital features
            extracted_features['digital'] = self._extract_digital_features(raw_data)
            
            # Extract social features
            extracted_features['social'] = self._extract_social_features(raw_data)
            
            # Calculate derived features
            extracted_features['derived'] = self._calculate_derived_features(extracted_features)
            
            # Feature quality assessment
            extracted_features['quality'] = self._assess_feature_quality(extracted_features)
            
            result = {
                'features': extracted_features,
                'feature_count': self._count_features(extracted_features),
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'data_sources': list(raw_data.keys()),
                'processing_notes': self._get_processing_notes(raw_data, extracted_features)
            }
            
            logger.info(f"Feature extraction completed: {result['feature_count']} features extracted")
            return result
            
        except Exception as e:
            logger.error(f"Error in feature extraction: {e}")
            return {
                'features': {},
                'error': str(e),
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
    
    def _extract_demographic_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract demographic features."""
        features = {}
        
        # Age calculation
        if 'date_of_birth' in data:
            try:
                dob = datetime.fromisoformat(data['date_of_birth'].replace('Z', '+00:00'))
                age = (datetime.utcnow() - dob).days // 365
                features['age'] = age
                features['age_group'] = self._get_age_group(age)
            except:
                features['age'] = data.get('age', 0)
                features['age_group'] = self._get_age_group(features['age'])
        else:
            features['age'] = data.get('age', 0)
            features['age_group'] = self._get_age_group(features['age'])
        
        # Gender
        features['gender'] = data.get('gender', 'unknown').lower()
        
        # Marital status
        features['marital_status'] = data.get('marital_status', 'unknown').lower()
        features['is_married'] = features['marital_status'] in ['married', 'civil_partnership']
        
        # Dependents
        features['dependents_count'] = int(data.get('dependents', 0))
        features['has_dependents'] = features['dependents_count'] > 0
        
        # Education
        education = data.get('education_level', 'unknown').lower()
        features['education_level'] = education
        features['education_score'] = self._calculate_education_score(education)
        
        # Location
        features['city'] = data.get('city', 'unknown')
        features['state'] = data.get('state', 'unknown')
        features['pincode'] = data.get('pincode', 'unknown')
        features['is_metro_city'] = self._is_metro_city(features['city'])
        
        return features
    
    def _extract_financial_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial features."""
        features = {}
        
        # Income features
        features['monthly_income'] = float(data.get('monthly_income', 0))
        features['annual_income'] = features['monthly_income'] * 12
        features['income_source'] = data.get('income_source', 'unknown')
        features['income_stability'] = data.get('income_stability', 'unknown')
        
        # Expense features
        features['monthly_expenses'] = float(data.get('monthly_expenses', 0))
        features['expense_categories'] = data.get('expense_breakdown', {})
        
        # Savings and investments
        features['savings_amount'] = float(data.get('savings', 0))
        features['investment_amount'] = float(data.get('investments', 0))
        features['total_assets'] = features['savings_amount'] + features['investment_amount']
        
        # Debt information
        features['total_debt'] = float(data.get('total_debt', 0))
        features['credit_card_debt'] = float(data.get('credit_card_debt', 0))
        features['loan_emi'] = float(data.get('monthly_emi', 0))
        
        # Financial ratios
        if features['monthly_income'] > 0:
            features['savings_rate'] = features['savings_amount'] / (features['monthly_income'] * 12)
            features['debt_to_income_ratio'] = features['total_debt'] / features['annual_income']
            features['expense_ratio'] = features['monthly_expenses'] / features['monthly_income']
        else:
            features['savings_rate'] = 0
            features['debt_to_income_ratio'] = 0
            features['expense_ratio'] = 0
        
        # Bank account information
        features['bank_account_age_months'] = int(data.get('bank_account_age_months', 0))
        features['has_salary_account'] = data.get('has_salary_account', False)
        features['average_bank_balance'] = float(data.get('average_bank_balance', 0))
        
        return features
    
    def _extract_employment_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract employment-related features."""
        features = {}
        
        # Employment status
        features['employment_status'] = data.get('employment_status', 'unknown')
        features['is_employed'] = features['employment_status'] in ['employed', 'self_employed']
        
        # Job details
        features['job_title'] = data.get('job_title', 'unknown')
        features['company_name'] = data.get('company_name', 'unknown')
        features['company_type'] = data.get('company_type', 'unknown')
        features['industry'] = data.get('industry', 'unknown')
        
        # Employment duration
        features['current_job_months'] = int(data.get('current_job_months', 0))
        features['total_experience_months'] = int(data.get('total_experience_months', 0))
        features['job_stability'] = self._assess_job_stability(features['current_job_months'])
        
        # Company information
        features['company_size'] = data.get('company_size', 'unknown')
        features['is_mnc'] = data.get('is_multinational', False)
        features['company_rating'] = data.get('company_rating', 0)
        
        # Profession categorization
        features['profession_category'] = self._categorize_profession(features['job_title'])
        features['profession_risk_level'] = self._assess_profession_risk(features['profession_category'])
        
        return features
    
    def _extract_behavioral_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract behavioral and transaction features."""
        features = {}
        
        # Payment behavior
        features['payment_history'] = data.get('payment_history', [])
        features['on_time_payments'] = len([p for p in features['payment_history'] if p.get('on_time', False)])
        features['total_payments'] = len(features['payment_history'])
        features['on_time_percentage'] = (features['on_time_payments'] / max(features['total_payments'], 1)) * 100
        
        # Transaction patterns
        transactions = data.get('transactions', [])
        features['monthly_transaction_count'] = len(transactions)
        features['transaction_amounts'] = [float(t.get('amount', 0)) for t in transactions]
        
        if features['transaction_amounts']:
            features['avg_transaction_amount'] = sum(features['transaction_amounts']) / len(features['transaction_amounts'])
            features['max_transaction_amount'] = max(features['transaction_amounts'])
            features['min_transaction_amount'] = min(features['transaction_amounts'])
            features['transaction_variance'] = self._calculate_variance(features['transaction_amounts'])
        else:
            features['avg_transaction_amount'] = 0
            features['max_transaction_amount'] = 0
            features['min_transaction_amount'] = 0
            features['transaction_variance'] = 0
        
        # Spending patterns
        features['spending_categories'] = self._analyze_spending_categories(transactions)
        features['spending_regularity'] = self._assess_spending_regularity(transactions)
        
        # Credit behavior
        features['credit_utilization'] = float(data.get('credit_utilization', 0))
        features['credit_inquiries'] = int(data.get('recent_credit_inquiries', 0))
        features['credit_accounts'] = int(data.get('active_credit_accounts', 0))
        
        return features
    
    def _extract_digital_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract digital footprint features."""
        features = {}
        
        # Device and connectivity
        features['has_smartphone'] = data.get('has_smartphone', False)
        features['internet_usage_years'] = int(data.get('internet_usage_years', 0))
        features['uses_mobile_banking'] = data.get('uses_mobile_banking', False)
        features['uses_digital_payments'] = data.get('uses_digital_payments', False)
        
        # Online presence
        features['email_age_years'] = int(data.get('email_age_years', 0))
        features['social_media_accounts'] = int(data.get('social_media_accounts', 0))
        features['has_professional_profile'] = data.get('has_linkedin', False)
        
        # Digital transaction behavior
        features['digital_payment_frequency'] = int(data.get('digital_transactions_monthly', 0))
        features['prefers_digital_payments'] = features['digital_payment_frequency'] > 10
        
        # App usage patterns
        features['financial_apps_used'] = data.get('financial_apps', [])
        features['uses_budgeting_apps'] = 'budgeting' in str(features['financial_apps_used']).lower()
        
        return features
    
    def _extract_social_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract social and community features."""
        features = {}
        
        # References and connections
        references = data.get('references', [])
        features['reference_count'] = len(references)
        features['has_professional_references'] = any(r.get('type') == 'professional' for r in references)
        features['has_family_references'] = any(r.get('type') == 'family' for r in references)
        
        # Community involvement
        features['community_memberships'] = data.get('community_memberships', [])
        features['is_community_active'] = len(features['community_memberships']) > 0
        features['has_professional_memberships'] = any('professional' in str(m).lower() for m in features['community_memberships'])
        
        # Social validation
        features['social_validation_score'] = self._calculate_social_validation(data)
        features['network_quality'] = self._assess_network_quality(references)
        
        return features
    
    def _calculate_derived_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived features from base features."""
        derived = {}
        
        # Financial health indicators
        financial = features.get('financial', {})
        if financial.get('monthly_income', 0) > 0:
            derived['financial_health_score'] = self._calculate_financial_health(financial)
            derived['disposable_income'] = financial['monthly_income'] - financial['monthly_expenses']
            derived['liquidity_ratio'] = financial['savings_amount'] / max(financial['monthly_expenses'], 1)
        
        # Stability indicators
        employment = features.get('employment', {})
        derived['career_stability_score'] = self._calculate_career_stability(employment)
        
        # Risk indicators
        behavioral = features.get('behavioral', {})
        derived['behavioral_risk_score'] = self._calculate_behavioral_risk(behavioral)
        
        # Digital maturity
        digital = features.get('digital', {})
        derived['digital_maturity_score'] = self._calculate_digital_maturity(digital)
        
        return derived
    
    def _assess_feature_quality(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality and completeness of extracted features."""
        quality = {}
        
        total_features = self._count_features(features)
        complete_features = self._count_complete_features(features)
        
        quality['completeness_score'] = (complete_features / max(total_features, 1)) * 100
        quality['total_features'] = total_features
        quality['complete_features'] = complete_features
        quality['missing_critical_features'] = self._identify_missing_critical_features(features)
        quality['data_quality_issues'] = self._identify_data_quality_issues(features)
        
        return quality
    
    # Helper methods
    def _get_age_group(self, age: int) -> str:
        """Categorize age into groups."""
        if age < 25:
            return 'young'
        elif age < 35:
            return 'young_adult'
        elif age < 50:
            return 'middle_aged'
        elif age < 65:
            return 'mature'
        else:
            return 'senior'
    
    def _calculate_education_score(self, education: str) -> int:
        """Calculate education score."""
        education_scores = {
            'postgraduate': 5,
            'graduate': 4,
            'undergraduate': 3,
            'diploma': 3,
            'high_school': 2,
            'secondary': 1,
            'unknown': 0
        }
        return education_scores.get(education.lower(), 0)
    
    def _is_metro_city(self, city: str) -> bool:
        """Check if city is a metro city."""
        metro_cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 'ahmedabad']
        return city.lower() in metro_cities
    
    def _assess_job_stability(self, months: int) -> str:
        """Assess job stability based on tenure."""
        if months >= 36:
            return 'very_stable'
        elif months >= 24:
            return 'stable'
        elif months >= 12:
            return 'moderate'
        elif months >= 6:
            return 'low'
        else:
            return 'very_low'
    
    def _categorize_profession(self, job_title: str) -> str:
        """Categorize profession into standard categories."""
        job_title = job_title.lower()
        
        if any(word in job_title for word in ['engineer', 'developer', 'architect', 'analyst']):
            return 'technology'
        elif any(word in job_title for word in ['doctor', 'nurse', 'medical']):
            return 'healthcare'
        elif any(word in job_title for word in ['teacher', 'professor', 'education']):
            return 'education'
        elif any(word in job_title for word in ['manager', 'director', 'executive']):
            return 'management'
        elif any(word in job_title for word in ['sales', 'marketing']):
            return 'sales_marketing'
        else:
            return 'other'
    
    def _assess_profession_risk(self, category: str) -> str:
        """Assess profession risk level."""
        risk_levels = {
            'technology': 'low',
            'healthcare': 'low',
            'education': 'low',
            'management': 'medium',
            'sales_marketing': 'medium',
            'other': 'high'
        }
        return risk_levels.get(category, 'high')
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _analyze_spending_categories(self, transactions: List[Dict]) -> Dict[str, float]:
        """Analyze spending by categories."""
        categories = {}
        for transaction in transactions:
            category = transaction.get('category', 'other')
            amount = float(transaction.get('amount', 0))
            categories[category] = categories.get(category, 0) + amount
        return categories
    
    def _assess_spending_regularity(self, transactions: List[Dict]) -> str:
        """Assess regularity of spending patterns."""
        if len(transactions) < 5:
            return 'insufficient_data'
        
        # Analyze transaction frequency
        amounts = [float(t.get('amount', 0)) for t in transactions]
        variance = self._calculate_variance(amounts)
        mean = sum(amounts) / len(amounts)
        
        if variance / max(mean, 1) < 0.5:
            return 'very_regular'
        elif variance / max(mean, 1) < 1.0:
            return 'regular'
        elif variance / max(mean, 1) < 2.0:
            return 'moderate'
        else:
            return 'irregular'
    
    def _calculate_social_validation(self, data: Dict[str, Any]) -> float:
        """Calculate social validation score."""
        score = 0
        
        # Reference quality
        references = data.get('references', [])
        score += len(references) * 10
        
        # Community involvement
        memberships = data.get('community_memberships', [])
        score += len(memberships) * 5
        
        # Professional network
        if data.get('has_linkedin', False):
            score += 20
        
        return min(score, 100)
    
    def _assess_network_quality(self, references: List[Dict]) -> str:
        """Assess quality of professional network."""
        if not references:
            return 'none'
        
        professional_refs = sum(1 for r in references if r.get('type') == 'professional')
        
        if professional_refs >= 3:
            return 'excellent'
        elif professional_refs >= 2:
            return 'good'
        elif professional_refs >= 1:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_financial_health(self, financial: Dict[str, Any]) -> float:
        """Calculate overall financial health score."""
        score = 0
        
        # Savings rate
        savings_rate = financial.get('savings_rate', 0)
        if savings_rate >= 0.2:
            score += 30
        elif savings_rate >= 0.1:
            score += 20
        elif savings_rate > 0:
            score += 10
        
        # Debt to income ratio
        debt_ratio = financial.get('debt_to_income_ratio', 0)
        if debt_ratio <= 0.3:
            score += 30
        elif debt_ratio <= 0.5:
            score += 20
        elif debt_ratio <= 0.7:
            score += 10
        
        # Income level
        monthly_income = financial.get('monthly_income', 0)
        if monthly_income >= 100000:
            score += 40
        elif monthly_income >= 50000:
            score += 30
        elif monthly_income >= 25000:
            score += 20
        elif monthly_income >= 15000:
            score += 10
        
        return min(score, 100)
    
    def _calculate_career_stability(self, employment: Dict[str, Any]) -> float:
        """Calculate career stability score."""
        score = 0
        
        # Current job tenure
        months = employment.get('current_job_months', 0)
        if months >= 36:
            score += 40
        elif months >= 24:
            score += 30
        elif months >= 12:
            score += 20
        elif months >= 6:
            score += 10
        
        # Total experience
        total_months = employment.get('total_experience_months', 0)
        if total_months >= 60:
            score += 30
        elif total_months >= 36:
            score += 20
        elif total_months >= 24:
            score += 15
        elif total_months >= 12:
            score += 10
        
        # Company type
        if employment.get('is_mnc', False):
            score += 20
        elif employment.get('company_type') == 'established':
            score += 15
        
        # Industry stability
        stable_industries = ['technology', 'healthcare', 'education', 'banking']
        if employment.get('industry', '').lower() in stable_industries:
            score += 10
        
        return min(score, 100)
    
    def _calculate_behavioral_risk(self, behavioral: Dict[str, Any]) -> float:
        """Calculate behavioral risk score (higher is riskier)."""
        risk = 0
        
        # Payment history
        on_time_percentage = behavioral.get('on_time_percentage', 100)
        if on_time_percentage < 70:
            risk += 40
        elif on_time_percentage < 85:
            risk += 20
        elif on_time_percentage < 95:
            risk += 10
        
        # Credit utilization
        utilization = behavioral.get('credit_utilization', 0)
        if utilization > 0.8:
            risk += 30
        elif utilization > 0.5:
            risk += 20
        elif utilization > 0.3:
            risk += 10
        
        # Credit inquiries
        inquiries = behavioral.get('credit_inquiries', 0)
        if inquiries > 5:
            risk += 20
        elif inquiries > 3:
            risk += 10
        
        return min(risk, 100)
    
    def _calculate_digital_maturity(self, digital: Dict[str, Any]) -> float:
        """Calculate digital maturity score."""
        score = 0
        
        if digital.get('has_smartphone', False):
            score += 20
        
        if digital.get('uses_mobile_banking', False):
            score += 25
        
        if digital.get('uses_digital_payments', False):
            score += 25
        
        internet_years = digital.get('internet_usage_years', 0)
        if internet_years >= 5:
            score += 20
        elif internet_years >= 3:
            score += 15
        elif internet_years >= 1:
            score += 10
        
        if digital.get('uses_budgeting_apps', False):
            score += 10
        
        return min(score, 100)
    
    def _count_features(self, features: Dict[str, Any]) -> int:
        """Count total number of features."""
        count = 0
        for category, feature_dict in features.items():
            if isinstance(feature_dict, dict):
                count += len(feature_dict)
        return count
    
    def _count_complete_features(self, features: Dict[str, Any]) -> int:
        """Count complete (non-null, non-zero) features."""
        count = 0
        for category, feature_dict in features.items():
            if isinstance(feature_dict, dict):
                for key, value in feature_dict.items():
                    if value not in [None, 0, '', 'unknown', [], {}]:
                        count += 1
        return count
    
    def _identify_missing_critical_features(self, features: Dict[str, Any]) -> List[str]:
        """Identify missing critical features."""
        critical_features = [
            'demographic.age',
            'financial.monthly_income',
            'employment.employment_status',
            'behavioral.on_time_percentage'
        ]
        
        missing = []
        for feature_path in critical_features:
            category, feature_name = feature_path.split('.')
            if category not in features or feature_name not in features[category]:
                missing.append(feature_path)
        
        return missing
    
    def _identify_data_quality_issues(self, features: Dict[str, Any]) -> List[str]:
        """Identify data quality issues."""
        issues = []
        
        # Check for inconsistent data
        financial = features.get('financial', {})
        if financial.get('monthly_income', 0) < financial.get('monthly_expenses', 0):
            issues.append("Income less than expenses - possible data error")
        
        demographic = features.get('demographic', {})
        if demographic.get('age', 0) < 18:
            issues.append("Age below minimum eligibility - possible data error")
        
        return issues
    
    def _get_processing_notes(self, raw_data: Dict[str, Any], features: Dict[str, Any]) -> List[str]:
        """Generate processing notes."""
        notes = []
        
        if 'transactions' in raw_data and len(raw_data['transactions']) > 100:
            notes.append("Large transaction dataset processed - only recent transactions analyzed")
        
        quality = features.get('quality', {})
        if quality.get('completeness_score', 100) < 70:
            notes.append("Low data completeness - scores may be less accurate")
        
        return notes

# Flask application
app = Flask(__name__)

# Initialize feature extractor
feature_extractor = FeatureExtractor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Feature Extraction Agent',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_data():
    """Process raw data for feature extraction."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = feature_extractor.extract_features(data)
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'feature_extractor'
        })
        
    except Exception as e:
        logger.error(f"Error processing feature extraction: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'feature_extractor'
        }), 500

@app.route('/feature_categories', methods=['GET'])
def get_feature_categories():
    """Get available feature categories."""
    return jsonify({
        'feature_categories': feature_extractor.feature_categories
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Feature Extraction Agent on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
