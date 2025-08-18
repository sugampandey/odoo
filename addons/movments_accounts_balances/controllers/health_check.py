import json
import time
from datetime import datetime
from odoo import http, api, SUPERUSER_ID
from odoo.http import request
from ..logger.logger import logger


class HealthCheckController(http.Controller):
    
    @http.route('/api/health', type='http', auth='none', methods=['GET'], csrf=False, save_session=False)
    def comprehensive_health_check(self):
        """Health check for API, EC2, and RDS monitoring"""
        start_time = time.time()
        health_status = {
            'status': 'pass',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'checks': {}
        }
        
        try:
            # RDS (Database) health check
            health_status['checks']['rds'] = self._check_rds()
            
            # API health check
            health_status['checks']['api'] = self._check_api()
            
            # Overall status
            failed_checks = [check for check in health_status['checks'].values() if check['status'] == 'fail']
            if failed_checks:
                health_status['status'] = 'fail'
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            health_status['status'] = 'fail'
            health_status['error'] = str(e)
        
        health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        status_code = 200 if health_status['status'] == 'pass' else 503
        
        response = request.make_response(
            json.dumps(health_status, indent=2),
            headers=[
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-store, no-cache, must-revalidate')
            ]
        )
        response.status_code = status_code
        return response
    
    def _check_rds(self):
        """Check RDS (database) connectivity and performance"""
        try:
            start_time = time.time()
            
            with api.Environment.manage():
                env = api.Environment(request.cr, SUPERUSER_ID, {})
                
                # Test connection
                env.cr.execute("SELECT 1")
                env.cr.fetchone()
                
                # Test basic operations
                env.cr.execute("SELECT count(*) FROM res_company")
                company_count = env.cr.fetchone()[0]
                
                # Check database size
                env.cr.execute("SELECT pg_database_size(current_database())")
                db_size = env.cr.fetchone()[0]
                
                db_response_time = round((time.time() - start_time) * 1000, 2)
                
                # Status based on response time
                status = 'fail' if db_response_time > 5000 else 'pass'
                
                return {
                    'status': status,
                    'response_time_ms': db_response_time,
                    'details': {
                        'connection': 'ok',
                        'companies': company_count,
                        'database_size_mb': round(db_size / (1024*1024), 2)
                    }
                }
                
        except Exception as e:
            logger.error(f"RDS health check failed: {str(e)}")
            return {
                'status': 'fail',
                'error': str(e)
            }
    
    def _check_api(self):
        """Check API functionality"""
        try:
            with api.Environment.manage():
                env = api.Environment(request.cr, SUPERUSER_ID, {})
                
                # Test basic API operations
                env['res.users'].search_count([])
                
                return {
                    'status': 'pass',
                    'details': {
                        'api_functional': True
                    }
                }
                
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
            return {
                'status': 'fail',
                'error': str(e)
            }

    @http.route('/api/health/simple', type='http', auth='none', methods=['GET'], csrf=False, save_session=False)
    def simple_health_check(self):
        """Simple health check"""
        try:
            with api.Environment.manage():
                env = api.Environment(request.cr, SUPERUSER_ID, {})
                env.cr.execute("SELECT 1")
                
            return request.make_response(
                json.dumps({'status': 'ok', 'timestamp': datetime.utcnow().isoformat() + 'Z'}),
                headers=[('Content-Type', 'application/json')]
            )
            
        except Exception as e:
            response = request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
            response.status_code = 503
            return response
