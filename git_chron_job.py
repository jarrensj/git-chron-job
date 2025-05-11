#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime
import pytz
from typing import List, Optional

def get_commit_log(repo_path: str) -> Optional[List[datetime]]:
    """
    Get the commit log dates and times from the given git repository path in PST.
    
    Args:
        repo_path (str): Path to the git repository
        
    Returns:
        Optional[List[datetime]]: List of commit dates in PST timezone, or None if there was an error
    """
    
    # Validate repository path
    if not os.path.exists(repo_path):
        print(f"Error: Path '{repo_path}' does not exist.")
        return None
    
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        return None

    try:
        # Run git log command to get the commit dates with ISO format
        log_output = subprocess.check_output(
            ["git", "-C", repo_path, "log", "--pretty=format:%cd", "--date=iso-strict"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Define timezone for conversion
        pst = pytz.timezone('America/Los_Angeles')
        
        # Parse and convert each date
        parsed_dates = []
        for date_str in log_output.splitlines():
            if not date_str.strip():
                continue
                
            try:
                # Parse the ISO format date with timezone
                utc_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                pst_time = utc_time.astimezone(pst)
                parsed_dates.append(pst_time)
            except ValueError as e:
                print(f"Warning: Could not parse date '{date_str}': {str(e)}")
        
        if not parsed_dates:
            print(f"Warning: No valid commit dates found in repository '{repo_path}'")
            return None
            
        # Sort dates from earliest to latest
        parsed_dates.sort()
        
        # Display the commit dates
        print(f"\nCommit dates and times (PST) for repository at '{repo_path}':")
        print("-" * 60)
        for pst_time in parsed_dates:
            print(pst_time.strftime('%A, %Y-%m-%d %H:%M:%S %Z'))
        print("-" * 60)
        print(f"Total commits: {len(parsed_dates)}")
        
        return parsed_dates
    
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e.output}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python3 git_chron_job.py <path_to_git_repo>")
        sys.exit(1)
        
    repo_path = sys.argv[1]
    get_commit_log(repo_path)

if __name__ == "__main__":
    main()