#!/usr/bin/env python3
"""
Test script to verify Render deployment readiness.
Run this before deploying to catch issues early.
"""
import sys
import os

def check_imports():
    """Check if critical imports work."""
    print("🔍 Checking critical imports...")

    try:
        from app.main import app
        print("✅ FastAPI app imports successfully")
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return False

    try:
        from app.core.database import connect_to_mongo, get_database
        print("✅ Database module imports successfully")
    except Exception as e:
        print(f"❌ Failed to import database: {e}")
        return False

    try:
        from app.core.cache import cache_manager
        print("✅ Cache module imports successfully")
    except Exception as e:
        print(f"❌ Failed to import cache: {e}")
        return False

    return True


def check_env_vars():
    """Check required environment variables."""
    print("\n🔍 Checking environment variables...")

    required = ["MONGODB_URI", "SECRET_KEY"]
    optional = ["REDIS_URL", "MAIL_USERNAME", "OPENROUTER_API_KEY"]

    missing_required = []
    for var in required:
        if not os.getenv(var):
            missing_required.append(var)

    if missing_required:
        print(f"❌ Missing required env vars: {', '.join(missing_required)}")
        print("   Set these in Render dashboard or .env file")
        return False
    else:
        print(f"✅ All required env vars present")

    missing_optional = [var for var in optional if not os.getenv(var)]
    if missing_optional:
        print(f"⚠️  Optional env vars not set: {', '.join(missing_optional)}")
        print("   Some features will be disabled")

    return True


def check_function_calls():
    """Check that the problematic function call is fixed."""
    print("\n🔍 Checking main.py for correct function calls...")

    try:
        with open("app/main.py", "r") as f:
            content = f.read()

            if "get_database_client()" in content:
                print("❌ Found get_database_client() - this function doesn't exist!")
                print("   Should use get_database() instead")
                return False

            if "get_database()" in content:
                print("✅ Using correct get_database() function")

    except FileNotFoundError:
        print("❌ app/main.py not found")
        return False

    return True


def check_requirements():
    """Check requirements files."""
    print("\n🔍 Checking requirements files...")

    if os.path.exists("requirements-prod.txt"):
        print("✅ requirements-prod.txt exists (for Render)")
    else:
        print("⚠️  requirements-prod.txt not found")

    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt exists (for development)")

        with open("requirements.txt", "r") as f:
            lines = f.readlines()
            heavy = [l for l in lines if any(pkg in l for pkg in ["scikit-learn", "numpy", "tensorflow"])]
            if heavy:
                print(f"⚠️  Heavy packages in requirements.txt: {', '.join(p.strip() for p in heavy)}")
                print("   Consider using requirements-prod.txt for Render")

    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("🚀 RENDER DEPLOYMENT READINESS CHECK")
    print("=" * 60)

    checks = [
        ("Imports", check_imports),
        ("Environment Variables", check_env_vars),
        ("Function Calls", check_function_calls),
        ("Requirements", check_requirements)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error in {name} check: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED - Ready for Render deployment!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Commit changes: git add . && git commit -m 'fix: render deployment'")
        print("2. Push to trigger deploy: git push")
        print("3. Monitor build in Render dashboard")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Fix issues before deploying")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    # Set dummy env vars for testing
    if not os.getenv("MONGODB_URI"):
        os.environ["MONGODB_URI"] = "mongodb://localhost:27017/test"
    if not os.getenv("SECRET_KEY"):
        os.environ["SECRET_KEY"] = "test-secret-key"

    sys.exit(main())
