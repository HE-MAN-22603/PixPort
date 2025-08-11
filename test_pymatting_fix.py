#!/usr/bin/env python3
"""
Test script to verify pymatting/numba fix
This should run without the cache error after applying the fixes
"""

import os
import sys

# Set the fix environment variables
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['NUMBA_CACHE_DIR'] = '/tmp/.numba_cache'
os.environ['NUMBA_DISABLE_PERFORMANCE_WARNINGS'] = '1'

print("🧪 Testing pymatting fix...")
print(f"✅ NUMBA_DISABLE_JIT = {os.environ.get('NUMBA_DISABLE_JIT')}")
print(f"✅ NUMBA_CACHE_DIR = {os.environ.get('NUMBA_CACHE_DIR')}")
print(f"✅ NUMBA_DISABLE_PERFORMANCE_WARNINGS = {os.environ.get('NUMBA_DISABLE_PERFORMANCE_WARNINGS')}")

try:
    print("📦 Testing rembg import...")
    from rembg import new_session
    print("✅ rembg imported successfully")
    
    print("🤖 Creating model session...")
    session = new_session('isnet-general-use')
    print("✅ Model session created successfully")
    
    print("🧹 Cleaning up...")
    del session
    print("✅ Test completed successfully - the fix works!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    print(f"🔍 Error type: {type(e).__name__}")
    if "pymatting" in str(e).lower() or "numba" in str(e).lower():
        print("💡 This is still a pymatting/numba issue")
        print("💡 Try running with: export NUMBA_DISABLE_JIT=1")
    sys.exit(1)

print("🎉 All tests passed!")
