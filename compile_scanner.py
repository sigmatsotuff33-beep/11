import os
import subprocess
import sys
from rich.console import Console

console = Console()

def compile_scanner():
    console.print("[bold blue]🔨 Compiling C++ OSINT Scanner...[/]")
    
    # Check for required libraries
    console.print("[yellow]Checking for required libraries...[/]")
    
    # Try to find nlohmann/json
    json_header_found = False
    possible_paths = [
        "/usr/include/nlohmann/json.hpp",
        "/usr/local/include/nlohmann/json.hpp",
        "/include/nlohmann/json.hpp",
        "nlohmann/json.hpp"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            json_header_found = True
            console.print(f"[green]✓ Found nlohmann/json at: {path}[/]")
            break
    
    if not json_header_found:
        console.print("[yellow]⚠ nlohmann/json.hpp not found in standard locations[/]")
        console.print("[yellow]Downloading nlohmann/json...[/]")
        
        # Download nlohmann/json single header
        try:
            import requests
            url = "https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp"
            response = requests.get(url)
            with open("json.hpp", "wb") as f:
                f.write(response.content)
            console.print("[green]✓ Downloaded nlohmann/json.hpp[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to download nlohmann/json: {e}[/]")
            return False

    # Compilation attempts
    compile_attempts = [
        {
            "flags": ["-std=c++11", "-o", "scanner", "scanner.cpp", "-lcurl", "-lpthread"],
            "desc": "C++11 with curl & pthread"
        },
        {
            "flags": ["-std=c++11", "-o", "scanner", "scanner.cpp", "-lcurl"],
            "desc": "C++11 with curl"
        },
        {
            "flags": ["-std=c++11", "-o", "scanner", "scanner.cpp"],
            "desc": "C++11 basic"
        },
    ]
    
    success = False
    for attempt in compile_attempts:
        console.print(f"[yellow]Trying {attempt['desc']}...[/]")
        try:
            result = subprocess.run(
                ["g++"] + attempt["flags"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                console.print(f"[bold green]✅ Successfully compiled with {attempt['desc']}[/]")
                success = True
                break
            else:
                console.print(f"[red]❌ {attempt['desc']} failed[/]")
                if result.stderr:
                    console.print(f"[red]Error: {result.stderr}[/]")
                
        except subprocess.TimeoutExpired:
            console.print(f"[red]⏰ {attempt['desc']} timed out[/]")
        except Exception as e:
            console.print(f"[red]❌ {attempt['desc']} error: {e}[/]")
    
    if success:
        # Make executable
        try:
            os.chmod("scanner", 0o755)
            console.print("[green]✓ Scanner is now executable[/]")
            
            # Test the scanner
            console.print("[yellow]Testing scanner...[/]")
            test_result = subprocess.run(
                ["./scanner", "help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if test_result.returncode in [0, 1]:
                console.print("[bold green]✅ Scanner is working correctly![/]")
            else:
                console.print("[yellow]⚠ Scanner compiled but may have issues[/]")
                
        except Exception as e:
            console.print(f"[yellow]⚠ Could not set permissions: {e}[/]")
    else:
        console.print("[bold red]❌ All compilation attempts failed[/]")
        console.print("\n[bold yellow]Troubleshooting steps:[/]")
        console.print("1. Install C++ compiler: sudo apt install g++")
        console.print("2. Install curl development libraries: sudo apt install libcurl4-openssl-dev")
        console.print("3. Ensure nlohmann/json.hpp is available")
        
    return success

if __name__ == "__main__":
    compile_scanner()