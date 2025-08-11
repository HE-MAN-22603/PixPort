# PyMatting/Numba Cache Fix for Google Cloud Run

## Problem
The deployment was failing with this error:
```
Error: cannot cache function '_make_tree': no locator available for file '/opt/venv/lib/python3.11/site-packages/pymatting/util/kdtree.py'
```

This is a known issue with `pymatting` (a dependency of `rembg`) in containerized environments where Numba cannot properly cache compiled functions.

## Solution Applied

### 1. Environment Variables
Added these environment variables to disable Numba JIT compilation and caching:
- `NUMBA_DISABLE_JIT=1` - Disables JIT compilation completely
- `NUMBA_CACHE_DIR=/tmp/.numba_cache` - Sets cache directory to writable location
- `NUMBA_DISABLE_PERFORMANCE_WARNINGS=1` - Suppresses performance warnings

### 2. Dockerfile Changes
- Added environment variables in the production stage
- Created `/tmp/.numba_cache` directory with proper permissions
- Ensured the `appuser` has write access to the cache directory

### 3. Cloud Build Configuration  
- Added the environment variables to the Cloud Run deployment configuration
- These will be set at runtime in addition to build time

### 4. Application Changes
- Modified `app.py` to set environment variables early in the startup process
- Updated `preload_models.py` to set the variables before importing any modules
- Added better error handling for pymatting-related issues

### 5. Test Script
Created `test_pymatting_fix.py` to verify the fix works before deployment.

## Files Modified
1. `Dockerfile` - Added environment variables and cache directory
2. `cloudbuild.yaml` - Added env vars to Cloud Run deployment 
3. `app.py` - Early environment variable setup
4. `preload_models.py` - Better error handling and env var setup
5. `test_pymatting_fix.py` - Test script to verify fix

## Deployment Impact
- **Performance**: Disabling JIT may slightly reduce performance but eliminates the crash
- **Stability**: Much more stable in containerized environments
- **Memory**: Reduced memory usage from disabled JIT compilation
- **Startup**: Should resolve the container startup failures

## Next Steps
1. Deploy with `gcloud builds submit --config cloudbuild.yaml`
2. Monitor logs to confirm the fix works
3. If successful, the service should start without the pymatting error

## Testing Locally
Run `python test_pymatting_fix.py` to verify the fix works in your environment.
