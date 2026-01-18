"""
Demo script để khởi chạy IoT Network Selection Web UI.

Script này sẽ:
1. Khởi động FastAPI server với CORS support
2. Serve web UI tại http://localhost:8000/ui
3. Provide API endpoints cho map visualization

Chạy: python demo_web_ui.py
"""

import uvicorn
import webbrowser
import time
import threading
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def open_browser():
    """Open web browser after server starts"""
    time.sleep(2)  # Wait for server to start
    try:
        print("🌐 Opening web browser...")
        webbrowser.open('http://localhost:8000/ui')
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("🌐 Please open http://localhost:8000/ui manually")

def main():
    print("🚀 Starting IoT Network Selection Web UI Demo")
    print("=" * 60)
    print()
    
    # Print instructions
    print("📋 Instructions:")
    print("1. Web UI will open automatically at http://localhost:8000/ui")
    print("2. Use the control panel to run simulation steps")
    print("3. Click 'Make Decision' to test the MCDM algorithm")
    print("4. Toggle 'Auto-run' for continuous simulation")
    print("5. Click on the map to manually place the device")
    print()
    print("🌐 API Endpoints:")
    print("   - http://localhost:8000/docs (Swagger UI)")
    print("   - http://localhost:8000/ui (Map Visualization)")
    print("   - http://localhost:8000/map (Map data API)")
    print()
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start FastAPI server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app", "web"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        print("💡 Make sure port 8000 is available and try again")

if __name__ == "__main__":
    main()