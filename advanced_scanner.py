import requests
import sys
import json
import subprocess
import os
import re
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.markdown import Markdown

def search_username(username):
    console = Console()
    results = {
        'usernames': [],
        'images': [],
        'links': [],
        'emails': [],
        'profiles': []
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Initializing advanced OSINT scan...", total=100)

        # Enhanced platform configurations
        platforms = {
            'GitHub': {
                'url': f'https://api.github.com/users/{username}',
                'type': 'json',
                'parser': lambda data: {
                    'username': f"GitHub: {data.get('name', username)} ({data.get('login', username)})",
                    'image': data.get('avatar_url', ''),
                    'links': [data.get('blog')] if data.get('blog') else [],
                    'profile': f"https://github.com/{username}"
                }
            },
            'Reddit': {
                'url': f'https://www.reddit.com/user/{username}/about.json',
                'type': 'json',
                'headers': {'User-Agent': 'OSINT-Tool/1.0'},
                'parser': lambda data: {
                    'username': f"Reddit: {data.get('data', {}).get('subreddit', {}).get('title', username)}",
                    'image': data.get('data', {}).get('icon_img', ''),
                    'links': [],
                    'profile': f"https://reddit.com/user/{username}"
                }
            },
            'Keybase': {
                'url': f'https://keybase.io/_/api/1.0/user/lookup.json?usernames={username}',
                'type': 'json',
                'parser': lambda data: {
                    'username': f"Keybase: {username}",
                    'image': data.get('them', [{}])[0].get('pictures', {}).get('primary', {}).get('url', ''),
                    'links': [],
                    'profile': f"https://keybase.io/{username}"
                }
            },
            'GitLab': {
                'url': f'https://gitlab.com/api/v4/users?username={username}',
                'type': 'json',
                'parser': lambda data: {
                    'username': f"GitLab: {data[0].get('name', username)}" if data else '',
                    'image': data[0].get('avatar_url', '') if data else '',
                    'links': [],
                    'profile': f"https://gitlab.com/{username}"
                }
            }
        }

        # Check platforms
        platform_count = len(platforms)
        progress_per_platform = 20 / platform_count if platform_count > 0 else 0

        for name, info in platforms.items():
            progress.update(task, description=f"Checking {name}...")
            try:
                headers = info.get('headers', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                r = requests.get(info['url'], headers=headers, timeout=10)
                
                if r.status_code == 200:
                    if info['type'] == 'json':
                        data = r.json()
                        parsed = info['parser'](data)
                        if parsed['username']:
                            results['usernames'].append(parsed['username'])
                            results['profiles'].append({
                                'platform': name,
                                'url': parsed.get('profile', ''),
                                'username': parsed['username']
                            })
                        if parsed['image']:
                            results['images'].append(parsed['image'])
                        results['links'].extend(parsed['links'])
                    
            except Exception as e:
                console.print(f"[red]Error checking {name}: {str(e)}[/red]")
            
            progress.update(task, advance=progress_per_platform)

        # Run external tools with better error handling
        tools = [
            ('Maigret', 'maigret', [username, '--timeout', '10', '--no-recursion']),
            ('Sherlock', 'sherlock', [username, '--timeout', '10', '--print-found']),
        ]

        if '@' in username:
            tools.append(('Holehe', 'holehe', [username, '--only-used']))

        progress_per_tool = 30 / len(tools) if len(tools) > 0 else 0

        for tool_name, tool_cmd, tool_args in tools:
            progress.update(task, description=f"Running {tool_name}...")
            try:
                # Try different ways to find the tool
                cmd = None
                possible_paths = [
                    tool_cmd,
                    f'~/.local/bin/{tool_cmd}',
                    f'/usr/local/bin/{tool_cmd}',
                    f'python -m {tool_cmd}',
                ]
                
                for path in possible_paths:
                    expanded_path = os.path.expanduser(path)
                    try:
                        if path.startswith('python'):
                            # For python -m commands
                            output = subprocess.check_output(
                                path.split() + tool_args, 
                                text=True, 
                                timeout=120,
                                stderr=subprocess.DEVNULL
                            )
                        else:
                            output = subprocess.check_output(
                                [expanded_path] + tool_args, 
                                text=True, 
                                timeout=120,
                                stderr=subprocess.DEVNULL
                            )
                        results[f'{tool_name.lower()}_output'] = output
                        parse_tool_output(tool_name, output, results)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                        
            except Exception as e:
                console.print(f"[yellow]Warning: {tool_name} not available or failed: {str(e)}[/yellow]")
            
            progress.update(task, advance=progress_per_tool)

        # Web scraping for additional sources
        progress.update(task, description="Searching additional sources...")
        try:
            # Search Pastebin-like sites
            paste_sites = [
                f'https://pastebin.com/u/{username}',
                f'https://www.codepad.co/{username}',
            ]
            
            for site in paste_sites:
                try:
                    r = requests.get(site, timeout=5)
                    if r.status_code == 200 and username.lower() in r.text.lower():
                        results['links'].append(site)
                except:
                    pass
                    
        except Exception as e:
            console.print(f"[yellow]Web scraping failed: {str(e)}[/yellow]")
        
        progress.update(task, advance=10)

        # Final processing
        progress.update(task, description="Processing results...")
        
        # Deduplicate and clean results
        results['usernames'] = list(dict.fromkeys([u for u in results['usernames'] if u and len(u.strip()) > 2]))
        results['images'] = list(dict.fromkeys([i for i in results['images'] if i and i.startswith('http')]))
        results['links'] = list(dict.fromkeys([l for l in results['links'] if l and l.startswith('http')]))
        results['emails'] = list(dict.fromkeys(results['emails']))
        
        progress.update(task, completed=100)

    # Display results in a formatted way
    display_results(console, username, results)

def parse_tool_output(tool_name, output, results):
    """Parse output from external tools"""
    if tool_name == 'Maigret':
        for line in output.split('\n'):
            if '[+]' in line and 'http' in line:
                # Extract URL from Maigret output
                url_match = re.search(r'(https?://[^\s]+)', line)
                if url_match:
                    results['links'].append(url_match.group(1))
    
    elif tool_name == 'Sherlock':
        for line in output.split('\n'):
            if '[+]' in line and 'http' in line:
                results['links'].append(line.split(' ')[-1])
    
    elif tool_name == 'Holehe':
        for line in output.split('\n'):
            if '[+]' in line and '@' in line:
                results['emails'].append(line.strip())

def display_results(console, username, results):
    """Display results in a formatted Rich output"""
    
    console.print(f"\n🎯 [bold cyan]Advanced OSINT Results for: {username}[/bold cyan]")
    
    # Profiles Table
    if results['profiles']:
        table = Table(title="📊 Found Profiles", show_header=True, header_style="bold magenta")
        table.add_column("Platform", style="cyan")
        table.add_column("URL", style="green")
        
        for profile in results['profiles']:
            table.add_row(profile['platform'], profile['url'])
        console.print(table)
    
    # Usernames
    if results['usernames']:
        console.print("\n👤 [bold]Usernames Found:[/bold]")
        for username in results['usernames']:
            console.print(f"  • {username}")
    
    # Images
    if results['images']:
        console.print("\n🖼️ [bold]Profile Images:[/bold]")
        for img in results['images']:
            console.print(f"  • {img}")
    
    # Links
    if results['links']:
        console.print("\n🔗 [bold]Related Links:[/bold]")
        for link in results['links'][:10]:  # Show first 10 links
            console.print(f"  • {link}")
        if len(results['links']) > 10:
            console.print(f"  ... and {len(results['links']) - 10} more")
    
    # Emails
    if results['emails']:
        console.print("\n📧 [bold]Email Checks:[/bold]")
        for email in results['emails']:
            console.print(f"  • {email}")
    
    # Tool Reports
    for tool in ['maigret', 'sherlock', 'holehe']:
        if f'{tool}_output' in results and results[f'{tool}_output']:
            console.print(f"\n🔍 [bold]{tool.title()} Report:[/bold]")
            console.print(Panel(results[f'{tool}_output'], title=f"{tool.title()} Output", title_align="left"))
    
    # Generate search queries
    generate_search_queries(console, username)

def generate_search_queries(console, username):
    """Generate useful search queries"""
    
    console.print("\n🔎 [bold]Recommended Search Queries:[/bold]")
    
    search_suggestions = [
        f"\"{username}\" site:github.com OR site:gitlab.com",
        f"\"{username}\" site:reddit.com OR site:twitter.com",
        f"\"{username}\" filetype:pdf OR filetype:doc",
        f"inurl:{username} site:pastebin.com OR site:codepad.co",
        f"\"{username}\" intitle:\"profile\" OR intitle:\"about\"",
        f"\"{username}\" @gmail.com OR @yahoo.com OR @hotmail.com",
    ]
    
    for query in search_suggestions:
        console.print(f"  • {query}")

def check_dependencies():
    """Check if required tools are installed"""
    console = Console()
    missing_tools = []
    
    tools_to_check = ['maigret', 'sherlock', 'holehe']
    
    for tool in tools_to_check:
        try:
            subprocess.run([tool, '--help'], capture_output=True, timeout=5)
        except:
            missing_tools.append(tool)
    
    if missing_tools:
        console.print(f"\n[yellow]⚠️  The following tools are not installed: {', '.join(missing_tools)}[/yellow]")
        console.print("[yellow]You can install them with:[/yellow]")
        console.print("[cyan]pip install maigret sherlock holehe[/cyan]")
        console.print("[yellow]Some features will be limited without these tools.[/yellow]\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        check_dependencies()
        search_username(username)
    else:
        print("Usage: python advanced_scanner.py <username>")
        print("Example: python advanced_scanner.py john_doe")