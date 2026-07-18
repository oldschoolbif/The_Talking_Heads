"""
Check status of HeyGen videos by video ID.
Useful for checking videos that timed out during generation.
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

# HeyGen API configuration
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_BASE_URL = "https://api.heygen.com/v2"

def check_video_status(video_id: str):
    """Check the status of a HeyGen video."""
    if not HEYGEN_API_KEY:
        print("[ERROR] HEYGEN_API_KEY not found in environment variables")
        return None
    
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Try both endpoint formats
    endpoints = [
        f"{HEYGEN_BASE_URL}/videos/{video_id}",
        f"{HEYGEN_BASE_URL}/video/{video_id}",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Checking: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 404:
                print(f"  [404] Video not found (may still be processing)")
                continue
            else:
                print(f"  [{response.status_code}] {response.text[:200]}")
                continue
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            continue
    
    return None

def format_video_info(data: dict):
    """Format video information for display."""
    if not data:
        return "No data available"
    
    # HeyGen API response structure
    video_data = data.get("data", data)
    
    status = video_data.get("status", "unknown")
    video_url = video_data.get("video_url") or video_data.get("url")
    created_at = video_data.get("created_at") or video_data.get("created")
    updated_at = video_data.get("updated_at") or video_data.get("updated")
    duration = video_data.get("duration")
    error = video_data.get("error") or video_data.get("error_message")
    
    result = []
    result.append(f"Status: {status.upper()}")
    
    if video_url:
        result.append(f"Video URL: {video_url}")
    
    if created_at:
        try:
            # Parse timestamp (could be ISO string or Unix timestamp)
            if isinstance(created_at, (int, float)):
                created_dt = datetime.fromtimestamp(created_at)
            else:
                from dateutil import parser
                created_dt = parser.parse(created_at)
            
            elapsed = datetime.now() - created_dt
            result.append(f"Created: {created_dt.strftime('%Y-%m-%d %H:%M:%S')} ({elapsed.total_seconds()/60:.1f} minutes ago)")
        except:
            result.append(f"Created: {created_at}")
    
    if updated_at:
        try:
            if isinstance(updated_at, (int, float)):
                updated_dt = datetime.fromtimestamp(updated_at)
            else:
                from dateutil import parser
                updated_dt = parser.parse(updated_at)
            
            elapsed = datetime.now() - updated_dt
            result.append(f"Updated: {updated_dt.strftime('%Y-%m-%d %H:%M:%S')} ({elapsed.total_seconds()/60:.1f} minutes ago)")
        except:
            result.append(f"Updated: {updated_at}")
    
    if duration:
        result.append(f"Duration: {duration} seconds")
    
    if error:
        result.append(f"Error: {error}")
    
    # Show full response for debugging
    result.append(f"\nFull response:")
    result.append(json.dumps(data, indent=2))
    
    return "\n".join(result)

def main():
    """Main function to check video statuses."""
    # Video IDs from the failed tests
    video_ids = [
        "f7f9cb05d2d9481a93817ff00b1402d0",  # Short_2Personas
        "03c0306748c24fff9d159238978e814e",  # Medium_2Personas
        "45430d0c77714835aafc15af2da41f93",  # Long_5Personas
    ]
    
    test_names = [
        "Short_2Personas",
        "Medium_2Personas",
        "Long_5Personas",
    ]
    
    print("="*70)
    print("HeyGen Video Status Check")
    print("="*70)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    for video_id, test_name in zip(video_ids, test_names):
        print(f"\n{'='*70}")
        print(f"Test: {test_name}")
        print(f"Video ID: {video_id}")
        print(f"{'='*70}")
        
        data = check_video_status(video_id)
        
        if data:
            info = format_video_info(data)
            print(info)
            results.append({
                "test": test_name,
                "video_id": video_id,
                "status": data.get("data", data).get("status", "unknown"),
                "has_url": bool(data.get("data", data).get("video_url") or data.get("data", data).get("url"))
            })
        else:
            print("[INFO] Could not retrieve video status")
            results.append({
                "test": test_name,
                "video_id": video_id,
                "status": "unknown",
                "has_url": False
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    for result in results:
        if result["has_url"]:
            status_icon = "[OK]"
        elif result["status"] == "processing":
            status_icon = "[...]"
        else:
            status_icon = "[X]"
        print(f"{status_icon} {result['test']:<20} Status: {result['status']:<15} Has URL: {result['has_url']}")
    
    print(f"\n{'='*70}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

