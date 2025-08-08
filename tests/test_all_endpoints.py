#!/usr/bin/env python3
"""
Comprehensive endpoint testing for PixPort after fixes
"""

import requests
import time
import json

def test_all_endpoints():
    """Test all PixPort endpoints"""
    print('🔍 TESTING ALL PIXPORT ENDPOINTS AFTER FIXES')
    print('=' * 60)
    
    base_url = 'http://127.0.0.1:5000'
    
    # Test basic page endpoints
    page_endpoints = [
        ('/', 'Home Page', 'GET'),
        ('/features', 'Features Page', 'GET'),
        ('/about', 'About Page', 'GET'),
        ('/contact', 'Contact Page', 'GET'),
    ]
    
    # Test API endpoints
    api_endpoints = [
        ('/health', 'Health Check', 'GET'),
        ('/status', 'Status Check', 'GET'),
        ('/ping', 'Ping Test', 'GET'),
        ('/api/save-image', 'Save Image API', 'POST'),
    ]
    
    # Test processing endpoints (these need files, so we'll just check if they return proper errors)
    process_endpoints = [
        ('/process/upload', 'File Upload', 'POST'),
    ]
    
    results = {
        'pages': {'passed': 0, 'failed': 0, 'total': 0},
        'apis': {'passed': 0, 'failed': 0, 'total': 0},
        'process': {'passed': 0, 'failed': 0, 'total': 0}
    }
    
    print('\n📄 TESTING PAGE ENDPOINTS:')
    print('-' * 30)
    
    for endpoint, name, method in page_endpoints:
        results['pages']['total'] += 1
        try:
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}', timeout=10)
            else:
                response = requests.post(f'{base_url}{endpoint}', timeout=10)
            
            if response.status_code == 200:
                print(f'✅ {name:<20} → {response.status_code} ({len(response.content)} bytes)')
                results['pages']['passed'] += 1
            else:
                print(f'⚠️  {name:<20} → {response.status_code}')
                results['pages']['failed'] += 1
                
        except requests.exceptions.ConnectionError:
            print(f'❌ {name:<20} → Connection failed')
            results['pages']['failed'] += 1
        except Exception as e:
            print(f'❌ {name:<20} → Error: {str(e)}')
            results['pages']['failed'] += 1
    
    print('\n🔌 TESTING API ENDPOINTS:')
    print('-' * 30)
    
    for endpoint, name, method in api_endpoints:
        results['apis']['total'] += 1
        try:
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}', timeout=10)
            elif method == 'POST' and 'save-image' in endpoint:
                # Test save-image with minimal data
                data = {'action': 'save_image', 'image_data': 'test_data'}
                response = requests.post(f'{base_url}{endpoint}', data=data, timeout=10)
            else:
                response = requests.post(f'{base_url}{endpoint}', timeout=10)
            
            if response.status_code in [200, 400]:  # 400 is expected for save-image without proper data
                try:
                    json_response = response.json()
                    if endpoint == '/api/save-image' and response.status_code == 400:
                        print(f'✅ {name:<20} → {response.status_code} (Expected error response)')
                    else:
                        status = json_response.get('status', json_response.get('message', 'OK'))
                        print(f'✅ {name:<20} → {response.status_code} ({status})')
                    results['apis']['passed'] += 1
                except:
                    print(f'✅ {name:<20} → {response.status_code} (Non-JSON response)')
                    results['apis']['passed'] += 1
            else:
                print(f'⚠️  {name:<20} → {response.status_code}')
                results['apis']['failed'] += 1
                
        except requests.exceptions.ConnectionError:
            print(f'❌ {name:<20} → Connection failed')
            results['apis']['failed'] += 1
        except Exception as e:
            print(f'❌ {name:<20} → Error: {str(e)}')
            results['apis']['failed'] += 1
    
    print('\n⚙️  TESTING PROCESSING ENDPOINTS:')
    print('-' * 30)
    
    for endpoint, name, method in process_endpoints:
        results['process']['total'] += 1
        try:
            if method == 'POST':
                # Test upload without file (should return proper error)
                response = requests.post(f'{base_url}{endpoint}', timeout=10)
            
            if response.status_code == 400:  # Expected for upload without file
                try:
                    json_response = response.json()
                    error = json_response.get('error', 'Unknown error')
                    print(f'✅ {name:<20} → {response.status_code} (Expected: {error})')
                    results['process']['passed'] += 1
                except:
                    print(f'✅ {name:<20} → {response.status_code} (Expected error)')
                    results['process']['passed'] += 1
            else:
                print(f'⚠️  {name:<20} → {response.status_code}')
                results['process']['failed'] += 1
                
        except requests.exceptions.ConnectionError:
            print(f'❌ {name:<20} → Connection failed')
            results['process']['failed'] += 1
        except Exception as e:
            print(f'❌ {name:<20} → Error: {str(e)}')
            results['process']['failed'] += 1
    
    # Print summary
    print('\n📊 COMPREHENSIVE TEST SUMMARY:')
    print('=' * 60)
    
    total_passed = results['pages']['passed'] + results['apis']['passed'] + results['process']['passed']
    total_failed = results['pages']['failed'] + results['apis']['failed'] + results['process']['failed']
    total_tests = results['pages']['total'] + results['apis']['total'] + results['process']['total']
    
    print(f'📄 Page Endpoints:    {results["pages"]["passed"]}/{results["pages"]["total"]} passed')
    print(f'🔌 API Endpoints:     {results["apis"]["passed"]}/{results["apis"]["total"]} passed')
    print(f'⚙️  Process Endpoints: {results["process"]["passed"]}/{results["process"]["total"]} passed')
    print('-' * 60)
    print(f'🎯 OVERALL SCORE:     {total_passed}/{total_tests} ({(total_passed/total_tests*100):.1f}%)')
    
    if total_failed == 0:
        print('\n🎉 ALL TESTS PASSED - ALL FIXES SUCCESSFUL!')
        print('✅ Application is fully operational!')
    else:
        print(f'\n⚠️  {total_failed} issues remaining - need attention')
    
    return total_passed == total_tests

if __name__ == '__main__':
    success = test_all_endpoints()
    exit(0 if success else 1)
