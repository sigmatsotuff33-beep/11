#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
import tempfile
import shutil
import platform
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.text import Text
import colorama
from colorama import Fore, Style

colorama.init()
console = Console()

class AutoOSINTSetup:
    def __init__(self):
        self.venv_path = Path("osint_venv")
        self.requirements = [
            "requests", "rich", "colorama", "aiohttp",

            "maigret", "sherlock-project", "holehe", "whatsmyname",
            "twint", "photon-py", "theharvester", "recon-ng",

            "beautifulsoup4", "selenium", "scrapy", "lxml",

            "pandas", "python-docx", "pypdf2", "pdfplumber",

            "python-whois", "sublist3r", "dnsrecon", "dnspython",
            "shodan", "waybackpy", "certgraph", "CloudEnum",
            "pyasn", "IP2Location", "scapy", "pyshark",

            "emailharvester", "instagram-scraper", "linkedin-scraper",

            "geopy", "folium", "gpxpy", "rtree", "osmnx",

            "exif", "hachoir3", "olefile", "jq", "speedtest-cli",
            "ffmpeg-python", "imagehash", "python-magic", "yt-dlp",

            "greynoise", "abuseipdb", "virustotal", "haveibeenpwned",
            "pygit2"
        ]
        
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 weThink OSINT AUTO-SETUP                     ║
║               Complete Environment Builder                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        console.print(f"[bold cyan]{banner}[/]")
        
    def check_system_requirements(self):
        """Check system requirements and dependencies"""
        console.print("[bold blue]🔍 Checking System Requirements...[/]")
        
        checks = {
            "Python Version": sys.version_info >= (3, 7),
            "Operating System": platform.system() in ["Linux", "Darwin", "Windows"],
            "pip available": self.check_pip(),
            "git available": self.check_git(),
            "curl available": self.check_curl(),
            "Compiler (g++)": self.check_compiler(),
        }
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Requirement", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="green")
        
        all_ok = True
        for req, status in checks.items():
            status_text = "✅ PASS" if status else "❌ FAIL"
            details = self.get_requirement_details(req, status)
            if not status:
                all_ok = False
            table.add_row(req, status_text, details)
        
        console.print(table)
        return all_ok
        
    def check_pip(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            return True
        except:
            return False
            
    def check_git(self):
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
            
    def check_curl(self):
        try:
            subprocess.run(["curl", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
            
    def check_compiler(self):
        try:
            subprocess.run(["g++", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
            
    def get_requirement_details(self, requirement, status):
        details = {
            "Python Version": f"Required: 3.7+, Current: {platform.python_version()}",
            "Operating System": f"Detected: {platform.system()} {platform.release()}",
            "pip available": "pip package manager" if status else "Install pip: python -m ensurepip",
            "git available": "Git version control" if status else "Install git: sudo apt install git",
            "curl available": "curl HTTP client" if status else "Install curl: sudo apt install curl",
            "Compiler (g++)": "C++ compiler" if status else "Install g++: sudo apt install g++",
        }
        return details.get(requirement, "")
        
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        console.print("[bold blue]📦 Installing System Dependencies...[/]")
        
        system = platform.system().lower()
        packages = []
        
        if system == "linux":
            if platform.linux_distribution()[0].lower() in ["ubuntu", "debian"]:
                packages = [
                    "g++", "libcurl4-openssl-dev", "libssl-dev", 
                    "python3-dev", "build-essential", "cmake",
                    "git", "curl", "wget", "nodejs", "npm",
                    "libxml2-dev", "libxslt1-dev", "zlib1g-dev",
                    "libjpeg-dev", "libffi-dev", "libmagic1"
                ]
        
        if packages:
            console.print(f"[yellow]Installing system packages: {', '.join(packages)}[/]")
            if Confirm.ask(f"Install {len(packages)} system packages?"):
                try:
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
                    console.print("[green]✅ System packages installed successfully[/]")
                except Exception as e:
                    console.print(f"[red]❌ Failed to install system packages: {e}[/]")
                    console.print("[yellow]You may need to install these manually[/]")
        
    def create_virtual_environment(self):
        """Create and activate virtual environment"""
        console.print("[bold blue]🐍 Creating Virtual Environment...[/]")
        
        if self.venv_path.exists():
            if Confirm.ask("Virtual environment already exists. Recreate?"):
                shutil.rmtree(self.venv_path)
            else:
                console.print("[yellow]Using existing virtual environment[/]")
                return True
                
        try:
            venv.create(self.venv_path, with_pip=True)
            console.print("[green]✅ Virtual environment created successfully[/]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create virtual environment: {e}[/]")
            return False
            
    def get_venv_pip(self):
        """Get the pip executable for the virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
            
    def get_venv_python(self):
        """Get the python executable for the virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
            
    def install_python_packages(self):
        """Install all Python packages in the virtual environment"""
        console.print("[bold blue]📚 Installing Python Packages...[/]")
        
        pip_exec = self.get_venv_pip()
        if not pip_exec.exists():
            console.print("[red]❌ Virtual environment pip not found[/]")
            return False
            
        # Update pip first
        console.print("[yellow]Upgrading pip...[/]")
        subprocess.run([str(pip_exec), "install", "--upgrade", "pip"], 
                      capture_output=True)
        
        # Install in batches to handle failures gracefully
        batch_size = 5
        batches = [self.requirements[i:i + batch_size] 
                  for i in range(0, len(self.requirements), batch_size)]
        
        successful_installs = []
        failed_installs = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            
            task = progress.add_task("Installing packages...", total=len(self.requirements))
            
            for batch in batches:
                for package in batch:
                    progress.update(task, description=f"Installing {package}...")
                    try:
                        result = subprocess.run(
                            [str(pip_exec), "install", package],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        if result.returncode == 0:
                            successful_installs.append(package)
                        else:
                            failed_installs.append(package)
                            console.print(f"[yellow]⚠️ Failed to install {package}[/]")
                    except subprocess.TimeoutExpired:
                        failed_installs.append(package)
                        console.print(f"[yellow]⏰ Timeout installing {package}[/]")
                    except Exception as e:
                        failed_installs.append(package)
                        console.print(f"[yellow]❌ Error installing {package}: {e}[/]")
                    
                    progress.update(task, advance=1)
        
        # Summary
        console.print(f"\n[bold green]✅ Successfully installed: {len(successful_installs)} packages[/]")
        if failed_installs:
            console.print(f"[bold yellow]⚠️ Failed to install: {len(failed_installs)} packages[/]")
            console.print(f"[yellow]Failed packages: {', '.join(failed_installs)}[/]")
            
        return len(successful_installs) > 0
        
    def download_nlohmann_json(self):
        """Download nlohmann/json for C++ scanner"""
        console.print("[bold blue]📥 Downloading nlohmann/json...[/]")
        
        try:
            import requests
            url = "https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp"
            response = requests.get(url)
            with open("json.hpp", "wb") as f:
                f.write(response.content)
            console.print("[green]✅ nlohmann/json downloaded successfully[/]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to download nlohmann/json: {e}[/]")
            console.print("[yellow]You may need to install it manually[/]")
            return False
            
    def compile_cpp_scanner(self):
        """Compile the C++ OSINT scanner"""
        console.print("[bold blue]🔨 Compiling C++ OSINT Scanner...[/]")
        
        if not os.path.exists("scanner.cpp"):
            console.print("[red]❌ scanner.cpp not found[/]")
            return False
            
        compile_attempts = [
            ["g++", "-std=c++11", "-I.", "-o", "scanner", "scanner.cpp", "-lcurl", "-lpthread"],
            ["g++", "-std=c++11", "-o", "scanner", "scanner.cpp", "-lcurl"],
            ["g++", "-std=c++11", "-o", "scanner", "scanner.cpp"],
        ]
        
        for attempt in compile_attempts:
            console.print(f"[yellow]Trying: {' '.join(attempt)}[/]")
            try:
                result = subprocess.run(attempt, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    os.chmod("scanner", 0o755)
                    console.print("[green]✅ C++ scanner compiled successfully[/]")
                    
                    # Test the scanner
                    test_result = subprocess.run(["./scanner", "help"], 
                                               capture_output=True, timeout=5)
                    if test_result.returncode in [0, 1]:
                        console.print("[green]✅ Scanner test passed[/]")
                    else:
                        console.print("[yellow]⚠️ Scanner compiled but test failed[/]")
                    
                    return True
                else:
                    console.print(f"[red]Compilation failed: {result.stderr}[/]")
            except Exception as e:
                console.print(f"[red]Compilation error: {e}[/]")
                
        console.print("[red]❌ All compilation attempts failed[/]")
        return False
        
    def create_advanced_scanner(self):
        """Create the advanced Python scanner if it doesn't exist"""
        if os.path.exists("advanced_scanner.py"):
            console.print("[green]✅ Advanced scanner already exists[/]")
            return True
            
        console.print("[bold blue]📝 Creating Advanced Python Scanner...[/]")
        
        advanced_scanner_code = '''import os
import sys
import requests
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

console = Console()

class AdvancedOSINTScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def run_maigret(self, username):
        """Run Maigret username search"""
        try:
            result = subprocess.run(
                ['maigret', username, '--timeout', '10', '--print-all', '--no-recursion'],
                capture_output=True, text=True, timeout=120
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            return f"Maigret error: {e}"

    def run_sherlock(self, username):
        """Run Sherlock username search"""
        try:
            result = subprocess.run(
                ['sherlock', username, '--timeout', '10', '--print-found'],
                capture_output=True, text=True, timeout=120
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            return f"Sherlock error: {e}"

    def run_holehe(self, email):
        """Run Holehe for email checking"""
        if '@' not in email:
            return ""
        try:
            result = subprocess.run(
                ['holehe', email, '--only-used'],
                capture_output=True, text=True, timeout=60
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            return f"Holehe error: {e}"

    def search_username(self, username):
        """Main search function"""
        with Progress() as progress:
            task = progress.add_task("Running advanced OSINT tools...", total=3)
            
            maigret_output = self.run_maigret(username)
            progress.update(task, advance=1)
            
            sherlock_output = self.run_sherlock(username)
            progress.update(task, advance=1)
            
            holehe_output = self.run_holehe(username)
            progress.update(task, advance=1)
        
        # Display results
        console.print(f"\\\\n[bold cyan]Advanced OSINT Results for: {username}[/]")
        console.print("=" * 80)
        
        if maigret_output:
            console.print(Panel(maigret_output, title="[green]Maigret Results[/]", border_style="green"))
        
        if sherlock_output:
            console.print(Panel(sherlock_output, title="[blue]Sherlock Results[/]", border_style="blue"))
        
        if '@' in username and holehe_output:
            console.print(Panel(holehe_output, title="[red]Email Breach Check[/]", border_style="red"))

def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
        scanner = AdvancedOSINTScanner()
        scanner.search_username(username)
    else:
        console.print("Usage: python advanced_scanner.py <username>")

if __name__ == "__main__":
    main()
'''
        
        try:
            with open("advanced_scanner.py", "w") as f:
                f.write(advanced_scanner_code)
            console.print("[green]✅ Advanced scanner created successfully[/]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create advanced scanner: {e}[/]")
            return False
            
    def create_activation_script(self):
        """Create activation script for the virtual environment"""
        console.print("[bold blue]📜 Creating Activation Script...[/]")
        
        if platform.system() == "Windows":
            script_content = f'''@echo off
echo Activating weThink OSINT Environment...
"{self.venv_path / 'Scripts' / 'activate.bat'}"
echo Environment activated! Run: python terminal.py
cmd /k
'''
            script_name = "activate_osint.bat"
        else:
            script_content = f'''#!/bin/bash
echo "Activating weThink OSINT Environment..."
source "{self.venv_path / 'bin' / 'activate'}"
echo "Environment activated! Run: python terminal.py"
exec $SHELL
'''
            script_name = "activate_osint.sh"
            # Make executable
            os.chmod(script_name, 0o755)
            
        try:
            with open(script_name, "w") as f:
                f.write(script_content)
            console.print(f"[green]✅ Activation script created: {script_name}[/]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to create activation script: {e}[/]")
            return False
            
    def run_tests(self):
        """Run basic tests to verify installation"""
        console.print("[bold blue]🧪 Running Tests...[/]")
        
        tests_passed = 0
        total_tests = 0
        
        # Test Python imports
        python_exec = self.get_venv_python()
        test_script = """
import sys
try:
    import requests, rich, colorama, maigret, sherlock, holehe
    print("SUCCESS: All core imports work")
    sys.exit(0)
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)
"""
        
        try:
            result = subprocess.run([str(python_exec), "-c", test_script], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                console.print("[green]✅ Python imports test passed[/]")
                tests_passed += 1
            else:
                console.print(f"[red]❌ Python imports test failed: {result.stdout}[/]")
            total_tests += 1
        except Exception as e:
            console.print(f"[red]❌ Python imports test error: {e}[/]")
            total_tests += 1
            
        # Test C++ scanner
        if os.path.exists("./scanner"):
            try:
                result = subprocess.run(["./scanner", "help"], 
                                      capture_output=True, timeout=10)
                if result.returncode in [0, 1]:
                    console.print("[green]✅ C++ scanner test passed[/]")
                    tests_passed += 1
                else:
                    console.print("[red]❌ C++ scanner test failed[/]")
                total_tests += 1
            except Exception as e:
                console.print(f"[red]❌ C++ scanner test error: {e}[/]")
                total_tests += 1
                
        console.print(f"[bold green]Tests passed: {tests_passed}/{total_tests}[/]")
        return tests_passed == total_tests
        
    def show_final_instructions(self):
        """Show final instructions and troubleshooting tips"""
        console.print(Panel.fit(
            "[bold green]🚀 Setup Complete![/]\\n\\n"
            "[bold white]Next Steps:[/]\\n"
            f"1. Activate environment: [cyan]source {self.venv_path}/bin/activate[/]\\n"
            "2. Run the terminal: [cyan]python terminal.py[/]\\n"
            "3. Or use the activation script: [cyan]./activate_osint.sh[/]\\n\\n"
            
            "[bold white]Available Commands:[/]\\n"
            "[cyan]adv username[/] - Advanced Python OSINT scan\\n"
            "[cyan]fscn domain.com[/] - Full domain reconnaissance\\n"
            "[cyan]iplc 8.8.8.8[/] - IP geolocation lookup\\n\\n"
            
            "[bold yellow]Troubleshooting Tips:[/]\\n"
            "• If tools fail, try: [cyan]pip install --upgrade package_name[/]\\n"
            "• For C++ issues: [cyan]sudo apt install g++ libcurl4-openssl-dev[/]\\n"
            "• Reset environment: [cyan]rm -rf osint_venv && python auto.py[/]",
            title="[bold blue]Getting Started[/]",
            border_style="green"
        ))
        
    def run(self):
        """Main setup process"""
        self.print_banner()
        
        console.print("[bold yellow]This will install and configure the complete weThink OSINT environment.[/]")
        console.print("[yellow]It may take 10-30 minutes depending on your system and internet connection.[/]")
        
        if not Confirm.ask("\\nContinue with setup?"):
            console.print("[yellow]Setup cancelled.[/]")
            return
            
        # Step 1: System checks
        if not self.check_system_requirements():
            console.print("[red]❌ System requirements not met. Please fix the issues above.[/]")
            if Confirm.ask("Try to install system dependencies automatically?"):
                self.install_system_dependencies()
            else:
                return
                
        # Step 2: Virtual environment
        if not self.create_virtual_environment():
            return
            
        # Step 3: Python packages
        if not self.install_python_packages():
            console.print("[yellow]⚠️ Some packages failed to install, but continuing...[/]")
            
        # Step 4: C++ dependencies
        self.download_nlohmann_json()
        
        # Step 5: Compile C++ scanner
        self.compile_cpp_scanner()
        
        # Step 6: Create advanced scanner
        self.create_advanced_scanner()
        
        # Step 7: Create activation script
        self.create_activation_script()
        
        # Step 8: Run tests
        self.run_tests()
        
        # Final instructions
        self.show_final_instructions()

def main():
    setup = AutoOSINTSetup()
    setup.run()

if __name__ == "__main__":
    main()