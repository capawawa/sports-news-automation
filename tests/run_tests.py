#!/usr/bin/env python3
"""
Test runner script for the Sports News Automation system.
This script provides a simple way to run the test suite.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite with pytest."""
    # Change to the project directory
    project_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(project_dir)
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', '-v'
        ], check=True, capture_output=True, text=True)
        
        print("Tests completed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("Tests failed!")
        print(e.stdout)
        print(e.stderr)
        return False


def run_tests_with_coverage():
    """Run the test suite with coverage reporting."""
    # Change to the project directory
    project_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(project_dir)
    
    # Run pytest with coverage
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 'tests/', 
            '--cov=src', '--cov-report=html', '--cov-report=term'
        ], check=True, capture_output=True, text=True)
        
        print("Tests with coverage completed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("Tests with coverage failed!")
        print(e.stdout)
        print(e.stderr)
        return False


if __name__ == '__main__':
    if '--coverage' in sys.argv:
        run_tests_with_coverage()
    else:
        run_tests()