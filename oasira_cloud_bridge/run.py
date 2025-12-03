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


async def start_matterhub():
    """Install and start Home Assistant Matter Hub."""

    if not ha_url or not ha_token:
        print("HA_URL or HA_TOKEN environment variables not set. Cannot start Oasira.")
        return

    # Step 1: install npm if not present
    npm_installed = False
    try:
        proc_check_npm = await asyncio.create_subprocess_exec("npm", "--version", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        await proc_check_npm.wait()
        if proc_check_npm.returncode == 0:
            print("npm is already installed.")
            npm_installed = True
    except FileNotFoundError:
        print("npm not found.")

    if not npm_installed:
        print("Installing npm via apk...")
        try:
            proc_apk = await asyncio.create_subprocess_exec(
                "apk", "add", "npm",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await proc_apk.communicate()
            if out:
                print(f"apk stdout: {out.decode()}")
            if err:
                print(f"apk stderr: {err.decode()}")
            if proc_apk.returncode != 0:
                print(f"apk add npm failed with code {proc_apk.returncode}")
                return
        except FileNotFoundError:
            print("apk not available in this environment. Cannot install npm.")
            return

    # Step 2: Check or install home-assistant-matter-hub
    hamh_installed = False
    try:
        proc_check_hamh = await asyncio.create_subprocess_exec(
            "home-assistant-matter-hub", "--help",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc_check_hamh.wait()
        if proc_check_hamh.returncode == 0:
            print("home-assistant-matter-hub is already installed.")
            hamh_installed = True
    except FileNotFoundError:
        print("home-assistant-matter-hub not found.")

    if not hamh_installed:
        print("Installing home-assistant-matter-hub globally...")
        proc_npm = await asyncio.create_subprocess_exec(
            "npm", "install", "-g", "home-assistant-matter-hub",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc_npm.communicate()
        if out:
            print(f"npm stdout: {out.decode()}")
        if err:
            print(f"npm stderr: {err.decode()}")
        if proc_npm.returncode != 0:
            print(f"npm install failed with code {proc_npm.returncode}")
            return
        else:
            print("home-assistant-matter-hub installed successfully.")

    # Step 3: Run home-assistant-matter-hub in the background
    print("Starting home-assistant-matter-hub...")
    
    CONFIG_PATH = "/data/options.json"  # Home Assistant injects add-on config here
    STORAGE_PATH = "/data/matterhub"    # /data is persistent storage
    HAMH_BINARY = "/usr/local/bin/home-assistant-matter-hub"

    if not os.path.exists(CONFIG_PATH):
        print("⚠️ No options.json found.")
        return

    with open(CONFIG_PATH, "r") as f:
        options = json.load(f)
    
    os.makedirs(STORAGE_PATH, exist_ok=True)

    try:
        proc_hamh = await asyncio.create_subprocess_exec(
            "home-assistant-matter-hub", "start",
            f"--home-assistant-url={ha_url}",
            f"--home-assistant-access-token={ha_token}",     
            "--log-level=debug",
            "--http-port=8482",
            f"--storage-location={STORAGE_PATH}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def log_output(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                print(f"{prefix}: {line.decode().strip()}")

        # Start logging tasks
        asyncio.create_task(log_output(proc_hamh.stdout, "matterhub-out"))
        asyncio.create_task(log_output(proc_hamh.stderr, "matterhub-err"))

        print(f"home-assistant-matter-hub process started with PID {proc_hamh.pid}")

        # Prevent the loop from closing before the subprocess ends
        try:
            await proc_hamh.wait()
        except asyncio.CancelledError:
            print("Shutting down home-assistant-matter-hub...")
            proc_hamh.terminate()
            await proc_hamh.wait()

    except FileNotFoundError:
        print("home-assistant-matter-hub command not found after install. Check PATH or npm global install.")
    except Exception as exc:
        print(f"Error running home-assistant-matter-hub: {exc}")


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
    """Serve the Oasira dashboard on the configured port."""
    dashboard_path = Path("/app/dist")
    
    if not dashboard_path.exists():
        print(f"⚠️ Dashboard files not found at {dashboard_path}")
        print("   Dashboard will not be available")
        return
    
    print(f"📊 Starting Oasira Dashboard server on port {dashboard_port}...")
    
    app = web.Application()
    
    # Root route - serve index.html with proper headers
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
    
    app.router.add_get('/', index_handler)
    
    # Serve static files (assets, js, css, etc)
    app.router.add_static('/', path=dashboard_path, name='static', show_index=True)
    
    # Catch-all route for SPA routing (must be last)
    app.router.add_get('/{path:.*}', index_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', dashboard_port)
    await site.start()
    
    print(f"✅ Dashboard server running at http://0.0.0.0:{dashboard_port}")
    
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
    
    # Start Matter Hub
    print("\n🔗 Starting Matter Hub...")
    asyncio.create_task(start_matterhub())
    await asyncio.sleep(2)  # Give matterhub a moment to start
    
    # Start dashboard server in background
    print("\n📊 Starting Dashboard...")
    asyncio.create_task(serve_dashboard())
    
    # Keep the main coroutine running
    await asyncio.Event().wait()

    #await register_with_server()
    #await connect_to_cloud()

if __name__ == "__main__":
    asyncio.run(main())

