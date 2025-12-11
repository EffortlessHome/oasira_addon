import os
import asyncio
import json
import aiohttp
import websockets
import uuid
import subprocess
from pathlib import Path
from aiohttp import web
from oasira import OasiraAPIClient, OasiraAPIError

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
SUPERVISOR_URL = "http://supervisor/core/api"

# Configuration from environment variables (set via addon config or docker-compose)
email = os.environ.get("EMAIL") or os.environ.get("OASIRA_EMAIL")
password = os.environ.get("PASSWORD") or os.environ.get("OASIRA_PASSWORD")
system_id = os.environ.get("SYSTEM_ID")  # Optional - will auto-select if not provided
matter_label = os.environ.get("MATTER_LABEL", "favorite")  # Label for Matter device filter
dashboard_port = int(os.environ.get("DASHBOARD_PORT", 8080))

# These will be populated from API response
ha_url = None
ha_token = None
cloudflare_token = None
fullname = None
emailaddress = None
customer_id = None
systemid = None
testmode = None
plan = None
trial_expiration = None
id_token = None
refresh_token = None  # Store refresh token for token refresh

CLIENT_ID = str(uuid.uuid4())  # Unique ID for this HA instance

##TODO: need to select correct cloudflared binary based on host system os

async def start():
    """Authenticate with Firebase OAuth and fetch system configuration."""
    global cloudflare_token, ha_token, ha_url, fullname, emailaddress
    global customer_id, system_id, systemid, testmode, plan, trial_expiration, id_token, refresh_token

    print("Starting OAuth authentication...")

    if not email or not password:
        print("❌ Email or password not configured. Cannot start Oasira.")
        return False

    try:
        # Step 1: Authenticate with Firebase
        async with OasiraAPIClient() as client:
            print("🔐 Authenticating with Firebase...")
            auth_result = await client.firebase_sign_in(email, password)
            
            firebase_uid = auth_result.get("localId")
            id_token = auth_result.get("idToken")
            refresh_token = auth_result.get("refreshToken")  # Store refresh token
            
            if not firebase_uid or not id_token:
                print("❌ Firebase authentication failed - missing tokens")
                return False
            
            print(f"✅ Firebase authentication successful (UID: {firebase_uid})")

        # Step 2: Fetch available systems for this user
        async with OasiraAPIClient(id_token=id_token) as client:
            print(f"📋 Fetching systems for {email}...")
            systems = await client.get_system_list_by_email(email)
            
            if not systems:
                print("❌ No systems found for this account")
                return False
            
            print(f"✅ Found {len(systems)} system(s)")
            
            # Step 3: Select system
            selected_system = None
            
            if len(systems) == 1:
                # Only one system - use it automatically
                selected_system = systems[0]
                print(f"✅ Using system: {selected_system.get('SystemID')} (only system available)")
            elif system_id:
                # User specified a system_id in config
                selected_system = next(
                    (s for s in systems if str(s.get('SystemID')) == str(system_id)),
                    None
                )
                if not selected_system:
                    print(f"⚠️ Configured system_id '{system_id}' not found. Available systems:")
                    for sys in systems:
                        print(f"  - System ID: {sys.get('SystemID')} (Customer: {sys.get('customer_id')})")
                    # Use first system as fallback
                    selected_system = systems[0]
                    print(f"✅ Using first available system: {selected_system.get('SystemID')}")
                else:
                    print(f"✅ Using configured system: {system_id}")
            else:
                # No system_id specified - use first one
                selected_system = systems[0]
                print(f"⚠️ Multiple systems available but no system_id configured.")
                print(f"Available systems:")
                for sys in systems:
                    print(f"  - System ID: {sys.get('SystemID')} (Customer: {sys.get('customer_id')})")
                print(f"✅ Using first system: {selected_system.get('SystemID')}")
            
            # Extract system information
            customer_id = str(selected_system.get('customer_id'))
            system_id = str(selected_system.get('SystemID'))
            
            print(f"🔍 Debug - customer_id: {customer_id}")
            print(f"🔍 Debug - system_id: {system_id}")

        # Step 4: Fetch full system configuration using get_system_by_system_id
        async with OasiraAPIClient(system_id=system_id, id_token=id_token) as client:
            print(f"📦 Fetching system configuration...")
            system_data = await client.get_system_by_system_id(system_id)

            # Extract values from system configuration
            ha_token = system_data.get("ha_token")
            cloudflare_token = system_data.get("cloudflare_token")
            ha_url = system_data.get("ha_url")
            systemid = str(system_data.get("id"))
            testmode = system_data.get("testmode")
            
            # Get customer info for display
            customer_data = await client.get_customer_and_system()
            fullname = customer_data.get("fullname")
            emailaddress = customer_data.get("emailaddress")
            plan = customer_data.get("name")
            trial_expiration = customer_data.get("trial_expiration")

            print("="*50)
            print(f"✅ Login successful!")
            print(f"   User: {fullname} ({emailaddress})")
            print(f"   Customer ID: {customer_id}")
            print(f"   System ID: {system_id}")
            print(f"   Plan: {plan}")
            print(f"   Test Mode: {testmode}")
            if trial_expiration:
                print(f"   Trial Expiration: {trial_expiration}")
            print("="*50)
            
            return True

    except OasiraAPIError as e:
        print(f"❌ Failed to authenticate with Oasira API: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during login: {e}")
        import traceback
        traceback.print_exc()
        return False


async def start_cloudflared():
    """Download, install, and run cloudflared binary with error handling."""
    try:
        # Install part
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        path = "/usr/local/bin/cloudflared"

        try:
            if not os.path.exists(path):
                print("cloudflared not found, downloading...")
                proc = await asyncio.create_subprocess_exec(
                    "wget", "-O", path, url,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode != 0:
                    print(f"wget failed: {stderr.decode()}")
                    return

                # Make executable
                proc_chmod = await asyncio.create_subprocess_exec(
                    "chmod", "+x", path
                )
                await proc_chmod.communicate()
                print(f"cloudflared installed at {path}")
            else:
                print("cloudflared already installed.")

        except Exception as e:
            print(f"Error installing cloudflared: {e}")
            return

        # Run part
        if not cloudflare_token:
            print("CLOUDFLARE_TOKEN variable not set. Cannot start tunnel.")
            return

        print("Starting cloudflared tunnel...")
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # Run cloudflared as a background process
                proc = await asyncio.create_subprocess_exec(
                    path,
                    "tunnel",
                    "run",
                    "--token",
                    cloudflare_token,            
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                async def log_output(stream, prefix):
                    try:
                        while True:
                            line = await stream.readline()
                            if not line:
                                break
                            decoded = line.decode().strip()
                            if decoded:
                                print(f"{prefix}: {decoded}")
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        print(f"⚠️ Error reading {prefix}: {e}")

                asyncio.create_task(log_output(proc.stdout, "cloudflared-out"))
                asyncio.create_task(log_output(proc.stderr, "cloudflared-err"))

                print("✅ cloudflared tunnel process started.")
                
                # Wait for process and restart if it exits
                await proc.wait()
                print(f"⚠️ cloudflared exited with code {proc.returncode}")
                
                retry_count += 1
                if retry_count < max_retries:
                    print(f"🔄 Restarting cloudflared (attempt {retry_count + 1}/{max_retries})...")
                    await asyncio.sleep(5)
                else:
                    print("❌ cloudflared failed too many times, stopping restart attempts")
                    break

            except FileNotFoundError:
                print("❌ cloudflared binary not found. Installation might have failed.")
                break
            except Exception as exc:
                print(f"❌ cloudflared error: {exc}")
                import traceback
                traceback.print_exc()
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                else:
                    break
    
    except asyncio.CancelledError:
        print("⚠️ Cloudflared task cancelled")
        raise
    except Exception as e:
        print(f"❌ Fatal cloudflared error: {e}")
        import traceback
        traceback.print_exc()
        print(f"Error running cloudflared: {exc}")


# Matter Hub API implementation in Python
MATTER_STORAGE_PATH = "/data/matter"
matter_bridges = {}  # In-memory storage for bridge configurations

def load_matter_config():
    """Load Matter bridge configuration from disk."""
    global matter_bridges
    config_file = Path(MATTER_STORAGE_PATH) / "bridges.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                matter_bridges = json.load(f)
            print(f"✅ Loaded {len(matter_bridges)} Matter bridge(s)")
        except Exception as e:
            print(f"⚠️ Error loading Matter config: {e}")
            matter_bridges = {}
    else:
        matter_bridges = {}
        os.makedirs(MATTER_STORAGE_PATH, exist_ok=True)

# Matter Hub - proxy to Node.js backend
MATTER_BACKEND_URL = "http://localhost:8482"  # Matter backend port

async def proxy_to_matter_backend(request):
    """Proxy requests to the Matter.js backend."""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return web.Response(
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
            }
        )
    
    # Forward the request to Matter backend
    path = request.path.replace('/api/matter', '')
    url = f"{MATTER_BACKEND_URL}/api/matter{path}"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Forward method, headers, and body
            method = request.method
            headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
            
            data = None
            if method in ['POST', 'PUT', 'PATCH']:
                data = await request.read()
            
            async with session.request(method, url, headers=headers, data=data) as resp:
                body = await resp.read()
                # Add CORS headers to response
                response_headers = {
                    'Content-Type': resp.content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
                }
                return web.Response(
                    body=body,
                    status=resp.status,
                    headers=response_headers
                )
    except aiohttp.ClientError as e:
        print(f"❌ Matter backend proxy error: {e}")
        return web.json_response(
            {'error': 'Matter backend unavailable'},
            status=503,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
            }
        )



async def register_with_server():
    """Notify the Cloud Run / Cloudflare service about this HA instance"""
    data = {
        "client_id": CLIENT_ID,
        "socket_url": "WEBSOCKET_URL",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("REGISTER_URL", json=data) as resp:
                text = await resp.text()
                print(f"✅ Registered with Oasira Cloud: {resp.status} - {text}")
        except Exception as e:
            print(f"⚠️ Failed to register with server: {e}")

async def call_home_assistant(method, path, body=None):
    url = f"{SUPERVISOR_URL}{path}"
    headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, json=body) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
            return {"status": resp.status, "data": data}

async def connect_to_cloud():
    print(f"🌐 Connecting to {"WEBSOCKET_URL"} as client {CLIENT_ID}")
    while True: # Keep trying to connect forever
        try:
            async with websockets.connect("WEBSOCKET_URL") as ws:            
           # async with websockets.connect(WEBSOCKET_URL, extra_headers={"X-Client-ID": CLIENT_ID}) as ws:
                print("✅ Connected to Oasira WebSocket bridge")
                async for msg in ws:
                    try:
                        payload = json.loads(msg)
                        print(f"📩 Received: {payload}")

                        method = payload.get("method", "GET").upper()
                        path = payload.get("path", "/")
                        body = payload.get("body")
                        req_id = payload.get("id")

                        result = await call_home_assistant(method, path, body)
                        response = json.dumps({"id": req_id, "result": result})
                        await ws.send(response)
                        print(f"📤 Sent response for {req_id}")

                    except Exception as e:
                        err = str(e)
                        print(f"❌ Error handling message: {err}")
                        await ws.send(json.dumps({"error": err}))
        except Exception as e:
            print(f"⚠️ WebSocket connection lost: {e}, retrying in 5s...")
            await asyncio.sleep(5)


async def serve_dashboard():
    """Serve the Oasira dashboard with integrated Matter Hub API."""
    try:
        dashboard_path = Path("/app/dist")
        
        if not dashboard_path.exists():
            print(f"⚠️ Dashboard files not found at {dashboard_path}")
            print("   Dashboard will not be available")
            return
        
        print(f"📊 Starting unified Oasira server on port {dashboard_port}...")
        
        app = web.Application()
        
        # Main dashboard handler
        async def index_handler(request):
            try:
                index_file = dashboard_path / 'index.html'
                if index_file.exists():
                    response = web.FileResponse(index_file)
                    # Disable caching for index.html to ensure fresh loads
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    return response
                else:
                    return web.Response(text="Dashboard not available", status=404)
            except Exception as e:
                print(f"❌ Error serving index: {e}")
                return web.Response(text="Internal server error", status=500)
        
        # Static file handler
        async def static_handler(request):
            try:
                filename = request.match_info['filename']
                filepath = dashboard_path / filename
                
                # Log request for debugging
                print(f"📄 [Dashboard] Request: {request.method} /{filename}")
                
                if filepath.exists() and filepath.is_file():
                    response = web.FileResponse(filepath)
                    # Explicitly set MIME types for JavaScript files (critical for service workers)
                    if filename.endswith('.js'):
                        response.headers['Content-Type'] = 'application/javascript'
                        print(f"✅ [Dashboard] Serving JS file: {filename} (Content-Type: application/javascript)")
                    elif filename.endswith('.mjs'):
                        response.headers['Content-Type'] = 'application/javascript'
                        print(f"✅ [Dashboard] Serving MJS file: {filename} (Content-Type: application/javascript)")
                    return response
                # If file not found, serve index.html for SPA routing
                print(f"⚠️ [Dashboard] File not found: {filename}, serving index.html")
                return await index_handler(request)
            except Exception as e:
                print(f"❌ Error serving static file: {e}")
                return web.Response(text="Internal server error", status=500)
        
        # Register routes - API routes first!
        # Matter API routes - these are checked FIRST
        app.router.add_route('*', '/api/matter', proxy_to_matter_backend)
        app.router.add_route('*', '/api/matter/{path:.*}', proxy_to_matter_backend)
        
        print("✅ Matter API proxy configured at /api/matter/")
        
        # Dashboard routes - these come AFTER API routes
        app.router.add_get('/', index_handler)
        app.router.add_static('/assets', path=dashboard_path / 'assets', name='assets', show_index=False)
        # Serve other static files and handle SPA routing (but API routes already matched above)
        app.router.add_get('/{filename:.+}', static_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', dashboard_port)
        await site.start()
        
        print(f"✅ Unified server running at http://0.0.0.0:{dashboard_port}")
        print(f"   - Main Dashboard: http://0.0.0.0:{dashboard_port}/")
        print(f"   - Matter API (proxied): http://0.0.0.0:{dashboard_port}/api/matter/")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
    
    except asyncio.CancelledError:
        print("⚠️ Dashboard server cancelled")
        raise
    except Exception as e:
        print(f"❌ Failed to start dashboard server: {e}")
        import traceback
        traceback.print_exc()


# Global Matter backend process reference
matter_backend_process = None
matter_backend_healthy = False

async def start_matter_backend():
    """Start the Matter.js backend server with automatic restart on failure."""
    global matter_backend_process, matter_backend_healthy
    
    cli_path = Path("/app/packages/backend/dist/cli.js")
    
    print(f"🔍 Checking Matter backend at {cli_path}")
    print(f"   - CLI exists: {cli_path.exists()}")
    
    if not cli_path.exists():
        print("⚠️ Matter backend cli.js not found, skipping...")
        return
    
    retry_count = 0
    max_retries = 5
    retry_delay = 10
    
    while True:
        try:
            print("🔷 Starting Matter.js backend server...")
            matter_backend_healthy = False
            
            # Set environment variables for Matter backend
            env = os.environ.copy()
            env["STORAGE_PATH"] = "/data/matter"
            env["HA_URL"] = ha_url or ""
            env["HA_TOKEN"] = ha_token or ""
            # Set NODE_PATH to include both pnpm store and node_modules
            env["NODE_PATH"] = "/app/node_modules:/app/node_modules/.pnpm/node_modules"
            
            print(f"   - HA_URL: {ha_url}")
            print(f"   - Storage: /data/matter")
            print(f"   - HTTP Port: 8482")
            
            # Start Matter backend as subprocess
            matter_backend_process = await asyncio.create_subprocess_exec(
                "node",
                "--experimental-specifier-resolution=node",
                str(cli_path),
                "start",
                "--storage-location", "/data/matter",
                "--http-port", "8482",
                "--home-assistant-url", ha_url or "",
                "--home-assistant-access-token", ha_token or "",
                env=env,
                cwd="/app/packages/backend",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            print(f"✅ Matter backend started (PID: {matter_backend_process.pid})")
            retry_count = 0  # Reset retry count on successful start
            
            # Monitor output with error handling
            async def read_output(stream, prefix):
                try:
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        decoded = line.decode().strip()
                        if decoded:
                            print(f"{prefix}: {decoded}")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"⚠️ Error reading {prefix} output: {e}")
            
            # Create monitored tasks
            stdout_task = asyncio.create_task(read_output(matter_backend_process.stdout, "Matter"))
            stderr_task = asyncio.create_task(read_output(matter_backend_process.stderr, "Matter-ERR"))
            
            # Wait a moment then mark as healthy
            await asyncio.sleep(5)
            matter_backend_healthy = True
            print("✅ Matter backend marked as healthy")
            
            # Monitor process
            returncode = await matter_backend_process.wait()
            matter_backend_healthy = False
            
            # Cancel output tasks
            stdout_task.cancel()
            stderr_task.cancel()
            
            print(f"⚠️ Matter backend exited with code {returncode}")
            
            # If process exits cleanly, wait before restart
            retry_count += 1
            if retry_count >= max_retries:
                print(f"❌ Matter backend failed {max_retries} times, stopping restart attempts")
                break
            
            print(f"🔄 Restarting Matter backend in {retry_delay} seconds (attempt {retry_count}/{max_retries})...")
            await asyncio.sleep(retry_delay)
            
        except asyncio.CancelledError:
            print("⚠️ Matter backend task cancelled")
            matter_backend_healthy = False
            break
        except Exception as e:
            matter_backend_healthy = False
            print(f"❌ Failed to start Matter backend: {e}")
            import traceback
            traceback.print_exc()
            
            retry_count += 1
            if retry_count >= max_retries:
                print(f"❌ Matter backend failed {max_retries} times, stopping restart attempts")
                break
            
            print(f"🔄 Retrying in {retry_delay} seconds (attempt {retry_count}/{max_retries})...")
            await asyncio.sleep(retry_delay)
        import traceback
        traceback.print_exc()

async def check_matter_backend_health():
    """Check if Matter backend is responding."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8482/api/matter/bridges", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
    except Exception:
        return False

async def health_check_loop():
    """Periodically check Matter backend health and restart if needed."""
    global matter_backend_process, matter_backend_healthy
    
    # Wait for initial startup
    await asyncio.sleep(30)
    
    while True:
        try:
            await asyncio.sleep(60)  # Check every 60 seconds
            
            if not matter_backend_healthy:
                print("⚠️ Matter backend not marked as healthy, skipping health check")
                continue
            
            is_healthy = await check_matter_backend_health()
            
            if not is_healthy:
                print("❌ Matter backend health check failed")
                
                # Try to restart the backend
                if matter_backend_process and matter_backend_process.returncode is None:
                    print("🔄 Terminating unresponsive Matter backend...")
                    try:
                        matter_backend_process.terminate()
                        await asyncio.sleep(5)
                        if matter_backend_process.returncode is None:
                            matter_backend_process.kill()
                    except Exception as e:
                        print(f"⚠️ Error terminating process: {e}")
                
                matter_backend_healthy = False
                print("✅ Matter backend will be restarted automatically")
            else:
                print("✅ Matter backend health check passed")
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️ Health check error: {e}")

async def ensure_default_bridge():
    """Create a default Matter bridge if none exists."""
    try:
        # Wait for Matter backend to be ready (with retry logic)
        max_retries = 30
        retry_delay = 2
        backend_ready = False
        
        print("⏳ Waiting for Matter backend to be ready...")
        for attempt in range(max_retries):
            try:
                if await check_matter_backend_health():
                    backend_ready = True
                    print(f"✅ Matter backend is ready (attempt {attempt + 1})")
                    break
            except Exception:
                pass
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                    
        if not backend_ready:
            print("⚠️ Matter backend did not become ready in time")
            return
            
        # Check if any bridges exist
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8482/api/matter/bridges") as resp:
                if resp.status == 200:
                    bridges = await resp.json()
                    if len(bridges) == 0:
                        print(f"📦 Creating default Matter bridge with label filter: '{matter_label}'...")
                        
                        # Create default bridge with configured label filter
                        bridge_config = {
                            "name": "Oasira Matter Bridge",
                            "port": 5540,
                            "filter": {
                                "include": [{"type": "label", "value": matter_label}],
                                "exclude": []
                            }
                        }
                        
                        async with session.post(
                            "http://localhost:8482/api/matter/bridges",
                            json=bridge_config,
                            headers={"Content-Type": "application/json"}
                        ) as create_resp:
                            if create_resp.status == 201:
                                bridge = await create_resp.json()
                                print(f"✅ Created default bridge: {bridge.get('id')}")
                            else:
                                error = await create_resp.text()
                                print(f"⚠️ Failed to create default bridge: {error}")
                    else:
                        print(f"✅ Found {len(bridges)} existing bridge(s)")
                else:
                    print(f"⚠️ Could not check bridges: HTTP {resp.status}")
    except Exception as e:
        print(f"⚠️ Could not create default bridge: {e}")
        import traceback
        traceback.print_exc()

async def task_wrapper(coro, name):
    """Wrapper to handle exceptions in background tasks."""
    try:
        await coro
    except asyncio.CancelledError:
        print(f"⚠️ Task '{name}' was cancelled")
    except Exception as e:
        print(f"❌ Unhandled error in task '{name}': {e}")
        import traceback
        traceback.print_exc()

async def refresh_firebase_token_loop():
    """Periodically refresh the Firebase ID token."""
    global id_token, refresh_token
    
    if not refresh_token:
        print("⚠️ No refresh token available - cannot refresh Firebase token")
        return
    
    # Wait 50 minutes before first refresh (tokens expire in 60 minutes)
    await asyncio.sleep(50 * 60)
    
    while True:
        try:
            print("🔄 Refreshing Firebase ID token...")
            
            async with OasiraAPIClient() as client:
                result = await client.firebase_refresh_token(refresh_token)
                
                new_id_token = result.get("idToken")
                new_refresh_token = result.get("refreshToken")
                
                if new_id_token:
                    id_token = new_id_token
                    
                    if new_refresh_token:
                        refresh_token = new_refresh_token
                    
                    print("✅ Firebase ID token refreshed successfully")
                else:
                    print("❌ Failed to refresh Firebase token - no idToken in response")
                    
        except OasiraAPIError as e:
            print(f"❌ Failed to refresh Firebase token: {e}")
            # Continue trying even if refresh fails
        except Exception as e:
            print(f"❌ Unexpected error refreshing Firebase token: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait another 50 minutes before next refresh
        await asyncio.sleep(50 * 60)

async def main():
    """Main entry point with comprehensive error handling."""
    try:
        success = await start()
        
        if not success:
            print("❌ Start failed. Exiting...")
            return

        # Start Firebase token refresh loop
        print("\n🔄 Starting Firebase Token Refresh Monitor...")
        asyncio.create_task(task_wrapper(refresh_firebase_token_loop(), "Firebase Token Refresh"))

        # Start cloudflared tunnel with error handling
        print("\n🌩️ Starting Cloudflare tunnel...")
        asyncio.create_task(task_wrapper(start_cloudflared(), "Cloudflare Tunnel"))
        await asyncio.sleep(2)  # Give cloudflared a moment to start
        
        # Start Matter backend with error handling
        print("\n🔷 Starting Matter Backend...")
        asyncio.create_task(task_wrapper(start_matter_backend(), "Matter Backend"))
        await asyncio.sleep(5)  # Give Matter backend a moment to start
        
        # Start health check loop
        print("\n❤️ Starting Health Check Monitor...")
        asyncio.create_task(task_wrapper(health_check_loop(), "Health Check"))
        
        # Ensure default bridge exists
        print("\n🌉 Checking Default Bridge...")
        asyncio.create_task(task_wrapper(ensure_default_bridge(), "Default Bridge"))
        
        # Start unified dashboard server with integrated Matter UI
        print("\n📊 Starting Unified Dashboard...")
        asyncio.create_task(task_wrapper(serve_dashboard(), "Dashboard Server"))
        
        # Keep the main coroutine running
        print("\n✅ All services started. Running...")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\n⚠️ Received shutdown signal")
    except Exception as e:
        print(f"\n❌ Fatal error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

