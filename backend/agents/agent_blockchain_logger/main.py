"""
KredMitra Blockchain Logger Agent
Logs credit scoring activities and decisions to Hyperledger Fabric blockchain for audit trail.
"""

from flask import Flask, request, jsonify
import os
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlockchainLogger:
    """
    Blockchain logging service for KredMitra credit scoring activities.
    """
    
    def __init__(self):
        self.chaincode_name = "kredmitra-cc"
        self.channel_name = "kredmitra-channel"
        self.network_config = self._load_network_config()
        self.local_cache = []  # Fallback storage when blockchain is unavailable
        
    def _load_network_config(self) -> Dict[str, Any]:
        """Load Hyperledger Fabric network configuration."""
        return {
            'peer_endpoint': os.environ.get('FABRIC_PEER_ENDPOINT', 'localhost:7051'),
            'orderer_endpoint': os.environ.get('FABRIC_ORDERER_ENDPOINT', 'localhost:7050'),
            'ca_endpoint': os.environ.get('FABRIC_CA_ENDPOINT', 'localhost:7054'),
            'msp_id': os.environ.get('FABRIC_MSP_ID', 'KredMitraMSP'),
            'wallet_path': os.environ.get('FABRIC_WALLET_PATH', './wallet')
        }
    
    def log_credit_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log credit assessment to blockchain.
        
        Args:
            assessment_data: Credit assessment data to log
            
        Returns:
            Dictionary with logging result
        """
        try:
            # Create transaction record
            transaction_record = self._create_transaction_record(assessment_data, 'credit_assessment')
            
            # Attempt to submit to blockchain
            blockchain_result = self._submit_to_blockchain(transaction_record)
            
            if blockchain_result['success']:
                logger.info(f"Credit assessment logged to blockchain: {blockchain_result['transaction_id']}")
                return {
                    'success': True,
                    'transaction_id': blockchain_result['transaction_id'],
                    'block_number': blockchain_result.get('block_number'),
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'blockchain'
                }
            else:
                # Fallback to local cache
                cache_result = self._store_in_cache(transaction_record)
                logger.warning(f"Blockchain unavailable, stored in cache: {cache_result['cache_id']}")
                return {
                    'success': True,
                    'cache_id': cache_result['cache_id'],
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'cache',
                    'note': 'Will sync to blockchain when available'
                }
                
        except Exception as e:
            logger.error(f"Error logging credit assessment: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def log_fraud_detection(self, fraud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log fraud detection results to blockchain."""
        try:
            transaction_record = self._create_transaction_record(fraud_data, 'fraud_detection')
            blockchain_result = self._submit_to_blockchain(transaction_record)
            
            if blockchain_result['success']:
                return {
                    'success': True,
                    'transaction_id': blockchain_result['transaction_id'],
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'blockchain'
                }
            else:
                cache_result = self._store_in_cache(transaction_record)
                return {
                    'success': True,
                    'cache_id': cache_result['cache_id'],
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'cache'
                }
                
        except Exception as e:
            logger.error(f"Error logging fraud detection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_loan_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log loan decision to blockchain."""
        try:
            transaction_record = self._create_transaction_record(decision_data, 'loan_decision')
            blockchain_result = self._submit_to_blockchain(transaction_record)
            
            if blockchain_result['success']:
                return {
                    'success': True,
                    'transaction_id': blockchain_result['transaction_id'],
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'blockchain'
                }
            else:
                cache_result = self._store_in_cache(transaction_record)
                return {
                    'success': True,
                    'cache_id': cache_result['cache_id'],
                    'timestamp': transaction_record['timestamp'],
                    'storage': 'cache'
                }
                
        except Exception as e:
            logger.error(f"Error logging loan decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_audit_trail(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query audit trail from blockchain.
        
        Args:
            query_params: Query parameters (applicant_id, date_range, etc.)
            
        Returns:
            Dictionary with audit trail data
        """
        try:
            # Try blockchain first
            blockchain_results = self._query_blockchain(query_params)
            
            if blockchain_results['success']:
                # Also include cached data if any
                cache_results = self._query_cache(query_params)
                
                all_records = blockchain_results['records'] + cache_results['records']
                all_records.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return {
                    'success': True,
                    'total_records': len(all_records),
                    'blockchain_records': len(blockchain_results['records']),
                    'cache_records': len(cache_results['records']),
                    'records': all_records,
                    'query_timestamp': datetime.utcnow().isoformat()
                }
            else:
                # Fallback to cache only
                cache_results = self._query_cache(query_params)
                return {
                    'success': True,
                    'total_records': len(cache_results['records']),
                    'records': cache_results['records'],
                    'source': 'cache_only',
                    'note': 'Blockchain query failed, showing cached data only'
                }
                
        except Exception as e:
            logger.error(f"Error querying audit trail: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_cache_to_blockchain(self) -> Dict[str, Any]:
        """Sync cached records to blockchain when it becomes available."""
        try:
            if not self.local_cache:
                return {
                    'success': True,
                    'synced_count': 0,
                    'message': 'No cached records to sync'
                }
            
            synced_count = 0
            failed_sync = []
            
            for cached_record in self.local_cache[:]:  # Create copy for iteration
                result = self._submit_to_blockchain(cached_record)
                if result['success']:
                    self.local_cache.remove(cached_record)
                    synced_count += 1
                    logger.info(f"Synced cached record to blockchain: {result['transaction_id']}")
                else:
                    failed_sync.append(cached_record['record_id'])
            
            return {
                'success': True,
                'synced_count': synced_count,
                'remaining_cache': len(self.local_cache),
                'failed_sync': failed_sync,
                'sync_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing cache to blockchain: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_transaction_record(self, data: Dict[str, Any], record_type: str) -> Dict[str, Any]:
        """Create standardized transaction record."""
        timestamp = datetime.utcnow().isoformat()
        
        # Create hash of sensitive data for privacy
        data_hash = self._create_data_hash(data)
        
        record = {
            'record_id': self._generate_record_id(data, timestamp),
            'record_type': record_type,
            'timestamp': timestamp,
            'applicant_id': data.get('applicant_id', 'anonymous'),
            'session_id': data.get('session_id', 'unknown'),
            'data_hash': data_hash,
            'metadata': {
                'agent_version': '1.0.0',
                'network_id': 'kredmitra-network',
                'compliance_version': '2024.1'
            }
        }
        
        # Add type-specific fields
        if record_type == 'credit_assessment':
            record['assessment_details'] = {
                'credit_score': data.get('credit_score'),
                'risk_level': data.get('risk_level'),
                'decision': data.get('decision'),
                'factors_considered': len(data.get('factors', []))
            }
        elif record_type == 'fraud_detection':
            record['fraud_details'] = {
                'is_fraud': data.get('is_fraud'),
                'fraud_probability': data.get('fraud_probability'),
                'risk_factors': data.get('risk_factors', [])
            }
        elif record_type == 'loan_decision':
            record['loan_details'] = {
                'decision': data.get('decision'),
                'loan_amount': data.get('loan_amount'),
                'interest_rate': data.get('interest_rate'),
                'approval_conditions': data.get('conditions', [])
            }
        
        return record
    
    def _generate_record_id(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate unique record ID."""
        content = f"{data.get('applicant_id', 'anonymous')}_{timestamp}_{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _create_data_hash(self, data: Dict[str, Any]) -> str:
        """Create hash of data for integrity verification."""
        # Remove sensitive fields before hashing
        safe_data = {k: v for k, v in data.items() if not self._is_sensitive_field(k)}
        content = json.dumps(safe_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive information."""
        sensitive_fields = [
            'personal_details', 'phone_number', 'email', 'address',
            'bank_account', 'pan_number', 'aadhar_number'
        ]
        return field_name.lower() in sensitive_fields
    
    def _submit_to_blockchain(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit transaction to Hyperledger Fabric blockchain.
        This is a mock implementation - replace with actual Fabric SDK calls.
        """
        try:
            # Mock blockchain submission
            # In real implementation, this would use Fabric SDK
            
            # Simulate network availability check
            if not self._is_blockchain_available():
                return {
                    'success': False,
                    'error': 'Blockchain network not available'
                }
            
            # Mock successful submission
            transaction_id = f"tx_{record['record_id']}"
            block_number = len(self.local_cache) + 1000  # Mock block number
            
            logger.info(f"Mock blockchain submission successful: {transaction_id}")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'block_number': block_number,
                'confirmation_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Blockchain submission error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_blockchain_available(self) -> bool:
        """
        Check if blockchain network is available.
        Mock implementation - replace with actual network check.
        """
        # Mock availability based on environment variable
        return os.environ.get('BLOCKCHAIN_AVAILABLE', 'false').lower() == 'true'
    
    def _store_in_cache(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Store record in local cache as fallback."""
        cache_id = f"cache_{len(self.local_cache)}"
        cached_record = {
            **record,
            'cache_id': cache_id,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        self.local_cache.append(cached_record)
        
        # Limit cache size
        if len(self.local_cache) > 1000:
            self.local_cache = self.local_cache[-1000:]
        
        return {
            'cache_id': cache_id,
            'cache_size': len(self.local_cache)
        }
    
    def _query_blockchain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query blockchain for audit records.
        Mock implementation - replace with actual Fabric SDK calls.
        """
        try:
            if not self._is_blockchain_available():
                return {
                    'success': False,
                    'error': 'Blockchain not available for query'
                }
            
            # Mock query results
            mock_records = [
                {
                    'record_id': 'blockchain_record_1',
                    'record_type': 'credit_assessment',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'transaction_id': 'tx_blockchain_record_1',
                    'block_number': 1001
                }
            ]
            
            return {
                'success': True,
                'records': mock_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _query_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query local cache for records."""
        try:
            filtered_records = []
            
            for record in self.local_cache:
                # Apply filters
                if 'applicant_id' in params:
                    if record.get('applicant_id') != params['applicant_id']:
                        continue
                
                if 'record_type' in params:
                    if record.get('record_type') != params['record_type']:
                        continue
                
                if 'date_from' in params:
                    if record.get('timestamp') < params['date_from']:
                        continue
                
                if 'date_to' in params:
                    if record.get('timestamp') > params['date_to']:
                        continue
                
                filtered_records.append(record)
            
            return {
                'success': True,
                'records': filtered_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'records': []
            }

# Flask application
app = Flask(__name__)

# Initialize blockchain logger
blockchain_logger = BlockchainLogger()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Blockchain Logger Agent',
        'timestamp': datetime.utcnow().isoformat(),
        'blockchain_available': blockchain_logger._is_blockchain_available(),
        'cache_size': len(blockchain_logger.local_cache)
    })

@app.route('/process', methods=['POST'])
def process_logging():
    """Process logging request."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        log_type = data.get('log_type', 'credit_assessment')
        
        if log_type == 'credit_assessment':
            result = blockchain_logger.log_credit_assessment(data)
        elif log_type == 'fraud_detection':
            result = blockchain_logger.log_fraud_detection(data)
        elif log_type == 'loan_decision':
            result = blockchain_logger.log_loan_decision(data)
        else:
            return jsonify({'error': f'Unknown log type: {log_type}'}), 400
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'blockchain_logger'
        })
        
    except Exception as e:
        logger.error(f"Error processing logging request: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'blockchain_logger'
        }), 500

@app.route('/query', methods=['POST'])
def query_audit_trail():
    """Query audit trail."""
    try:
        params = request.get_json() or {}
        result = blockchain_logger.query_audit_trail(params)
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'blockchain_logger'
        })
        
    except Exception as e:
        logger.error(f"Error querying audit trail: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'blockchain_logger'
        }), 500

@app.route('/sync', methods=['POST'])
def sync_cache():
    """Sync cached records to blockchain."""
    try:
        result = blockchain_logger.sync_cache_to_blockchain()
        
        return jsonify({
            'success': True,
            'result': result,
            'service': 'blockchain_logger'
        })
        
    except Exception as e:
        logger.error(f"Error syncing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'blockchain_logger'
        }), 500

@app.route('/cache_status', methods=['GET'])
def get_cache_status():
    """Get cache status."""
    return jsonify({
        'cache_size': len(blockchain_logger.local_cache),
        'blockchain_available': blockchain_logger._is_blockchain_available(),
        'oldest_cached': blockchain_logger.local_cache[0]['timestamp'] if blockchain_logger.local_cache else None,
        'newest_cached': blockchain_logger.local_cache[-1]['timestamp'] if blockchain_logger.local_cache else None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Blockchain Logger Agent on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)