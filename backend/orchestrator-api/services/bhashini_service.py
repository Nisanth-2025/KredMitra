"""
KredMitra Bhashini Translation Service
Integration with Bhashini API for multi-language support in the credit scoring system.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class BhashiniService:
    """
    Service class for integrating with Bhashini API for translation services.
    Supports translation between Indian languages for inclusive credit scoring.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://meity-auth.ulcacontrib.org"
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'te': 'Telugu',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'as': 'Assamese',
            'ur': 'Urdu'
        }
        
        # Fallback translations for common credit terms
        self.fallback_translations = {
            'hi': {
                'credit_score': 'क्रेडिट स्कोर',
                'loan_application': 'ऋण आवेदन',
                'interest_rate': 'ब्याज दर',
                'monthly_income': 'मासिक आय',
                'approved': 'स्वीकृत',
                'rejected': 'अस्वीकृत',
                'pending': 'लंबित',
                'documents_required': 'आवश्यक दस्तावेज',
                'repayment': 'पुनर्भुगतान',
                'financial_guidance': 'वित्तीय मार्गदर्शन'
            },
            'te': {
                'credit_score': 'క్రెడిట్ స్కోర్',
                'loan_application': 'రుణ దరఖాస్తు',
                'interest_rate': 'వడ్రాట',
                'monthly_income': 'నెలవారీ ఆదాయం',
                'approved': 'ఆమోదించబడింది',
                'rejected': 'తిరస్కరించబడింది',
                'pending': 'పెండింగ్',
                'documents_required': 'అవసరమైన పత్రాలు',
                'repayment': 'తిరిగి చెల్లింపు',
                'financial_guidance': 'ఆర్థిక మార్గదర్శకత్వం'
            },
            'ta': {
                'credit_score': 'கடன் மதிப்பெண்',
                'loan_application': 'கடன் விண்ணப்பம்',
                'interest_rate': 'வட்டி விகிதம்',
                'monthly_income': 'மாதாந்திர வருமானம்',
                'approved': 'அங்கீகரிக்கப்பட்டது',
                'rejected': 'நிராகரிக்கப்பட்டது',
                'pending': 'நிலுவையில்',
                'documents_required': 'தேவையான ஆவணங்கள்',
                'repayment': 'திருப்பிச் செலுத்துதல்',
                'financial_guidance': 'நிதி வழிகாட்டுதல்'
            }
        }
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'hi') -> Dict[str, Any]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'hi')
            
        Returns:
            Dictionary with translation result
        """
        try:
            # Validate language codes
            if source_lang not in self.supported_languages:
                return {
                    'success': False,
                    'error': f'Unsupported source language: {source_lang}',
                    'translated_text': text  # Return original text
                }
            
            if target_lang not in self.supported_languages:
                return {
                    'success': False,
                    'error': f'Unsupported target language: {target_lang}',
                    'translated_text': text  # Return original text
                }
            
            # If source and target are the same, return original text
            if source_lang == target_lang:
                return {
                    'success': True,
                    'translated_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'translation_method': 'no_translation_needed'
                }
            
            # Try Bhashini API first
            if self.api_key:
                api_result = self._call_bhashini_api(text, source_lang, target_lang)
                if api_result['success']:
                    return api_result
                else:
                    logger.warning(f"Bhashini API failed: {api_result.get('error')}")
            
            # Fallback to local translations
            fallback_result = self._get_fallback_translation(text, source_lang, target_lang)
            return fallback_result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translated_text': text,  # Return original text as fallback
                'translation_method': 'error_fallback'
            }
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'hi') -> Dict[str, Any]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with batch translation results
        """
        try:
            results = []
            successful_translations = 0
            
            for text in texts:
                result = self.translate(text, source_lang, target_lang)
                results.append(result)
                if result.get('success', False):
                    successful_translations += 1
            
            return {
                'success': True,
                'total_texts': len(texts),
                'successful_translations': successful_translations,
                'results': results,
                'batch_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of given text.
        Note: This is a simplified implementation.
        """
        try:
            # Simple language detection based on script
            if self._contains_devanagari(text):
                return {
                    'success': True,
                    'detected_language': 'hi',
                    'language_name': 'Hindi',
                    'confidence': 0.8,
                    'method': 'script_detection'
                }
            elif self._contains_bengali(text):
                return {
                    'success': True,
                    'detected_language': 'bn',
                    'language_name': 'Bengali',
                    'confidence': 0.8,
                    'method': 'script_detection'
                }
            elif self._contains_tamil(text):
                return {
                    'success': True,
                    'detected_language': 'ta',
                    'language_name': 'Tamil',
                    'confidence': 0.8,
                    'method': 'script_detection'
                }
            elif self._contains_telugu(text):
                return {
                    'success': True,
                    'detected_language': 'te',
                    'language_name': 'Telugu',
                    'confidence': 0.8,
                    'method': 'script_detection'
                }
            else:
                # Default to English for Latin script
                return {
                    'success': True,
                    'detected_language': 'en',
                    'language_name': 'English',
                    'confidence': 0.6,
                    'method': 'default_detection'
                }
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return {
                'success': False,
                'error': str(e),
                'detected_language': 'en'  # Default fallback
            }
    
    def _call_bhashini_api(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Call Bhashini API for translation.
        This is a mock implementation - replace with actual Bhashini API calls.
        """
        try:
            # Mock API call - replace with actual Bhashini implementation
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'provider': 'bhashini'
            }
            
            # Mock response - in real implementation, make actual API call
            mock_translations = {
                ('en', 'hi'): {
                    'Hello': 'नमस्ते',
                    'Thank you': 'धन्यवाद',
                    'Your loan application has been approved': 'आपका ऋण आवेदन स्वीकृत हो गया है',
                    'Credit score': 'क्रेडिट स्कोर'
                },
                ('en', 'te'): {
                    'Hello': 'నమస్కారం',
                    'Thank you': 'ధన్యవాదాలు',
                    'Your loan application has been approved': 'మీ రుణ దరఖాస్తు ఆమోదించబడింది',
                    'Credit score': 'క్రెడిట్ స్కోర్'
                }
            }
            
            translation_key = (source_lang, target_lang)
            if translation_key in mock_translations and text in mock_translations[translation_key]:
                translated_text = mock_translations[translation_key][text]
                
                return {
                    'success': True,
                    'translated_text': translated_text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'translation_method': 'bhashini_api',
                    'confidence': 0.95
                }
            else:
                return {
                    'success': False,
                    'error': 'Translation not found in mock data',
                    'translated_text': text
                }
                
        except Exception as e:
            logger.error(f"Bhashini API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translated_text': text
            }
    
    def _get_fallback_translation(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Get fallback translation using local dictionary."""
        try:
            # Convert to lowercase for matching
            text_lower = text.lower().strip()
            
            # Check if we have fallback translations for the target language
            if target_lang in self.fallback_translations:
                translations = self.fallback_translations[target_lang]
                
                # Look for exact matches or partial matches
                for english_term, translation in translations.items():
                    if english_term in text_lower:
                        # Simple replacement
                        translated_text = text.replace(english_term.replace('_', ' '), translation)
                        return {
                            'success': True,
                            'translated_text': translated_text,
                            'source_language': source_lang,
                            'target_language': target_lang,
                            'translation_method': 'fallback_dictionary',
                            'confidence': 0.7
                        }
            
            # If no translation found, return original text
            return {
                'success': False,
                'error': 'No fallback translation available',
                'translated_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'translation_method': 'no_translation',
                'confidence': 0.0
            }
            
        except Exception as e:
            logger.error(f"Fallback translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translated_text': text,
                'translation_method': 'error_fallback'
            }
    
    def _contains_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari script (Hindi)."""
        devanagari_range = range(0x0900, 0x097F)
        return any(ord(char) in devanagari_range for char in text)
    
    def _contains_bengali(self, text: str) -> bool:
        """Check if text contains Bengali script."""
        bengali_range = range(0x0980, 0x09FF)
        return any(ord(char) in bengali_range for char in text)
    
    def _contains_tamil(self, text: str) -> bool:
        """Check if text contains Tamil script."""
        tamil_range = range(0x0B80, 0x0BFF)
        return any(ord(char) in tamil_range for char in text)
    
    def _contains_telugu(self, text: str) -> bool:
        """Check if text contains Telugu script."""
        telugu_range = range(0x0C00, 0x0C7F)
        return any(ord(char) in telugu_range for char in text)
    
    def translate_credit_terms(self, terms: List[str], target_lang: str = 'hi') -> Dict[str, str]:
        """
        Translate common credit-related terms.
        
        Args:
            terms: List of credit terms to translate
            target_lang: Target language code
            
        Returns:
            Dictionary mapping original terms to translations
        """
        translations = {}
        
        for term in terms:
            result = self.translate(term, 'en', target_lang)
            translations[term] = result.get('translated_text', term)
        
        return translations
    
    def get_localized_messages(self, target_lang: str = 'hi') -> Dict[str, str]:
        """Get localized system messages for the target language."""
        
        english_messages = {
            'welcome': 'Welcome to KredMitra Credit Scoring System',
            'application_submitted': 'Your loan application has been submitted successfully',
            'score_calculated': 'Your credit score has been calculated',
            'documents_required': 'Please submit the required documents',
            'application_approved': 'Congratulations! Your loan application has been approved',
            'application_rejected': 'We regret to inform you that your loan application has been rejected',
            'under_review': 'Your application is currently under review',
            'contact_support': 'Please contact customer support for assistance'
        }
        
        localized_messages = {}
        
        for key, message in english_messages.items():
            translation_result = self.translate(message, 'en', target_lang)
            localized_messages[key] = translation_result.get('translated_text', message)
        
        return localized_messages