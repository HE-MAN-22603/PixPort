#!/usr/bin/env python3
"""
Test script for model monitoring endpoints
"""

import os
import sys

def test_model_monitoring():
    """Test the model monitoring endpoints"""
    
    # Set up test environment
    os.environ['SECRET_KEY'] = '88b1a20dd30fe2520c874c73ad64b0648b62d0dcb01ffc372a86a4c8700f3770'
    os.environ['RAILWAY_ENVIRONMENT_NAME'] = 'production'
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            print('🔍 TESTING MODEL MONITORING ENDPOINTS')
            print('=' * 50)
            
            # Test model status endpoint
            response = client.get('/api/model/status')
            print(f'Model Status Response: {response.status_code}')
            
            if response.status_code == 200:
                data = response.get_json()
                env = data.get('environment', 'Unknown')
                print(f'✅ Environment: {env}')
                
                models = data.get('models', {})
                print(f'📊 Found {len(models)} model services:')
                
                for name, info in models.items():
                    status = '✅' if info.get('loaded') else '❌'
                    model_name = info.get('model_name', 'N/A')
                    memory = info.get('memory_mb', 0)
                    priority = info.get('priority', 'N/A')
                    
                    print(f'   {status} {name}')
                    if info.get('loaded'):
                        print(f'      Model: {model_name}')
                        print(f'      Memory: {memory}MB')
                        print(f'      Priority: {priority}')
                
                # Railway compatibility check
                compat = data.get('railway_compatibility', {})
                if compat:
                    status = compat.get('status', 'Unknown')
                    current = compat.get('current_usage_mb', 0)
                    percent = compat.get('usage_percent', 0)
                    
                    print(f'\n🚂 Railway Status: {status}')
                    print(f'   Memory Usage: {current}MB / 512MB')
                    print(f'   Usage Percent: {percent}%')
                
                # Processing strategy
                strategy = data.get('processing_strategy', [])
                if strategy:
                    print(f'\n🔄 Processing Strategy:')
                    for step in strategy:
                        print(f'   {step}')
                
                print(f'\n✅ Model monitoring endpoints working!')
                return True
            else:
                print(f'❌ Failed with status {response.status_code}')
                return False
                
    except Exception as e:
        print(f'❌ Error testing model monitoring: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up environment
        if 'RAILWAY_ENVIRONMENT_NAME' in os.environ:
            del os.environ['RAILWAY_ENVIRONMENT_NAME']
        if 'SECRET_KEY' in os.environ:
            del os.environ['SECRET_KEY']

if __name__ == '__main__':
    print('🧪 MODEL MONITORING TEST')
    print('=' * 30)
    
    success = test_model_monitoring()
    
    if success:
        print('\n🎉 Model monitoring test PASSED!')
        print('\n📋 How to use in production:')
        print('   GET /api/model/status - Check current models and memory')
        print('   POST /api/model/clear-memory - Free up memory if needed') 
        print('   POST /api/model/test-processing - Simulate model selection')
        sys.exit(0)
    else:
        print('\n❌ Model monitoring test FAILED!')
        sys.exit(1)
