#!/usr/bin/env python3
"""
Test script to verify all routes are properly registered
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.main import app

def test_routes():
    """Test that all routes are registered"""
    
    print("🔍 Checking registered routes...")
    
    # Get all routes from the FastAPI app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods)
            })
    
    print(f"\n📋 Found {len(routes)} routes:")
    print("-" * 50)
    
    for route in routes:
        methods_str = ", ".join(route['methods'])
        print(f"{route['path']:<30} [{methods_str}]")
    
    # Check for our specific routes
    advanced_routes = [r for r in routes if '/advanced' in r['path']]
    
    print(f"\n🎯 Advanced Processing Routes: {len(advanced_routes)}")
    print("-" * 50)
    
    if advanced_routes:
        for route in advanced_routes:
            methods_str = ", ".join(route['methods'])
            print(f"✅ {route['path']:<30} [{methods_str}]")
    else:
        print("❌ No advanced processing routes found!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the server is restarted after adding new routes")
        print("2. Check that advanced_processing.py is in backend/routes/")
        print("3. Verify the import in main.py is correct")
    
    return len(advanced_routes) > 0

if __name__ == "__main__":
    success = test_routes()
    if success:
        print("\n✅ All routes are properly registered!")
    else:
        print("\n❌ Route registration failed!")
        print("\n💡 Solution: Restart the backend server")
        print("   Run: uvicorn backend.main:app --reload")
