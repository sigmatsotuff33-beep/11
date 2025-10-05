import os
import time
import sys
import platform
import colorama
import subprocess
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.align import Align

colorama.init()
console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def system_check():
    """Check system requirements"""
    console.print("[bold blue]🔍 Performing System Check...[/]")
    
    checks = {
        "Python Version": sys.version_info >= (3, 7),
        "Operating System": platform.system() in ["Linux", "Darwin", "Windows"],
        "Compiler Available": check_compiler(),
        "Internet Connection": check_internet(),
    }
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    for check, status in checks.items():
        status_text = "✅ PASS" if status else "❌ FAIL"
        details = get_check_details(check, status)
        table.add_row(check, status_text, details)
    
    console.print(table)
    return all(checks.values())

def check_compiler():
    """Check if C++ compiler is available"""
    try:
        subprocess.run(["g++", "--version"], capture_output=True, timeout=5)
        return True
    except:
        return False

def check_internet():
    """Check internet connectivity"""
    try:
        subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, timeout=5)
        return True
    except:
        return False

def get_check_details(check, status):
    """Get detailed information for each check"""
    details = {
        "Python Version": f"Required: 3.7+, Current: {platform.python_version()}",
        "Operating System": f"Detected: {platform.system()} {platform.release()}",
        "Compiler Available": "GCC/G++ compiler found" if status else "Install g++ compiler",
        "Internet Connection": "Online" if status else "No internet connection",
    }
    return details.get(check, "")

def flash_animate(text, flash_frames=5, flash_delay=0.01):
    """Enhanced flash animation with colors"""
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.WHITE]
    
    for i in range(1, flash_frames + 1):
        color = colors[i % len(colors)]
        cutoff = int(len(text) * (i / flash_frames))
        animated_text = color + text[:cutoff] + Style.RESET_ALL
        sys.stdout.write("\r" + animated_text)
        sys.stdout.flush()
        time.sleep(flash_delay)
    
    sys.stdout.write("\r" + Fore.GREEN + text + Style.RESET_ALL + "\n")
    sys.stdout.flush()

def loading_animation():
    """Enhanced loading animation with system status"""
    spinner_frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta", "white"]
    wave_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"]
    
    start_time = time.time()
    duration = 5
    
    # System status simulation
    modules = [
        "Core Security", "Network Stack", "OSINT Engine", 
        "Data Processor", "Report Generator", "Terminal UI"
    ]
    module_status = {module: False for module in modules}
    
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            progress = elapsed / duration
            
            # Update module status based on progress
            modules_to_activate = int(len(modules) * progress)
            for i, module in enumerate(modules):
                module_status[module] = (i < modules_to_activate)
            
            # Calculate indices for animations
            spinner_idx = int(elapsed * 8) % len(spinner_frames)
            color_idx = int(elapsed * 3) % len(colors)
            wave_idx = int(elapsed * 10) % len(wave_chars)
            
            current_color = colors[color_idx]
            next_color = colors[(color_idx + 1) % len(colors)]
            
            # Create wave progress bar
            wave_length = 50
            filled = int(wave_length * progress)
            wave_bar = f"[{current_color}]" + (wave_chars[wave_idx] * filled) + "[/]" + (" " * (wave_length - filled))
            
            # Create module status display
            module_status_text = ""
            for module in modules:
                status_icon = "✅" if module_status[module] else "⏳"
                module_color = "green" if module_status[module] else "yellow"
                module_status_text += f"[{module_color}]{status_icon} {module}[/]\n"
            
            content = f"""
[{current_color}]{spinner_frames[spinner_idx]}[/] [bold {next_color}]weThink OSINT Framework[/] [{current_color}]{spinner_frames[spinner_idx]}[/]

[bold white]Initializing Security Platform...[/]

[italic green]• Loading Core Modules
• Starting OSINT Services  
• Compiling C++ Scanner
• Preparing Command Interface

[bold yellow]System Modules:[/]
{module_status_text}
[bold yellow]Progress:[/]
{wave_bar}
[bold cyan]{int(progress * 100)}% Complete[/]

[italic white]VHS 2025 | Doc Iota Aegis Production[/]
"""
            
            clear_screen()
            console.print(
                Panel(
                    content,
                    title=f"[bold {current_color}]weThink Boot Sequence[/]",
                    subtitle=f"[green]Time: {int(elapsed)}s | CPU: {platform.processor()}[/]"
                )
            )
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        console.print(f"\n{Fore.RED}Boot sequence interrupted{Style.RESET_ALL}")
        return False
    
    return True

def compile_scanner():
    """Enhanced compilation with better error handling"""
    console.print("[bold blue]🔨 Compiling C++ OSINT Scanner...[/]")
    
    # Check if source file exists
    if not os.path.exists("scanner.cpp"):
        console.print("[bold red]❌ scanner.cpp not found![/]")
        console.print("[yellow]Please ensure scanner.cpp is in the current directory.[/]")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Compiling...", total=100)
        
        # Try different compilation strategies
        compile_attempts = [
            {
                "flags": ["-std=c++17", "-I.", "-o", "scanner", "scanner.cpp", "-lcurl", "-lpthread"],
                "desc": "C++17 with curl & pthread"
            },
            {
                "flags": ["-std=c++17", "-o", "scanner", "scanner.cpp", "-lcurl"],
                "desc": "C++17 with curl"
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
        compilation_output = ""
        
        for attempt in compile_attempts:
            progress.update(task, description=f"Trying {attempt['desc']}...")
            time.sleep(0.5)
            
            try:
                result = subprocess.run(
                    ["g++"] + attempt["flags"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    progress.update(task, completed=100)
                    console.print(f"[bold green]✅ Successfully compiled with {attempt['desc']}[/]")
                    success = True
                    break
                else:
                    compilation_output = result.stderr
                    console.print(f"[yellow]⚠️ {attempt['desc']} failed[/]")
                    progress.update(task, description="Trying next method...")
                    time.sleep(0.5)
                    
            except subprocess.TimeoutExpired:
                console.print(f"[red]⏰ {attempt['desc']} timed out[/]")
            except Exception as e:
                console.print(f"[red]❌ {attempt['desc']} error: {e}[/]")
        
        if not success:
            console.print("[bold red]❌ All compilation attempts failed[/]")
            if compilation_output:
                console.print(f"[red]Compilation error:\n{compilation_output}[/]")
            return False
    
    # Make executable and verify
    try:
        os.chmod("scanner", 0o755)
        # Verify the binary works
        result = subprocess.run(["./scanner", "--help"], capture_output=True, timeout=5)
        if result.returncode in [0, 1]:  # Many tools return 1 for help
            console.print("[bold green]✅ Scanner verified and ready[/]")
        else:
            console.print("[yellow]⚠️ Scanner compiled but may have issues[/]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Scanner permissions: {e}[/]")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    console.print("[bold blue]📦 Installing Python Dependencies...[/]")
    
    dependencies = [
        "requests",
        "colorama",
        "rich"
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Installing...", total=len(dependencies))
        
        for dep in dependencies:
            progress.update(task, description=f"Installing {dep}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, check=True)
                progress.update(task, advance=1)
            except subprocess.CalledProcessError:
                console.print(f"[yellow]⚠️ Failed to install {dep}[/]")
    
    console.print("[bold green]✅ Dependencies installed[/]")

def show_welcome():
    """Display welcome message"""
    welcome_text = """
[bold cyan]╔══════════════════════════════════════════════╗
║                                                           ║
║            weThink OSINT Framework v2.0                  ║
║               Advanced Reconnaissance                    ║
║                                                          ║
╚══════════════════════════════════════════════╝[/bold cyan]

[bold white]Welcome to the next generation of open-source intelligence gathering.[/]

[italic green]• Multi-platform username reconnaissance
• Domain and network intelligence  
• Social media analysis
• Automated reporting
• Real-time data processing[/]

[bold yellow]Ready to begin your investigation...[/]
"""
    
    console.print(Panel(
        Align.center(welcome_text),
        title="[bold red]SECURE BOOT COMPLETE[/]",
        subtitle="[green]Status: OPERATIONAL[/]"
    ))

def main():
    """Main boot sequence"""
    clear_screen()
    
    # Initial system check
    if not system_check():
        console.print("[bold red]❌ System check failed. Please resolve issues above.[/]")
        return
    
    # Start boot sequence
    print(Fore.RED + "[+weThink] Automated Setup Starting...")
    time.sleep(1)
    
    flash_animate("Initializing weThink OSINT Security Platform", flash_frames=8, flash_delay=0.03)
    time.sleep(0.5)
    
    # Install dependencies
    install_dependencies()
    time.sleep(1)
    
    # Run loading animation
    if not loading_animation():
        return
    
    # Compile scanner
    if not compile_scanner():
        console.print("[bold red]❌ Setup failed. Please check compiler installation.[/]")
        console.print("[yellow]💡 Try: sudo apt install g++ libcurl4-openssl-dev[/]")
        return
    
    # Final success screen
    clear_screen()
    show_welcome()
    
    # Countdown to launch
    console.print("\n[bold yellow]🚀 Launching terminal in:[/]", end="")
    for i in range(3, 0, -1):
        console.print(f" [red]{i}[/]", end="")
        sys.stdout.flush()
        time.sleep(1)
    console.print()
    
    # Launch terminal
    clear_screen()
    try:
        # Import and run terminal
        from terminal import main as terminal_main
        terminal_main()
    except ImportError as e:
        console.print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        console.print("[yellow]💡 Make sure terminal.py exists in the same directory.[/]")
    except Exception as e:
        console.print(f"\n{Fore.RED}❌ Error launching terminal: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()