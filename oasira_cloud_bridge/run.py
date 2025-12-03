import os
import asyncio
import json
import aiohttp
import websockets
import uuid
from pathlib import Path
from aiohttp import web
from oasira import OasiraAPIClient, OasiraAPIError

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
SUPERVISOR_URL = "http://supervisor/core/api"

# Load addon options
with open("/data/options.json") as f:
    options = json.load(f)

email = options.get("email")
password = options.get("password")
system_id = options.get("system_id")
ha_url = options.get("ha_url", "http://homeassistant.local:8123")
dashboard_port = options.get("dashboard_port", 8080)

cloudflare_token = None
ha_token = None
customer_psk = None
fullname = None
emailaddress = None
ha_external_url = None
customer_id = None
systemid = None
testmode = None
plan = None
trial_expiration = None
id_token = None

CLIENT_ID = str(uuid.uuid4())  # Unique ID for this HA instance

##TODO: need to select correct cloudflared binary based on host system os

async def start():
    """Authenticate with Firebase OAuth and fetch system configuration."""
    global cloudflare_token, ha_token, customer_psk, fullname, emailaddress
    global ha_external_url, systemid, testmode, plan, trial_expiration
    global customer_id, system_id, id_token

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
            
            if not firebase_uid or not id_token:
                print("❌ Firebase authentication failed - missing tokens")
                return False
            
            print(f"✅ Firebase authentication successful (UID: {firebase_uid})")

        # Step 2: Fetch available systems for this user
        async with OasiraAPIClient(
            id_token=id_token
        ) as client:
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

        # Step 4: Fetch full system configuration
        async with OasiraAPIClient(
            system_id=system_id,
            id_token=id_token
        ) as client:
            print(f"📦 Fetching system configuration...")
            print(f"🔍 Debug - API client initialized with system_id: {client.system_id}")
            data = await client.get_customer_and_system()

            customer_psk = data.get("psk")
            fullname = data.get("fullname")
            emailaddress = data.get("emailaddress")
            ha_token = data.get("ha_security_token")
            cloudflare_token = data.get("cloudflare_token")
            ha_external_url = data.get("ha_url")
            systemid = system_id
            testmode = data.get("testmode")
            plan = data.get("name")
            trial_expiration = data.get("trial_expiration")

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
    """Download, install, and run cloudflared binary."""
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
            while True:
                line = await stream.readline()
                if not line:
                    break
                print(f"{prefix}: {line.decode().strip()}")

        asyncio.create_task(log_output(proc.stdout, "cloudflared-out"))
        asyncio.create_task(log_output(proc.stderr, "cloudflared-err"))

        print("cloudflared tunnel process started.")

    except FileNotFoundError:
        print("cloudflared binary not found. Installation might have failed.")
    except Exception as exc:
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

def save_matter_config():
    """Save Matter bridge configuration to disk."""
    config_file = Path(MATTER_STORAGE_PATH) / "bridges.json"
    os.makedirs(MATTER_STORAGE_PATH, exist_ok=True)
    try:
        with open(config_file, 'w') as f:
            json.dump(matter_bridges, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving Matter config: {e}")


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
    """Serve the Oasira dashboard with integrated Matter Hub on the same port."""
    dashboard_path = Path("/app/dist")
    matter_frontend_path = Path("/app/matter-frontend")
    
    if not dashboard_path.exists():
        print(f"⚠️ Dashboard files not found at {dashboard_path}")
        print("   Dashboard will not be available")
        return
    
    print(f"📊 Starting unified Oasira server on port {dashboard_port}...")
    
    # Load Matter configuration
    load_matter_config()
    
    app = web.Application()
    
    # Matter API endpoints
    async def matter_api_root(request):
        """Root Matter API endpoint."""
        return web.json_response({})
    
    async def matter_api_bridges_list(request):
        """List all Matter bridges."""
        bridges_list = list(matter_bridges.values())
        return web.json_response(bridges_list)
    
    async def matter_api_bridges_create(request):
        """Create a new Matter bridge."""
        try:
            data = await request.json()
            bridge_id = data.get('id', str(uuid.uuid4()))
            bridge = {
                'id': bridge_id,
                'name': data.get('name', 'Matter Bridge'),
                'port': data.get('port', 5540),
                'filter': data.get('filter', {}),
                'enabled': data.get('enabled', True),
                'created': data.get('created', asyncio.get_event_loop().time())
            }
            matter_bridges[bridge_id] = bridge
            save_matter_config()
            return web.json_response(bridge)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=400)
    
    async def matter_api_bridges_get(request):
        """Get a specific Matter bridge."""
        bridge_id = request.match_info['bridgeId']
        if bridge_id in matter_bridges:
            return web.json_response(matter_bridges[bridge_id])
        return web.Response(text="Not Found", status=404)
    
    async def matter_api_bridges_update(request):
        """Update a Matter bridge."""
        bridge_id = request.match_info['bridgeId']
        if bridge_id not in matter_bridges:
            return web.Response(text="Not Found", status=404)
        try:
            data = await request.json()
            if data.get('id') != bridge_id:
                return web.Response(text="Bridge ID mismatch", status=400)
            matter_bridges[bridge_id].update(data)
            save_matter_config()
            return web.json_response(matter_bridges[bridge_id])
        except Exception as e:
            return web.json_response({'error': str(e)}, status=400)
    
    async def matter_api_bridges_delete(request):
        """Delete a Matter bridge."""
        bridge_id = request.match_info['bridgeId']
        if bridge_id in matter_bridges:
            del matter_bridges[bridge_id]
            save_matter_config()
        return web.Response(status=204)
    
    async def matter_api_bridges_reset(request):
        """Factory reset a Matter bridge."""
        bridge_id = request.match_info['bridgeId']
        if bridge_id not in matter_bridges:
            return web.Response(text="Not Found", status=404)
        # Reset bridge to defaults
        bridge = matter_bridges[bridge_id]
        bridge['filter'] = {}
        bridge['enabled'] = True
        save_matter_config()
        return web.json_response(bridge)
    
    async def matter_api_bridges_devices(request):
        """Get devices for a Matter bridge."""
        bridge_id = request.match_info['bridgeId']
        if bridge_id not in matter_bridges:
            return web.Response(text="Not Found", status=404)
        
        # Query Home Assistant for devices
        # This would integrate with HA's Matter integration
        devices = {
            'endpoints': [],
            'bridgeInfo': matter_bridges[bridge_id]
        }
        return web.json_response(devices)
    
    # Matter UI handler - serve index.html with base path
    async def matter_ui_handler(request):
        """Serve the Matter frontend."""
        index_file = matter_frontend_path / 'index.html'
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Set base path for Matter UI assets
            if '<base' not in content:
                # Insert base tag in head if not present
                content = content.replace('<head>', '<head>\n  <base href="/matter/" />', 1)
            response = web.Response(text=content, content_type='text/html')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            return web.Response(text="Matter UI not available", status=404)
    
    # Main dashboard handler
    async def index_handler(request):
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
    
    # Register routes - order matters!
    # Matter API routes
    app.router.add_get('/matter/api/', matter_api_root)
    app.router.add_get('/matter/api/matter/bridges', matter_api_bridges_list)
    app.router.add_post('/matter/api/matter/bridges', matter_api_bridges_create)
    app.router.add_get('/matter/api/matter/bridges/{bridgeId}', matter_api_bridges_get)
    app.router.add_put('/matter/api/matter/bridges/{bridgeId}', matter_api_bridges_update)
    app.router.add_delete('/matter/api/matter/bridges/{bridgeId}', matter_api_bridges_delete)
    app.router.add_get('/matter/api/matter/bridges/{bridgeId}/actions/factory-reset', matter_api_bridges_reset)
    app.router.add_get('/matter/api/matter/bridges/{bridgeId}/devices', matter_api_bridges_devices)
    
    # Matter UI routes (static frontend)
    if matter_frontend_path.exists():
        app.router.add_get('/matter/', matter_ui_handler)
        app.router.add_get('/matter/index.html', matter_ui_handler)
        app.router.add_static('/matter/', path=matter_frontend_path, name='matter-static', show_index=False)
        print("✅ Matter Hub integrated at /matter/")
        print("✅ Matter API integrated at /matter/api/")
    else:
        print(f"⚠️ Matter frontend not found at {matter_frontend_path}")
    
    # Main dashboard routes
    app.router.add_get('/', index_handler)
    app.router.add_static('/', path=dashboard_path, name='static', show_index=True)
    app.router.add_get('/{path:.*}', index_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', dashboard_port)
    await site.start()
    
    print(f"✅ Unified server running at http://0.0.0.0:{dashboard_port}")
    print(f"   - Main Dashboard: http://0.0.0.0:{dashboard_port}/")
    print(f"   - Matter Hub UI: http://0.0.0.0:{dashboard_port}/matter/")
    print(f"   - Matter API: http://0.0.0.0:{dashboard_port}/matter/api/")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)


async def main():
    success = await start()
    
    if not success:
        print("❌ Start failed. Exiting...")
        return

    # Start cloudflared tunnel
    print("\n🌩️ Starting Cloudflare tunnel...")
    asyncio.create_task(start_cloudflared())
    await asyncio.sleep(2)  # Give cloudflared a moment to start
    
    # Start unified dashboard server with integrated Matter UI
    print("\n📊 Starting Unified Dashboard...")
    asyncio.create_task(serve_dashboard())
    
    # Keep the main coroutine running
    await asyncio.Event().wait()

    #await register_with_server()
    #await connect_to_cloud()

if __name__ == "__main__":
    asyncio.run(main())

