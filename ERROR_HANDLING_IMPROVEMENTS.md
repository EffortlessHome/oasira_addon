# Error Handling Improvements for Matter Service

## Problem
The oasira_addon matter service was failing with unhandled promise rejections and async errors, causing the entire service to crash.

## Solutions Implemented

### 1. **Comprehensive Error Handling**
- Added try-catch blocks to all async functions
- Wrapped all background tasks with `task_wrapper()` function
- Proper exception handling for `asyncio.CancelledError`
- Stack trace logging for debugging

### 2. **Automatic Restart Logic**
- **Matter Backend**: Automatically restarts up to 5 times with 10-second delays
- **Cloudflared**: Automatically restarts up to 3 times with 5-second delays
- Process monitoring detects exits and triggers restarts
- Retry counters prevent infinite restart loops

### 3. **Health Check System**
- New `health_check_loop()` function runs every 60 seconds
- Checks if Matter backend responds to API requests
- Automatically terminates and restarts unresponsive processes
- Marks backend as healthy/unhealthy for monitoring

### 4. **Graceful Error Recovery**
- Output stream reading wrapped in try-catch
- Cancelled task handling prevents error propagation
- Dashboard handlers return 500 errors instead of crashing
- Proxy errors return 503 with proper CORS headers

### 5. **Process Management**
- Global `matter_backend_process` variable for health checks
- Global `matter_backend_healthy` flag for status tracking
- Proper process termination (SIGTERM then SIGKILL)
- Async task cancellation support

## Key Functions Added

### `task_wrapper(coro, name)`
Wraps async tasks to catch and log all exceptions without crashing the main event loop.

### `check_matter_backend_health()`
Tests if Matter backend API is responding on port 8482.

### `health_check_loop()`
Periodically monitors Matter backend health and restarts if unresponsive.

### Enhanced `start_matter_backend()`
- Retry logic with exponential backoff
- Output stream monitoring with error handling
- Automatic restart on failure (up to 5 times)
- Health status updates

### Enhanced `start_cloudflared()`
- Retry logic for tunnel connection
- Output stream error handling
- Automatic restart on failure (up to 3 times)

### Enhanced `serve_dashboard()`
- Try-catch in all route handlers
- Error responses instead of crashes
- Graceful cancellation support

## Configuration

### Health Check Settings
- Check interval: 60 seconds
- Initial delay: 30 seconds (allows startup)
- Timeout: 5 seconds per check

### Restart Settings
- Matter Backend: 5 retries, 10-second delay
- Cloudflared: 3 retries, 5-second delay

## Benefits

1. **No More Crashes**: Service stays running even when components fail
2. **Self-Healing**: Automatic detection and restart of failed services
3. **Better Monitoring**: Clear logging of health status and errors
4. **Graceful Degradation**: Services continue running even if one component fails
5. **Easier Debugging**: Full stack traces for all errors

## Testing

To verify the improvements:

1. **Test automatic restart**: Kill Matter backend process manually
   ```bash
   docker exec <container> pkill -f "node.*cli.js"
   ```
   - Should see health check detect failure
   - Should see automatic restart attempt

2. **Test error handling**: Send invalid requests to Matter API
   ```bash
   curl http://localhost:8080/api/matter/bridges/invalid
   ```
   - Should return error without crashing

3. **Monitor logs**: Watch for health check messages
   ```bash
   docker logs -f <container> | grep "health check"
   ```

## Future Enhancements

- Add Prometheus metrics for monitoring
- Implement exponential backoff for retries
- Add configurable retry limits via environment variables
- Integrate with Home Assistant for alert notifications
