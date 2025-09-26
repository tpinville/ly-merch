#!/usr/bin/env python3
"""
Simple test runner for CI/CD environments
"""

import os
import sys
import subprocess
import argparse


def run_command(cmd: str, cwd: str = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    result = subprocess.run(
        cmd.split(),
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="LY-Merch API Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Default to running all tests
    if not args.unit and not args.integration:
        args.unit = True
        args.integration = True

    exit_code = 0

    # Install test dependencies
    print("📦 Installing test dependencies...")
    code, stdout, stderr = run_command("pip install -r requirements-test.txt")
    if code != 0:
        print("❌ Failed to install test dependencies")
        print(stderr)
        return 1

    # Run unit tests
    if args.unit:
        print("🧪 Running unit tests...")

        cmd = "pytest tests/"
        if args.verbose:
            cmd += " -v"
        if args.coverage:
            cmd += " --cov=app --cov-report=term-missing --cov-report=xml"

        code, stdout, stderr = run_command(cmd)
        print(stdout)
        if stderr:
            print(stderr)

        if code != 0:
            print("❌ Unit tests failed")
            exit_code = 1
        else:
            print("✅ Unit tests passed")

    # Run integration tests (if API is running)
    if args.integration:
        print("🔧 Running integration tests...")

        # Check if API is running
        try:
            import requests
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is running, proceeding with integration tests")

                # Run integration test script
                code, stdout, stderr = run_command("python3 ../scripts/test-api-integration.py")
                print(stdout)
                if stderr:
                    print(stderr)

                if code != 0:
                    print("❌ Integration tests failed")
                    exit_code = 1
                else:
                    print("✅ Integration tests passed")
            else:
                print("⚠️  API not responding, skipping integration tests")
        except:
            print("⚠️  API not available, skipping integration tests")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())