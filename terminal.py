import os
import time
import sys
import subprocess
import threading
import json
import platform
from pathlib import Path
from datetime import datetime

import colorama
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

colorama.init()
console = Console()

# Global results storage
scan_results = {}
current_session = {}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  weThink OSINT FRAMEWORK                     ║
║                 Advanced Reconnaissance Tool                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    console.print(f"[bold cyan]{banner}[/]")
    
    # System status
    system_info = f"""
[bold white]System Status:[/] [green]OPERATIONAL[/] | Scanner: [green]READY[/] | Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
[italic yellow]Platform: {platform.system()} {platform.release()} | Python: {platform.python_version()}[/]
"""
    console.print(system_info)

def create_results_directory():
    """Create directory for saving scan results"""
    results_dir = Path("osint_results")
    results_dir.mkdir(exist_ok=True)
    return results_dir

def save_scan_results(command, target, results):
    """Save scan results to file"""
    try:
        results_dir = create_results_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"{command}_{target}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"weThink OSINT Scan Results\n")
            f.write(f"Command: {command} {target}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(results)
        
        return filename
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save results: {e}[/]")
        return None

def run_scanner_command(command, target, timeout=120):
    """Run C++ scanner command"""
    try:
        if not os.path.exists("./scanner"):
            return "[bold red]C++ Scanner binary not found.[/]"
        
        console.print(f"[bold yellow][C++ Scanner] Executing: {command} {target}[/]")
        
        with console.status(f"[bold green]Running {command} scan...", spinner="dots") as status:
            result = subprocess.run(
                ["./scanner", command, target],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        
        output = result.stdout.strip()
        
        if result.returncode == 0:
            filename = save_scan_results(f"cpp_{command}", target, output)
            if filename:
                console.print(f"[green]Results saved to: {filename}[/]")
            
            session_key = f"cpp_{command}_{target}"
            scan_results[session_key] = {
                'timestamp': datetime.now(),
                'command': command,
                'target': target,
                'results': output,
                'saved_to': str(filename) if filename else None,
                'type': 'cpp'
            }
            
            return output
        else:
            error_msg = f"[bold red]C++ Scanner Error (Code {result.returncode}):[/]\n{result.stderr}"
            return error_msg
            
    except subprocess.TimeoutExpired:
        return "[bold red]C++ Scan timeout: Operation took too long[/]"
    except FileNotFoundError:
        return "[bold red]C++ Scanner binary not found.[/]"
    except Exception as e:
        return f"[bold red]C++ Scanner execution error: {e}[/]"

def run_advanced_scanner(username, timeout=180):
    """Run the Python advanced scanner"""
    try:
        if not os.path.exists("advanced_scanner.py"):
            return "[bold red]Advanced Python scanner not found.[/]"
        
        console.print(f"[bold yellow][Python Scanner] Executing advanced scan for: {username}[/]")
        
        with console.status(f"[bold green]Running advanced OSINT scan...", spinner="dots") as status:
            result = subprocess.run(
                [sys.executable, "advanced_scanner.py", username],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        
        output = result.stdout.strip()
        
        if result.returncode == 0:
            filename = save_scan_results("advanced_python", username, output)
            if filename:
                console.print(f"[green]Advanced results saved to: {filename}[/]")
            
            session_key = f"advanced_python_{username}"
            scan_results[session_key] = {
                'timestamp': datetime.now(),
                'command': 'advanced',
                'target': username,
                'results': output,
                'saved_to': str(filename) if filename else None,
                'type': 'python'
            }
            
            return output
        else:
            error_msg = f"[bold red]Advanced Scanner Error (Code {result.returncode}):[/]\n{result.stderr}"
            return error_msg
            
    except subprocess.TimeoutExpired:
        return "[bold red]Advanced scan timeout: Operation took too long[/]"
    except FileNotFoundError:
        return "[bold red]Advanced scanner not found.[/]"
    except Exception as e:
        return f"[bold red]Advanced scanner execution error: {e}[/]"

def run_scanner_command_async(command, target):
    """Run scanner command asynchronously"""
    def run_and_display():
        result = run_scanner_command(command, target)
        
        console.print(f"\n[bold cyan]C++ Scanner Results for {command} {target}:[/]")
        
        if "error" in result.lower() or "not found" in result:
            console.print(Panel(result, title=f"[red]C++ Scan Failed: {command}[/]", border_style="red"))
        else:
            console.print(Panel(result, title=f"[green]C++ Scan Complete: {command}[/]", border_style="green"))
    
    thread = threading.Thread(target=run_and_display)
    thread.daemon = True
    thread.start()
    
    console.print(f"[yellow]Started C++ async scan: {command} {target}[/]")

def run_advanced_scanner_async(username):
    """Run advanced Python scanner asynchronously"""
    def run_and_display():
        result = run_advanced_scanner(username)
        
        console.print(f"\n[bold cyan]Python Advanced Scanner Results for {username}:[/]")
        
        if "error" in result.lower() or "not found" in result:
            console.print(Panel(result, title=f"[red]Advanced Scan Failed[/]", border_style="red"))
        else:
            console.print(Panel(result, title=f"[green]Advanced Scan Complete[/]", border_style="green"))
    
    thread = threading.Thread(target=run_and_display)
    thread.daemon = True
    thread.start()
    
    console.print(f"[yellow]Started Python advanced async scan: {username}[/]")

def run_comprehensive_scan(target_type, target):
    """Run multiple scans based on target type"""
    scans = []
    
    if target_type == "domain":
        scans = [
            ("dLkp", target, "DNS Lookup"),
            ("wHis", target, "WHOIS Information"),
            ("sSll", target, "SSL Certificates"),
            ("wBck", target, "Wayback Archive"),
        ]
    elif target_type == "username":
        # Use Python advanced scanner for usernames
        console.print(f"[bold blue]Starting comprehensive username scan: {target}[/]")
        run_advanced_scanner_async(target)
        return
        
    elif target_type == "ip":
        scans = [
            ("iPlc", target, "IP Geolocation"),
        ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        
        task = progress.add_task(f"Running comprehensive {target_type} scan...", total=len(scans))
        
        for command, target_value, description in scans:
            progress.update(task, description=f"Running {description}...")
            result = run_scanner_command(command, target_value)
            
            if "error" not in result.lower() and "not found" not in result:
                progress.console.print(f"[green]Success: {description}[/]")
            else:
                progress.console.print(f"[red]Failed: {description}[/]")
            
            progress.update(task, advance=1)
            time.sleep(1)

def show_session_summary():
    """Display current session scan results"""
    if not scan_results:
        console.print("[yellow]No scan results in current session.[/]")
        return
    
    table = Table(title="Current Session Results", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Command", style="white")
    table.add_column("Target", style="green")
    table.add_column("Timestamp", style="yellow")
    table.add_column("Status", style="white")
    
    for key, result in scan_results.items():
        scanner_type = "C++" if result['type'] == 'cpp' else "Python"
        status = "SUCCESS" if "error" not in result['results'].lower() else "FAILED"
        table.add_row(
            scanner_type,
            result['command'],
            result['target'],
            result['timestamp'].strftime("%H:%M:%S"),
            status
        )
    
    console.print(table)

def export_session_results():
    """Export all session results to a single file"""
    if not scan_results:
        console.print("[yellow]No results to export.[/]")
        return
    
    try:
        results_dir = create_results_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = results_dir / f"session_export_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# weThink OSINT Session Export\n\n")
            f.write(f"**Export Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Scans:** {len(scan_results)}\n\n")
            
            for key, result in scan_results.items():
                scanner_type = "C++" if result['type'] == 'cpp' else "Python Advanced"
                f.write(f"## {scanner_type}: {result['command']} {result['target']}\n")
                f.write(f"**Time:** {result['timestamp'].strftime('%H:%M:%S')}\n")
                f.write("```\n")
                f.write(result['results'])
                f.write("\n```\n\n")
        
        console.print(f"[bold green]Session exported to: {filename}[/]")
        return filename
    except Exception as e:
        console.print(f"[red]Error exporting session: {e}[/]")
        return None

def show_help():
    """Enhanced help with both C++ and Python scanners"""
    help_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    help_table.add_column("Command", style="yellow", width=12)
    help_table.add_column("Description", style="white")
    help_table.add_column("Type", style="green", width=8)
    help_table.add_column("Usage", style="blue")
    
    commands = [
        # Python Advanced Scanner
        ("adv", "Advanced Python OSINT scan", "Python", "adv <username>"),
        ("wtnk", "Username search (Python)", "Python", "wtnk <username>"),
        
        # C++ Scanner Commands
        ("ghub", "GitHub user information", "C++", "ghub <username>"),
        ("rddt", "Reddit user information", "C++", "rddt <username>"),
        ("hnws", "Hacker News user information", "C++", "hnws <username>"),
        ("sovf", "Stack Overflow user information", "C++", "sovf <userid>"),
        
        # Domain & Network Intelligence
        ("dlkp", "DNS lookup and records", "C++", "dlkp <domain>"),
        ("whis", "WHOIS domain information", "C++", "whis <domain>"),
        ("ssll", "SSL certificate information", "C++", "ssll <domain>"),
        ("fscn", "Full comprehensive domain scan", "C++", "fscn <domain>"),
        ("wbck", "Wayback Machine archived URLs", "C++", "wbck <domain>"),
        
        # Digital Footprint Analysis
        ("iplc", "IP address geolocation", "C++", "iplc <ip_address>"),
        ("embp", "Email breach check", "C++", "embp <email>"),
        ("btcn", "Bitcoin address information", "C++", "btcn <address>"),
        
        # Session Management
        ("session", "Show current session results", "Both", "session"),
        ("export", "Export session results", "Both", "export"),
        ("clear", "Clear terminal", "Both", "clear"),
        ("help", "Show this help message", "Both", "help"),
        ("exit", "Exit the terminal", "Both", "exit"),
    ]
    
    for cmd, desc, scan_type, usage in commands:
        help_table.add_row(cmd, desc, scan_type, usage)
    
    console.print(Panel(help_table, title="[bold green]weThink OSINT Command Reference[/]"))
    
    # Quick examples
    examples = """
[bold yellow]Quick Examples:[/]
  [cyan]adv john_doe[/]           - Advanced Python OSINT scan
  [cyan]wtnk john_doe[/]          - Username search (Python)
  [cyan]fscn example.com[/]       - Full domain reconnaissance (C++)  
  [cyan]iplc 8.8.8.8[/]           - IP geolocation lookup (C++)
  [cyan]session[/]                - View current scan results
  [cyan]export[/]                 - Save all results to file
"""
    console.print(Panel(examples, title="[bold blue]Usage Examples[/]", border_style="blue"))

def process_command(user_input):
    """Enhanced command processor with both scanners"""
    parts = user_input.strip().split()
    if not parts:
        return None
    
    command = parts[0].lower()
    
    # Session management commands
    if command == "exit":
        if scan_results and Confirm.ask("\nSave session results before exiting?"):
            export_session_results()
        return "exit"
    
    elif command == "help":
        show_help()
        return None
    
    elif command == "clear":
        clear_screen()
        display_banner()
        return None
    
    elif command == "session":
        show_session_summary()
        return None
        
    elif command == "export":
        export_session_results()
        return None
    
    # Scan commands requiring target
    elif len(parts) >= 2:
        target = parts[1]
        
        # Python Advanced Scanner commands
        if command in ["adv", "wtnk"]:
            console.print(f"[bold blue]Starting Python advanced scan: {target}[/]")
            run_advanced_scanner_async(target)
            
        # C++ Scanner commands
        elif command in ["fscn"]:
            console.print(f"[bold blue]Starting comprehensive domain scan: {target}[/]")
            threading.Thread(target=run_comprehensive_scan, args=("domain", target)).start()
            
        elif command in ["ascn"]:
            console.print(f"[bold blue]Starting comprehensive username scan: {target}[/]")
            threading.Thread(target=run_comprehensive_scan, args=("username", target)).start()
            
        # Individual C++ scan commands
        elif command in ["dlkp", "wbck", "ghub", "rddt", "iplc", 
                        "whis", "ssll", "embp", "btcn", "hnws", "sovf"]:
            threading.Thread(target=run_scanner_command_async, args=(command, target)).start()
            
        else:
            console.print(f"[bold red]Unknown command: {command}[/]")
            console.print(f"[yellow]Type 'help' for available commands[/]")
    
    else:
        console.print(f"[bold red]Invalid command format[/]")
        console.print(f"[yellow]Usage: <command> <target>[/]")
        console.print(f"[yellow]Type 'help' for available commands[/]")
    
    return None

def check_scanners():
    """Check availability of both scanners"""
    console.print("[bold blue]Checking scanner availability...[/]")
    
    scanners_available = {
        "C++ Scanner": os.path.exists("./scanner"),
        "Python Advanced Scanner": os.path.exists("advanced_scanner.py")
    }
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Scanner", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="green")
    
    for scanner, available in scanners_available.items():
        status = "✅ AVAILABLE" if available else "❌ NOT FOUND"
        details = "Ready to use" if available else "File not found"
        table.add_row(scanner, status, details)
    
    console.print(table)
    
    return any(scanners_available.values())

def main():
    """Main terminal interface"""
    clear_screen()
    display_banner()
    
    # Check scanner availability
    if not check_scanners():
        console.print("[bold red]No scanners found! Please ensure at least one scanner is available.[/]")
        console.print("[yellow]Required files: './scanner' (C++) or 'advanced_scanner.py' (Python)[/]")
        return
    
    console.print(f"\n[bold green]weThink OSINT Terminal Ready![/]")
    console.print("[italic cyan]Type 'help' for commands, 'exit' to quit[/]\n")
    
    # Main command loop
    try:
        while True:
            try:
                prompt_text = Text("weThink > ", style="bold green")
                user_input = Prompt.ask(prompt_text)
                
                result = process_command(user_input)
                if result == "exit":
                    console.print("[bold green]Session ended. Goodbye![/]")
                    break
                    
            except KeyboardInterrupt:
                if Confirm.ask("\nReally exit?"):
                    break
                else:
                    continue
            except EOFError:
                break
                
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/]")
    
    finally:
        # Cleanup if needed
        if scan_results:
            console.print(f"[yellow]Session summary: {len(scan_results)} scans performed[/]")

if __name__ == "__main__":
    main()