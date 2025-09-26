"""
KredMitra RAG Coach Agent
Retrieval-Augmented Generation coach for financial literacy and credit guidance.
"""

from flask import Flask, request, jsonify
import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGCoach:
    """
    RAG-based financial coach that provides personalized guidance and education.
    """
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        self.conversation_history = {}
        
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize the financial knowledge base."""
        return {
            'credit_score_improvement': {
                'title': 'How to Improve Your Credit Score',
                'content': [
                    'Pay all bills on time - Payment history accounts for 35% of your credit score',
                    'Keep credit utilization below 30% - Lower is better, ideally under 10%',
                    'Maintain old credit accounts - Length of credit history matters',
                    'Limit new credit inquiries - Too many can hurt your score',
                    'Monitor your credit report regularly for errors',
                    'Consider becoming an authorized user on someone else\'s account',
                    'Pay down existing debt systematically'
                ],
                'tips': [
                    'Set up automatic payments to never miss due dates',
                    'Request credit limit increases to improve utilization ratio',
                    'Use credit monitoring services for alerts'
                ]
            },
            'budgeting_basics': {
                'title': 'Basic Budgeting Principles',
                'content': [
                    'Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings',
                    'Track all income and expenses for at least one month',
                    'Prioritize essential expenses first',
                    'Build an emergency fund of 3-6 months expenses',
                    'Review and adjust your budget monthly',
                    'Use budgeting apps or spreadsheets for tracking'
                ],
                'tips': [
                    'Start small - even saving ₹500 per month makes a difference',
                    'Automate savings to make it effortless',
                    'Review bank statements weekly'
                ]
            },
            'loan_application_tips': {
                'title': 'Loan Application Best Practices',
                'content': [
                    'Check your credit score before applying',
                    'Gather all required documents in advance',
                    'Compare offers from multiple lenders',
                    'Understand all fees and charges involved',
                    'Don\'t apply for multiple loans simultaneously',
                    'Be honest and accurate in your application',
                    'Consider having a co-signer if needed'
                ],
                'tips': [
                    'Pre-qualification doesn\'t hurt your credit score',
                    'Read all terms and conditions carefully',
                    'Ask about rate reduction options'
                ]
            },
            'financial_planning': {
                'title': 'Personal Financial Planning',
                'content': [
                    'Set clear short-term and long-term financial goals',
                    'Build an investment portfolio suited to your risk tolerance',
                    'Plan for retirement early - compound interest is powerful',
                    'Get adequate insurance coverage',
                    'Maintain liquid savings for emergencies',
                    'Diversify your income sources if possible',
                    'Review and update your financial plan annually'
                ],
                'tips': [
                    'Start investing even with small amounts',
                    'Take advantage of employer-sponsored retirement plans',
                    'Consider tax-saving investments'
                ]
            },
            'debt_management': {
                'title': 'Effective Debt Management',
                'content': [
                    'List all debts with balances, interest rates, and minimum payments',
                    'Use debt avalanche method: pay high-interest debt first',
                    'Consider debt snowball method for motivation',
                    'Negotiate with creditors for better terms',
                    'Avoid taking new debt while paying off existing debt',
                    'Consider debt consolidation if it lowers overall interest',
                    'Seek professional help if debt becomes unmanageable'
                ],
                'tips': [
                    'Pay more than minimum payments when possible',
                    'Use windfalls (bonuses, tax refunds) for debt payments',
                    'Avoid closing paid-off credit cards immediately'
                ]
            }
        }
    
    def provide_guidance(self, user_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide personalized financial guidance based on user query and profile.
        """
        try:
            user_id = user_query.get('user_id', 'anonymous')
            question = user_query.get('question', '').lower()
            user_profile = user_query.get('profile', {})
            context = user_query.get('context', {})
            
            # Analyze the query to determine relevant topics
            relevant_topics = self._identify_relevant_topics(question)
            
            # Generate personalized guidance
            guidance = self._generate_guidance(relevant_topics, user_profile, context)
            
            # Store conversation history
            self._update_conversation_history(user_id, question, guidance)
            
            result = {
                'guidance': guidance,
                'relevant_topics': relevant_topics,
                'personalization_factors': self._get_personalization_factors(user_profile),
                'follow_up_questions': self._suggest_follow_up_questions(relevant_topics),
                'recommended_actions': self._recommend_actions(user_profile, context),
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': user_id
            }
            
            logger.info(f"Guidance provided for user {user_id}: {len(relevant_topics)} topics covered")
            return result
            
        except Exception as e:
            logger.error(f"Error providing guidance: {e}")
            return {
                'guidance': 'I apologize, but I encountered an error processing your request. Please try again.',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _identify_relevant_topics(self, question: str) -> List[str]:
        """Identify relevant topics based on the user's question."""
        relevant_topics = []
        
        # Credit score related
        if any(word in question for word in ['credit', 'score', 'rating', 'cibil']):
            relevant_topics.append('credit_score_improvement')
        
        # Budgeting related
        if any(word in question for word in ['budget', 'expense', 'spending', 'money management']):
            relevant_topics.append('budgeting_basics')
        
        # Loan related
        if any(word in question for word in ['loan', 'borrow', 'lending', 'application']):
            relevant_topics.append('loan_application_tips')
        
        # Investment/planning related
        if any(word in question for word in ['invest', 'planning', 'future', 'retirement', 'saving']):
            relevant_topics.append('financial_planning')
        
        # Debt related
        if any(word in question for word in ['debt', 'emi', 'repay', 'default', 'overdue']):
            relevant_topics.append('debt_management')
        
        # If no specific topics identified, provide general guidance
        if not relevant_topics:
            relevant_topics = ['budgeting_basics', 'financial_planning']
        
        return relevant_topics
    
    def _generate_guidance(self, topics: List[str], profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate personalized guidance based on topics and user profile."""
        guidance_parts = []
        
        for topic in topics:
            if topic in self.knowledge_base:
                topic_info = self.knowledge_base[topic]
                
                # Add topic title
                guidance_parts.append(f"\n🎯 **{topic_info['title']}**\n")
                
                # Add personalized content
                personalized_content = self._personalize_content(topic_info['content'], profile, context)
                guidance_parts.extend([f"• {item}" for item in personalized_content[:5]])  # Limit to top 5
                
                # Add personalized tips
                if 'tips' in topic_info:
                    guidance_parts.append(f"\n💡 **Quick Tips:**")
                    personalized_tips = self._personalize_content(topic_info['tips'], profile, context)
                    guidance_parts.extend([f"  - {tip}" for tip in personalized_tips[:3]])  # Limit to top 3
        
        # Add profile-specific recommendations
        profile_recommendations = self._get_profile_specific_recommendations(profile, context)
        if profile_recommendations:
            guidance_parts.append(f"\n🎯 **Personalized for You:**")
            guidance_parts.extend([f"• {rec}" for rec in profile_recommendations])
        
        return "\n".join(guidance_parts)
    
    def _personalize_content(self, content: List[str], profile: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Personalize content based on user profile and context."""
        personalized = []
        
        # Get user characteristics
        age = profile.get('age', 30)
        income = profile.get('monthly_income', 0)
        employment_status = profile.get('employment_status', 'unknown')
        credit_score = context.get('credit_score', 0)
        
        for item in content:
            # Personalize based on age
            if age < 25 and 'retirement' in item.lower():
                item = item.replace('retirement', 'long-term savings and retirement')
            
            # Personalize based on income
            if income > 0:
                if '₹500' in item:
                    suggested_amount = max(500, int(income * 0.1))
                    item = item.replace('₹500', f'₹{suggested_amount}')
            
            # Personalize based on credit score
            if credit_score > 0:
                if 'credit score' in item.lower() and credit_score < 650:
                    item += ' (This is especially important given your current credit score)'
            
            personalized.append(item)
        
        return personalized
    
    def _get_profile_specific_recommendations(self, profile: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Generate profile-specific recommendations."""
        recommendations = []
        
        age = profile.get('age', 30)
        income = profile.get('monthly_income', 0)
        credit_score = context.get('credit_score', 0)
        debt_ratio = profile.get('debt_to_income_ratio', 0)
        
        # Age-based recommendations
        if age < 25:
            recommendations.append("Start building credit history early - consider a student credit card")
            recommendations.append("Focus on building skills to increase earning potential")
        elif age > 50:
            recommendations.append("Review retirement planning and ensure adequate savings")
            recommendations.append("Consider lower-risk investment options")
        
        # Income-based recommendations
        if income > 0:
            if income < 25000:
                recommendations.append("Focus on building emergency fund first, even if small amounts")
                recommendations.append("Look for opportunities to increase income through skills development")
            elif income > 100000:
                recommendations.append("Consider tax-saving investments and higher savings rates")
                recommendations.append("Explore diverse investment options for wealth building")
        
        # Credit score based recommendations
        if credit_score > 0:
            if credit_score < 600:
                recommendations.append("Priority: Focus on improving credit score before major loan applications")
                recommendations.append("Consider secured credit cards to rebuild credit")
            elif credit_score > 750:
                recommendations.append("Excellent credit! You qualify for the best loan rates")
                recommendations.append("Consider leveraging good credit for investment opportunities")
        
        # Debt ratio based recommendations
        if debt_ratio > 0.5:
            recommendations.append("High debt levels detected - prioritize debt reduction")
            recommendations.append("Avoid taking on new debt until current debt is under control")
        elif debt_ratio < 0.2:
            recommendations.append("Good debt management! You have room for strategic borrowing")
        
        return recommendations
    
    def _get_personalization_factors(self, profile: Dict[str, Any]) -> Dict[str, str]:
        """Get factors used for personalization."""
        factors = {}
        
        if profile.get('age'):
            factors['age_group'] = self._get_age_group(profile['age'])
        
        if profile.get('monthly_income'):
            factors['income_level'] = self._get_income_level(profile['monthly_income'])
        
        if profile.get('employment_status'):
            factors['employment'] = profile['employment_status']
        
        return factors
    
    def _suggest_follow_up_questions(self, topics: List[str]) -> List[str]:
        """Suggest relevant follow-up questions."""
        follow_ups = []
        
        if 'credit_score_improvement' in topics:
            follow_ups.extend([
                "How often should I check my credit report?",
                "What's the fastest way to improve my credit score?",
                "How long does it take to see credit score improvements?"
            ])
        
        if 'budgeting_basics' in topics:
            follow_ups.extend([
                "What budgeting app do you recommend?",
                "How do I handle irregular income in budgeting?",
                "What percentage should I save each month?"
            ])
        
        if 'loan_application_tips' in topics:
            follow_ups.extend([
                "What documents do I need for a loan application?",
                "How can I get pre-approved for a loan?",
                "What's the difference between fixed and variable interest rates?"
            ])
        
        # Remove duplicates and limit
        return list(set(follow_ups))[:5]
    
    def _recommend_actions(self, profile: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Recommend specific actionable steps."""
        actions = []
        
        credit_score = context.get('credit_score', 0)
        
        if credit_score > 0 and credit_score < 650:
            actions.append({
                'action': 'Check Credit Report',
                'description': 'Get your free credit report and look for errors',
                'timeline': 'This week',
                'priority': 'high'
            })
        
        if not profile.get('has_emergency_fund', False):
            actions.append({
                'action': 'Start Emergency Fund',
                'description': 'Save ₹1000 as initial emergency fund',
                'timeline': 'Next 3 months',
                'priority': 'high'
            })
        
        if profile.get('debt_to_income_ratio', 0) > 0.4:
            actions.append({
                'action': 'Create Debt Payoff Plan',
                'description': 'List all debts and create systematic payoff strategy',
                'timeline': 'This month',
                'priority': 'high'
            })
        
        actions.append({
            'action': 'Track Expenses',
            'description': 'Monitor spending for one month to understand patterns',
            'timeline': 'Starting now',
            'priority': 'medium'
        })
        
        return actions
    
    def _update_conversation_history(self, user_id: str, question: str, guidance: str):
        """Update conversation history for the user."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'question': question,
            'guidance_length': len(guidance),
            'topics_covered': len(guidance.split('🎯'))
        })
        
        # Keep only last 10 conversations per user
        self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def _get_age_group(self, age: int) -> str:
        """Get age group classification."""
        if age < 25:
            return 'young_adult'
        elif age < 35:
            return 'early_career'
        elif age < 50:
            return 'mid_career'
        else:
            return 'experienced'
    
    def _get_income_level(self, income: float) -> str:
        """Get income level classification."""
        if income < 25000:
            return 'entry_level'
        elif income < 50000:
            return 'moderate'
        elif income < 100000:
            return 'good'
        else:
            return 'high'

# Flask application
app = Flask(__name__)

# Initialize RAG coach
rag_coach = RAGCoach()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Coach Agent',
        'timestamp': datetime.utcnow().isoformat(),
        'knowledge_topics': len(rag_coach.knowledge_base)
    })

@app.route('/process', methods=['POST'])
def process_query():
    """Process user query for financial guidance."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = rag_coach.provide_guidance(data)
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'rag_coach'
        })
        
    except Exception as e:
        logger.error(f"Error processing guidance query: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'rag_coach'
        }), 500

@app.route('/topics', methods=['GET'])
def get_available_topics():
    """Get available knowledge base topics."""
    topics = {}
    for key, value in rag_coach.knowledge_base.items():
        topics[key] = {
            'title': value['title'],
            'content_items': len(value['content']),
            'has_tips': 'tips' in value
        }
    
    return jsonify({
        'available_topics': topics,
        'total_topics': len(topics)
    })

@app.route('/conversation_history/<user_id>', methods=['GET'])
def get_conversation_history(user_id: str):
    """Get conversation history for a user."""
    history = rag_coach.conversation_history.get(user_id, [])
    return jsonify({
        'user_id': user_id,
        'conversation_count': len(history),
        'history': history
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting RAG Coach Agent on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)