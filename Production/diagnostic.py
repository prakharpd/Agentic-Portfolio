
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# CONFIGURATION

script_dir = os.path.dirname(os.path.abspath(__file__))
resume_dir = os.path.join(script_dir, "resume")
resume_pdf = os.path.join(resume_dir, "linkedin.pdf")
resume_summary = os.path.join(resume_dir, "summary.txt")
env_file = os.path.join(script_dir, ".env")

required_files = {
    "backend.py": os.path.join(script_dir, "backend.py"),
    "frontend.py": os.path.join(script_dir, "frontend.py"),
    "main.py": os.path.join(script_dir, "main.py"),
}

required_packages = {
    "python-dotenv": "dotenv",
    "gradio": "gradio",
    "pypdf": "pypdf",
    "sentence-transformers": "sentence_transformers",
    "numpy": "numpy",
    "nest-asyncio": "nest_asyncio",
    "openai": "openai",
    "requests": "requests",
}

# 
# COLOR CODES
# 

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


# 
# 1. FILE STRUCTURE CHECK
# 

def check_file_structure():
    """Check if all required files and directories exist"""
    print_header("1️⃣  FILE STRUCTURE CHECK")
    
    all_good = True
    
    # Check main script files
    print(f"{Colors.BOLD}Main Script Files:{Colors.END}")
    for filename, filepath in required_files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
            print_success(f"{filename} ({size} bytes, modified: {mod_time})")
        else:
            print_error(f"{filename} NOT FOUND at {filepath}")
            all_good = False
    
    # Check resume folder
    print(f"\n{Colors.BOLD}Resume Files:{Colors.END}")
    if os.path.exists(resume_dir):
        print_success(f"resume/ folder EXISTS")
        
        # Check PDF
        if os.path.exists(resume_pdf):
            size = os.path.getsize(resume_pdf) / 1024 / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(resume_pdf)).strftime("%Y-%m-%d %H:%M:%S")
            print_success(f"linkedin.pdf EXISTS ({size:.2f} MB, modified: {mod_time})")
        else:
            print_error(f"linkedin.pdf NOT FOUND")
            all_good = False
        
        # Check summary
        if os.path.exists(resume_summary):
            size = os.path.getsize(resume_summary) / 1024
            mod_time = datetime.fromtimestamp(os.path.getmtime(resume_summary)).strftime("%Y-%m-%d %H:%M:%S")
            print_success(f"summary.txt EXISTS ({size:.2f} KB, modified: {mod_time})")
        else:
            print_error(f"summary.txt NOT FOUND")
            all_good = False
    else:
        print_error(f"resume/ folder NOT FOUND at {resume_dir}")
        all_good = False
    
    # Check .env file
    print(f"\n{Colors.BOLD}Environment File:{Colors.END}")
    if os.path.exists(env_file):
        size = os.path.getsize(env_file)
        print_success(f".env file EXISTS ({size} bytes)")
    else:
        print_warning(f".env file NOT FOUND (optional, but recommended for notifications)")
    
    return all_good


# 
# 2. PYTHON DEPENDENCIES CHECK
# 

def check_dependencies():
    """Check if all required Python packages are installed"""
    print_header("2️⃣  PYTHON DEPENDENCIES CHECK")
    
    all_good = True
    installed = []
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            installed.append(package_name)
            print_success(f"{package_name}")
        except ImportError:
            missing.append(package_name)
            print_error(f"{package_name} NOT INSTALLED")
            all_good = False
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print_info(f"Installed: {len(installed)}/{len(required_packages)}")
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print(f"\n{Colors.BOLD}To install missing packages, run:{Colors.END}")
        print(f"pip install {' '.join(missing)}\n")
    
    return all_good


# 3. ENVIRONMENT VARIABLES CHECK
# 

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("3️⃣  ENVIRONMENT VARIABLES CHECK")
    
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    required_vars = {
        "PUSHOVER_USER": "Pushover user ID (for notifications)",
        "PUSHOVER_TOKEN": "Pushover API token (for notifications)",
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key (should be 'ollama' for local)",
        "OPENAI_BASE_URL": "OpenAI base URL (should be local Ollama)",
    }
    
    print(f"{Colors.BOLD}Required Variables:{Colors.END}")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show only first 10 chars for security
            masked = value[:10] + "***" if len(value) > 10 else value
            print_success(f"{var} = {masked} ({description})")
        else:
            print_warning(f"{var} NOT SET (optional - {description})")
    
    print(f"\n{Colors.BOLD}Optional Variables:{Colors.END}")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var} = {value}")
        else:
            print_info(f"{var} not set (will use default)")


# 
# 4. OLLAMA SERVICE CHECK
# 

def check_ollama_service():
    """Check if Ollama service is running"""
    print_header("4️⃣  OLLAMA SERVICE CHECK")
    
    ollama_url = "http://localhost:11434/api/tags"
    
    print_info("Checking if Ollama is running on http://localhost:11434...")
    
    try:
        import requests
        response = requests.get(ollama_url, timeout=5)
        
        if response.status_code == 200:
            print_success("✅ Ollama service is RUNNING")
            
            # Get available models
            try:
                data = response.json()
                models = data.get("models", [])
                
                if models:
                    print_success(f"Found {len(models)} model(s):")
                    for model in models:
                        name = model.get("name", "Unknown")
                        print(f"   • {name}")
                        
                        # Check for the specific model we need
                        if "gpt-oss" in name or "120b" in name:
                            print_success(f"   ✓ {name} is available (PERFECT for chatbot)")
                else:
                    print_warning("Ollama is running but no models found")
                    print(f"\n{Colors.BOLD}To add a model, run:{Colors.END}")
                    print("ollama pull gpt-oss:120b-cloud\n")
            except:
                print_warning("Could not parse Ollama models")
        else:
            print_error(f"Ollama returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error("❌ Cannot connect to Ollama at http://localhost:11434")
        print(f"\n{Colors.BOLD}To start Ollama, run:{Colors.END}")
        print("ollama serve\n")
    except Exception as e:
        print_error(f"Error checking Ollama: {str(e)}")


# 
# 5. BACKEND MODULE LOADING TEST
# 

def check_backend_loading():
    """Test if backend module can be loaded without errors"""
    print_header("5️⃣  BACKEND MODULE LOADING TEST")
    
    print_info("Attempting to import backend module...")
    
    try:
        # Add script directory to path
        sys.path.insert(0, script_dir)
        
        # Try to import backend
        import backend
        
        print_success("✅ Backend module loaded successfully")
        
        # Check if key functions exist
        print(f"\n{Colors.BOLD}Backend Components:{Colors.END}")
        
        if hasattr(backend, 'chat'):
            print_success("chat() function available")
        else:
            print_error("chat() function NOT found")
        
        if hasattr(backend, 'find_matching_sections'):
            print_success("find_matching_sections() function available")
        else:
            print_error("find_matching_sections() function NOT found")
        
        if hasattr(backend, 'all_document_chunks'):
            chunks_count = len(backend.all_document_chunks)
            print_success(f"RAG system loaded with {chunks_count} chunks")
        else:
            print_error("RAG system NOT found")
            
    except ImportError as e:
        print_error(f"Failed to import backend: {str(e)}")
    except Exception as e:
        print_error(f"Error loading backend: {str(e)}")


# 
# 6. SYSTEM HEALTH CHECK
# 

def check_system_health():
    """Overall system health check"""
    print_header("6️⃣  SYSTEM HEALTH CHECK")
    
    checks = {
        "Files": check_file_structure,
        "Dependencies": check_dependencies,
    }
    
    results = []
    
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            results.append((check_name, result))
        except:
            results.append((check_name, False))
    
    # Summary
    print_header("📊 FINAL HEALTH REPORT")
    
    all_passed = all(result for _, result in results)
    
    for check_name, result in results:
        if result:
            print_success(f"{check_name} - PASS")
        else:
            print_error(f"{check_name} - FAIL")
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL CHECKS PASSED! System is ready to go!{Colors.END}")
        print(f"\n{Colors.BOLD}Run the chatbot with:{Colors.END}")
        print("python main.py\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  Some checks failed. See details above.{Colors.END}\n")


# 
# MAIN ENTRY POINT
# 

def main():
    """Main diagnostic function"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PORTFOLIO CHATBOT - DIAGNOSTIC TOOL" + " "*19 + "║")
    print("║" + " "*22 + "(Run SEPARATELY from main.py)" + " "*16 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.END}")
    
    # Run all checks
    check_file_structure()
    check_dependencies()
    check_environment_variables()
    check_ollama_service()
    check_backend_loading()
    check_system_health()


if __name__ == "__main__":
    main()
