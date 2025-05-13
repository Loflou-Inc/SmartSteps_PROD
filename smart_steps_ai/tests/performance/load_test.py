"""
Smart Steps AI Module - API Load Testing

This script performs load testing on the Smart Steps AI REST API.
It simulates multiple concurrent users and measures response times.

Usage:
    python -m tests.performance.load_test

Requirements:
    - The API server must be running on localhost:8000
    - A test user account must be available or will be created
"""

import asyncio
import json
import random
import statistics
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import aiohttp
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

# Constants
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "username": "loadtest_user",
    "password": "loadtest_password",
    "email": "loadtest@example.com",
    "full_name": "Load Test User"
}

# Initialize rich console
console = Console()
app = typer.Typer()

class LoadTestClient:
    """Client for load testing the Smart Steps AI API."""
    
    def __init__(self, user_id: int, auth_token: str):
        """Initialize with user ID and authentication token."""
        self.user_id = user_id
        self.auth_token = auth_token
        self.session_id = None
        self.conversation_ids = []
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        self.response_times = []
    
    async def create_session(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Create a new session and return its ID."""
        start_time = time.time()
        
        try:
            client_name = f"LoadTestClient_{self.user_id}_{random.randint(1000, 9999)}"
            session_data = {
                "client_name": client_name,
                "persona_id": "therapist_cbt",  # Using default persona
                "metadata": {
                    "load_test": True,
                    "client_age": random.randint(18, 65),
                    "client_gender": random.choice(["male", "female", "other"]),
                }
            }
            
            async with session.post(f"{BASE_URL}/sessions", 
                                   headers=self.headers,
                                   json=session_data) as response:
                elapsed = time.time() - start_time
                self.response_times.append(("create_session", elapsed))
                
                if response.status == 201:
                    data = await response.json()
                    self.session_id = data["id"]
                    return self.session_id
                else:
                    console.log(f"User {self.user_id}: Failed to create session, status: {response.status}")
                    return None
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.response_times.append(("create_session_error", elapsed))
            console.log(f"User {self.user_id}: Error creating session: {str(e)}")
            return None
    
    async def send_message(self, session: aiohttp.ClientSession) -> bool:
        """Send a message in the current session."""
        if not self.session_id:
            return False
        
        start_time = time.time()
        
        try:
            # Generate a random message
            test_messages = [
                "I've been feeling anxious lately.",
                "Work has been really stressful this week.",
                "I had a conflict with my friend yesterday.",
                "I'm having trouble sleeping at night.",
                "I don't know how to handle this situation.",
                "I feel like nobody understands me.",
                "I've been trying the techniques you suggested last time.",
                "I had a panic attack yesterday at work.",
                "My family is pressuring me about my career choices.",
                "I feel like I'm making progress but still struggle sometimes."
            ]
            
            message_data = {
                "content": random.choice(test_messages),
                "metadata": {
                    "load_test": True,
                    "timestamp": time.time()
                }
            }
            
            async with session.post(
                f"{BASE_URL}/sessions/{self.session_id}/conversations", 
                headers=self.headers,
                json=message_data
            ) as response:
                elapsed = time.time() - start_time
                self.response_times.append(("send_message", elapsed))
                
                if response.status == 201:
                    data = await response.json()
                    self.conversation_ids.append(data["id"])
                    return True
                else:
                    console.log(f"User {self.user_id}: Failed to send message, status: {response.status}")
                    return False
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.response_times.append(("send_message_error", elapsed))
            console.log(f"User {self.user_id}: Error sending message: {str(e)}")
            return False
    
    async def get_session_analysis(self, session: aiohttp.ClientSession) -> bool:
        """Get analysis for the current session."""
        if not self.session_id:
            return False
        
        start_time = time.time()
        
        try:
            async with session.get(
                f"{BASE_URL}/analysis/sessions/{self.session_id}", 
                headers=self.headers
            ) as response:
                elapsed = time.time() - start_time
                self.response_times.append(("get_analysis", elapsed))
                
                if response.status == 200:
                    return True
                else:
                    console.log(f"User {self.user_id}: Failed to get analysis, status: {response.status}")
                    return False
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.response_times.append(("get_analysis_error", elapsed))
            console.log(f"User {self.user_id}: Error getting analysis: {str(e)}")
            return False
    
    async def list_sessions(self, session: aiohttp.ClientSession) -> bool:
        """List all sessions for the user."""
        start_time = time.time()
        
        try:
            async with session.get(
                f"{BASE_URL}/sessions", 
                headers=self.headers
            ) as response:
                elapsed = time.time() - start_time
                self.response_times.append(("list_sessions", elapsed))
                
                if response.status == 200:
                    return True
                else:
                    console.log(f"User {self.user_id}: Failed to list sessions, status: {response.status}")
                    return False
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.response_times.append(("list_sessions_error", elapsed))
            console.log(f"User {self.user_id}: Error listing sessions: {str(e)}")
            return False
    
    async def run_user_simulation(self, session: aiohttp.ClientSession, 
                                 num_messages: int = 5, 
                                 include_analysis: bool = True) -> List[Tuple[str, float]]:
        """Run a complete user simulation."""
        # Create a session
        if not await self.create_session(session):
            return self.response_times
        
        # Send multiple messages
        for _ in range(num_messages):
            if not await self.send_message(session):
                break
            # Add small random delay between messages
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Get session analysis if requested
        if include_analysis and self.session_id:
            await self.get_session_analysis(session)
        
        # List sessions
        await self.list_sessions(session)
        
        return self.response_times

async def authenticate_user(session: aiohttp.ClientSession) -> Optional[str]:
    """Authenticate a test user and return the token."""
    try:
        # Try to authenticate
        async with session.post(
            f"{BASE_URL}/auth/token",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["access_token"]
            
            # If authentication fails, try to create the user
            async with session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            ) as reg_response:
                if reg_response.status == 201:
                    # Try authentication again
                    async with session.post(
                        f"{BASE_URL}/auth/token",
                        json={
                            "username": TEST_USER["username"],
                            "password": TEST_USER["password"]
                        }
                    ) as auth_response:
                        if auth_response.status == 200:
                            data = await auth_response.json()
                            return data["access_token"]
                
                console.log(f"Failed to authenticate: {response.status}, Register: {reg_response.status}")
                return None
                
    except Exception as e:
        console.log(f"Error during authentication: {str(e)}")
        return None

async def run_load_test(num_users: int, 
                       messages_per_user: int, 
                       include_analysis: bool) -> Dict:
    """Run load test with multiple simulated users."""
    results = {
        "start_time": datetime.now().isoformat(),
        "num_users": num_users,
        "messages_per_user": messages_per_user,
        "include_analysis": include_analysis,
        "user_response_times": [],
        "summary": {}
    }
    
    # Create aiohttp ClientSession for all requests
    async with aiohttp.ClientSession() as session:
        # Authenticate user
        auth_token = await authenticate_user(session)
        if not auth_token:
            console.log("Failed to authenticate. Aborting load test.")
            return results
        
        # Create and run user simulations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn()
        ) as progress:
            # Create task for each user
            task = progress.add_task(f"Running load test with {num_users} users...", total=num_users)
            
            # Create user clients
            clients = [LoadTestClient(i, auth_token) for i in range(num_users)]
            
            # Run user simulations concurrently
            tasks = []
            for client in clients:
                task = client.run_user_simulation(
                    session=session,
                    num_messages=messages_per_user,
                    include_analysis=include_analysis
                )
                tasks.append(task)
            
            # Wait for all simulations to complete
            user_results = await asyncio.gather(*tasks)
            progress.update(task, completed=num_users)
        
        # Store results
        for i, response_times in enumerate(user_results):
            results["user_response_times"].append({
                "user_id": i,
                "response_times": response_times
            })
    
    # Calculate summary statistics
    all_response_times = {}
    for user_result in results["user_response_times"]:
        for endpoint, time_taken in user_result["response_times"]:
            if endpoint not in all_response_times:
                all_response_times[endpoint] = []
            all_response_times[endpoint].append(time_taken)
    
    # Calculate statistics for each endpoint
    for endpoint, times in all_response_times.items():
        if times:
            results["summary"][endpoint] = {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "median": statistics.median(times),
                "p95": sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else None
            }
    
    results["end_time"] = datetime.now().isoformat()
    return results

def display_results(results: Dict):
    """Display load test results in a formatted table."""
    console.print("\n[bold green]Load Test Results[/bold green]")
    console.print(f"Start Time: {results['start_time']}")
    console.print(f"End Time: {results['end_time']}")
    console.print(f"Number of Users: {results['num_users']}")
    console.print(f"Messages per User: {results['messages_per_user']}")
    console.print(f"Include Analysis: {results['include_analysis']}")
    
    # Create and display summary table
    table = Table(title="Response Time Summary (seconds)")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Min", style="green")
    table.add_column("Max", style="red")
    table.add_column("Average", style="yellow")
    table.add_column("Median", style="blue")
    table.add_column("95th %", style="purple")
    
    for endpoint, stats in results["summary"].items():
        p95 = f"{stats['p95']:.3f}" if stats['p95'] is not None else "N/A"
        table.add_row(
            endpoint,
            str(stats["count"]),
            f"{stats['min']:.3f}",
            f"{stats['max']:.3f}",
            f"{stats['avg']:.3f}",
            f"{stats['median']:.3f}",
            p95
        )
    
    console.print(table)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"loadtest_results_{timestamp}.json"
    result_path = f"G:/My Drive/Deftech/SmartSteps/smart_steps_ai/tests/performance/results/{filename}"
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    
    with open(result_path, "w") as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\nResults saved to [bold]{result_path}[/bold]")

@app.command()
def main(
    num_users: int = typer.Option(10, help="Number of users to simulate"),
    messages_per_user: int = typer.Option(5, help="Number of messages each user sends"),
    include_analysis: bool = typer.Option(True, help="Include session analysis requests"),
):
    """Run a load test on the Smart Steps AI API."""
    console.print(f"[bold blue]Starting load test with {num_users} users[/bold blue]")
    console.print(f"Each user will send {messages_per_user} messages")
    console.print(f"Include analysis requests: {include_analysis}")
    
    try:
        # Run the load test
        results = asyncio.run(run_load_test(
            num_users=num_users,
            messages_per_user=messages_per_user,
            include_analysis=include_analysis
        ))
        
        # Display results
        display_results(results)
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Load test interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error during load test: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    app()
