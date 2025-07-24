#!/usr/bin/env python3
"""
Simplified documentation generation script for ATA_V3 project.

This script generates comprehensive HTML documentation for the entire ATA_V3 codebase
using pdoc with basic configuration and custom styling.

Usage:
    python generate_docs_simple.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Project information
project_name = "ATA_V3"
project_description = "Automated Test Automation Framework"
project_version = "3.0"
project_author = "ATA Development Team"
output_dir = "docs"

def clean_output_directory():
    """Clean the output directory before generating new documentation."""
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"Cleaning existing documentation in {output_dir}...")
        shutil.rmtree(output_path)
    output_path.mkdir(exist_ok=True)
    print(f"Output directory prepared: {output_dir}")

def clean_build_artifacts():
    """Clean PyInstaller build artifacts that might interfere with documentation generation."""
    build_dirs = [
        "src/gui/build",
        "src/gui/dist", 
        "build",
        "dist"
    ]
    
    for build_dir in build_dirs:
        if Path(build_dir).exists():
            print(f"Removing build artifacts: {build_dir}")
            shutil.rmtree(build_dir)

def generate_documentation():
    """Generate HTML documentation using pdoc."""
    print("Generating HTML documentation...")
    print(f"Project: {project_name} v{project_version}")
    print(f"Description: {project_description}")
    print(f"Author: {project_author}")
    print("-" * 60)
    
    # Simple pdoc command
    cmd = [
        sys.executable, "-m", "pdoc",
        "--html",  # Generate HTML output
        "-o", output_dir,  # Output directory
        "-f",  # Force overwrite existing files
        "src"  # Document the src package
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        # Run pdoc
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Documentation generation completed successfully!")
        print("Generated files:")
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Info:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Error generating documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    
    return True

def create_index_page():
    """Create a custom index page for the documentation."""
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - API Documentation</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 3rem;
            font-weight: 300;
        }}
        .header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .content {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .module-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .module-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .module-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .module-card h3 {{
            color: #667eea;
            margin-top: 0;
            font-size: 1.3rem;
        }}
        .module-card p {{
            color: #6c757d;
            margin-bottom: 1rem;
        }}
        .module-card a {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .module-card a:hover {{
            background: #5a6fd8;
        }}
        .info-section {{
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .info-section h2 {{
            color: #1976d2;
            margin-top: 0;
        }}
        .info-section ul {{
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }}
        .info-section li {{
            margin: 0.25rem 0;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e9ecef;
        }}
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            .module-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{project_name}</h1>
        <p>{project_description}</p>
        <p>Version {project_version} - Comprehensive API Documentation</p>
    </div>
    
    <div class="content">
        <div class="info-section">
            <h2>About {project_name}</h2>
            <p>{project_description} is a comprehensive automated testing framework designed for creating, 
            recording, and executing automated tests with advanced image recognition capabilities.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li><strong>Test Recording:</strong> Record mouse and keyboard events for automated test creation</li>
                <li><strong>Test Execution:</strong> Execute recorded tests with precise timing and validation</li>
                <li><strong>Image Recognition:</strong> Advanced template matching and image comparison</li>
                <li><strong>GUI Interface:</strong> User-friendly control panel for test management</li>
                <li><strong>Document Generation:</strong> Automatic generation of test reports and documentation</li>
                <li><strong>Configuration Management:</strong> Flexible configuration system for different environments</li>
            </ul>
        </div>
        
        <h2>Module Documentation</h2>
        <div class="module-grid">
            <div class="module-card">
                <h3>📦 Main Package (src)</h3>
                <p>Core package containing all ATA_V3 functionality and main entry points.</p>
                <a href="src/index.html">View Documentation</a>
            </div>
            
            <div class="module-card">
                <h3>🔧 Utilities (src.utils)</h3>
                <p>Core utility functions including configuration management, image processing, event handling, and test data management.</p>
                <a href="src/utils/index.html">View Documentation</a>
            </div>
            
            <div class="module-card">
                <h3>🖥️ GUI Components (src.gui)</h3>
                <p>Graphical user interface components including the main control panel, dialogs, and event monitoring windows.</p>
                <a href="src/gui/index.html">View Documentation</a>
            </div>
            
            <div class="module-card">
                <h3>🧪 Test Framework (src.tests)</h3>
                <p>Test recording and execution functionality for creating and running automated tests.</p>
                <a href="src/tests/index.html">View Documentation</a>
            </div>
            
            <div class="module-card">
                <h3>📄 Documentation (src.Doc)</h3>
                <p>Document generation utilities for creating Word documents from test results and configuration.</p>
                <a href="src/Doc/index.html">View Documentation</a>
            </div>
        </div>
        
        <div class="info-section">
            <h2>Getting Started</h2>
            <p>To use the ATA_V3 framework:</p>
            <ol>
                <li>Run the main application: <code>python src/gui/control_panel.py</code></li>
                <li>Use the GUI to record new tests or execute existing ones</li>
                <li>Configure test parameters and image recognition settings</li>
                <li>Generate test reports and documentation as needed</li>
            </ol>
            
            <h3>Documentation Features:</h3>
            <ul>
                <li><strong>Google-Style Docstrings:</strong> All code is documented using Google-style docstrings</li>
                <li><strong>Type Annotations:</strong> Full type hint support for better code understanding</li>
                <li><strong>Source Code:</strong> View the actual source code alongside documentation</li>
                <li><strong>Interactive Navigation:</strong> Easy navigation between modules and functions</li>
                <li><strong>Search Functionality:</strong> Search across all documentation</li>
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by <a href="https://pdoc3.github.io/pdoc/" target="_blank">pdoc</a> on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>© {project_author} - {project_name} v{project_version}</p>
    </div>
</body>
</html>"""
    
    index_path = Path(output_dir) / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"Created custom index page: {index_path}")

def main():
    """Main function to generate documentation."""
    print("=" * 60)
    print(f"ATA_V3 Documentation Generator (Simplified)")
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Clean build artifacts
    clean_build_artifacts()
    
    # Step 2: Clean output directory
    clean_output_directory()
    
    # Step 3: Generate documentation
    if not generate_documentation():
        print("Documentation generation failed!")
        return 1
    
    # Step 4: Create custom index page
    create_index_page()
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("DOCUMENTATION GENERATION COMPLETED!")
    print("=" * 60)
    print(f"📁 Output Directory: {os.path.abspath(output_dir)}")
    print(f"🌐 Main Index: {os.path.abspath(output_dir)}/index.html")
    print(f"📦 Package Documented: src")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTo view the documentation:")
    print(f"1. Open: {os.path.abspath(output_dir)}/index.html")
    print("2. Or start a local server: python -m http.server 8000")
    print("3. Then visit: http://localhost:8000/docs/")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 