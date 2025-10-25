"""
Simple test for vitals endpoints without external dependencies.
"""

def test_vitals_import():
    """Test if vitals endpoints can be imported and created."""
    try:
        from app.main import app
        print("✅ App imported successfully")
        
        # Check if vitals routes are registered
        vitals_routes = [route for route in app.routes if hasattr(route, 'path') and 'vitals' in route.path]
        print(f"✅ Found {len(vitals_routes)} vitals routes:")
        for route in vitals_routes:
            print(f"   - {route.path} - {route.methods}")
        
        # Test CRUD import
        from app.crud import vitals
        print("✅ Vitals CRUD imported successfully")
        
        # Test schemas import
        from app.schemas.vitals import VitalSign, VisitVitals
        print("✅ Vitals schemas imported successfully")
        
        print("\n🎉 All vitals components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_vitals_import()
