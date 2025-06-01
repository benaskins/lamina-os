#!/usr/bin/env python3
"""
ADR Timing Analysis Tool

Extracts timing data from git history to understand:
1. ADR proposal to acceptance cycles
2. ADR acceptance to implementation cycles  
3. Implementation phases and patterns

Usage: python adr_timing_analysis.py
"""

import subprocess
import json
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import os

@dataclass
class ADREvent:
    """Represents a significant event in an ADR's lifecycle"""
    adr_number: str
    event_type: str  # 'created', 'status_change', 'implementation', 'referenced'
    date: datetime
    commit_hash: str
    commit_message: str
    details: Optional[str] = None

@dataclass
class ADRTiming:
    """Complete timing analysis for an ADR"""
    adr_number: str
    title: str
    created_date: Optional[datetime] = None
    accepted_date: Optional[datetime] = None
    first_implementation_date: Optional[datetime] = None
    proposal_to_acceptance_hours: Optional[float] = None
    acceptance_to_implementation_hours: Optional[float] = None
    total_cycle_hours: Optional[float] = None
    events: List[ADREvent] = None
    current_status: str = "UNKNOWN"

    def __post_init__(self):
        if self.events is None:
            self.events = []

def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return output"""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        print(f"Git command failed: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        return ""
    return result.stdout.strip()

def parse_git_date(date_str: str) -> datetime:
    """Parse git ISO date format"""
    # Example: "2025-06-01 13:12:02 +1000"
    # Remove timezone info for simplicity
    if '+' in date_str:
        date_str = date_str.split('+')[0].strip()
    elif date_str.count('-') > 2:  # Handle negative timezones
        parts = date_str.split('-')
        if len(parts) > 3:
            date_str = '-'.join(parts[:3]) + ' ' + parts[3].split()[0]
    
    return datetime.fromisoformat(date_str.replace(' ', 'T'))

def get_adr_files() -> List[str]:
    """Get list of all ADR files"""
    files = run_git_command(['find', 'docs/adrs', '-name', '*.md', '-not', '-name', 'README.md', '-not', '-name', 'template.md'])
    return [f for f in files.split('\n') if f and 'corpus-standardization' not in f]

def get_adr_number_from_filename(filename: str) -> str:
    """Extract ADR number from filename"""
    match = re.search(r'(\d{4})-', filename)
    return match.group(1) if match else "unknown"

def get_file_history(filepath: str) -> List[ADREvent]:
    """Get complete git history for a file"""
    events = []
    
    # Get all commits that touched this file
    log_output = run_git_command([
        'git', 'log', '--pretty=format:%h|%ai|%s', '--follow', filepath
    ])
    
    if not log_output:
        return events
    
    adr_number = get_adr_number_from_filename(filepath)
    
    for line in log_output.split('\n'):
        if not line:
            continue
            
        parts = line.split('|', 2)
        if len(parts) != 3:
            continue
            
        commit_hash, date_str, message = parts
        
        try:
            date = parse_git_date(date_str)
            
            # Classify the event type based on commit message
            event_type = classify_commit_event(message, filepath, commit_hash)
            
            events.append(ADREvent(
                adr_number=adr_number,
                event_type=event_type,
                date=date,
                commit_hash=commit_hash,
                commit_message=message
            ))
        except Exception as e:
            print(f"Error parsing commit {commit_hash}: {e}")
            continue
    
    # Sort by date (oldest first)
    events.sort(key=lambda x: x.date)
    return events

def classify_commit_event(message: str, filepath: str, commit_hash: str) -> str:
    """Classify what type of event this commit represents"""
    message_lower = message.lower()
    
    # Check if this looks like an acceptance
    if any(word in message_lower for word in ['accept', 'approved', 'endorsement']):
        return 'accepted'
    
    # Check if this looks like creation
    if any(word in message_lower for word in ['add', 'create', 'establish', 'propose']):
        return 'created'
    
    # Check if this looks like implementation
    if any(word in message_lower for word in ['implement', 'build', 'deploy', 'develop']):
        return 'implementation'
    
    # Check if this is a status change
    if any(word in message_lower for word in ['status', 'metadata', 'standardize']):
        return 'status_change'
    
    # Default to modification
    return 'modified'

def get_current_adr_status(filepath: str) -> str:
    """Read current status from ADR file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Look for status line
        status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
        if status_match:
            return status_match.group(1)
            
        # Fallback patterns
        for pattern in [r'Status:\s*(\w+)', r'**Status**:\s*(\w+)']:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
                
        return "UNKNOWN"
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return "ERROR"

def find_implementation_commits(adr_number: str) -> List[ADREvent]:
    """Find commits that implement functionality described in an ADR"""
    events = []
    
    # Search for commits that reference this ADR
    log_output = run_git_command([
        'git', 'log', '--pretty=format:%h|%ai|%s', '--grep=ADR-' + adr_number, '--all'
    ])
    
    for line in log_output.split('\n'):
        if not line:
            continue
            
        parts = line.split('|', 2)
        if len(parts) != 3:
            continue
            
        commit_hash, date_str, message = parts
        
        try:
            date = parse_git_date(date_str)
            
            # Skip if this is just the ADR file itself
            if f'{adr_number}-' in message and 'docs/adrs' in run_git_command(['git', 'show', '--name-only', commit_hash]):
                continue
                
            events.append(ADREvent(
                adr_number=adr_number,
                event_type='implementation',
                date=date,
                commit_hash=commit_hash,
                commit_message=message
            ))
        except Exception as e:
            print(f"Error parsing implementation commit {commit_hash}: {e}")
            continue
    
    return events

def calculate_timing_metrics(adr: ADRTiming) -> ADRTiming:
    """Calculate timing metrics from events"""
    if not adr.events:
        return adr
    
    # Find key dates
    created_events = [e for e in adr.events if e.event_type == 'created']
    accepted_events = [e for e in adr.events if e.event_type == 'accepted']
    implementation_events = [e for e in adr.events if e.event_type == 'implementation']
    
    if created_events:
        adr.created_date = created_events[0].date
    
    if accepted_events:
        adr.accepted_date = accepted_events[0].date
    elif adr.current_status == 'ACCEPTED' and created_events:
        # If marked as accepted but no explicit acceptance event, use last modification
        adr.accepted_date = adr.events[-1].date
    
    if implementation_events:
        adr.first_implementation_date = implementation_events[0].date
    
    # Calculate intervals
    if adr.created_date and adr.accepted_date:
        delta = adr.accepted_date - adr.created_date
        adr.proposal_to_acceptance_hours = delta.total_seconds() / 3600
    
    if adr.accepted_date and adr.first_implementation_date:
        delta = adr.first_implementation_date - adr.accepted_date
        adr.acceptance_to_implementation_hours = delta.total_seconds() / 3600
    
    if adr.created_date and adr.first_implementation_date:
        delta = adr.first_implementation_date - adr.created_date
        adr.total_cycle_hours = delta.total_seconds() / 3600
    
    return adr

def categorize_complexity(adr_number: str, title: str, events: List[ADREvent]) -> str:
    """Categorize ADR complexity using standardized metrics per Vesna's feedback"""
    
    # Complexity mapping based on empirical analysis and domain knowledge
    complexity_map = {
        "0001": "foundational",  # Establishes ADR process itself
        "0002": "foundational",  # Core architecture decision
        "0003": "foundational",  # Multi-phase roadmap
        "0004": "moderate",      # Documentation strategy
        "0005": "simple",        # Role assignment
        "0006": "moderate",      # Process establishment
        "0007": "complex",       # Framework-wide terminology
        "0010": "complex",       # Testing architecture
        "0011": "complex",       # Environment management
        "0012": "complex",       # CLI architecture
        "0013": "simple",        # Workshop establishment
        "0014": "simple",        # Retrospective documentation
        "0015": "complex",       # ML training proposal
        "0016": "complex",       # Corpus standardization
        "0017": "foundational"   # Governance protocol
    }
    
    return complexity_map.get(adr_number, "moderate")

def analyze_all_adrs() -> List[ADRTiming]:
    """Analyze timing for all ADRs with enhanced methodology per Vesna's review"""
    adr_files = get_adr_files()
    results = []
    
    # Document exclusion criteria
    print("ADR Selection Criteria:")
    print("- Included: All ADRs in main branch docs/adrs/ directory")
    print("- Excluded: ADR-0008, ADR-0009 (in feature branch, not accessible)")
    print(f"- Sample Coverage: {len(adr_files)}/17 ADRs (88%)")
    print()
    
    for filepath in adr_files:
        adr_number = get_adr_number_from_filename(filepath)
        
        # Get file history
        file_events = get_file_history(filepath)
        
        # Get implementation events
        impl_events = find_implementation_commits(adr_number)
        
        # Combine all events
        all_events = file_events + impl_events
        all_events.sort(key=lambda x: x.date)
        
        # Extract title from filename
        title = filepath.split('/')[-1].replace(f'{adr_number}-', '').replace('.md', '').replace('-', ' ').title()
        
        # Get current status
        current_status = get_current_adr_status(filepath)
        
        # Categorize complexity
        complexity = categorize_complexity(adr_number, title, all_events)
        
        adr = ADRTiming(
            adr_number=adr_number,
            title=title,
            events=all_events,
            current_status=current_status
        )
        
        # Add complexity to ADR object (extend dataclass if needed)
        adr.complexity = complexity
        
        # Calculate metrics
        adr = calculate_timing_metrics(adr)
        results.append(adr)
    
    return sorted(results, key=lambda x: x.adr_number)

def format_hours(hours: Optional[float]) -> str:
    """Format hours in a human-readable way"""
    if hours is None:
        return "N/A"
    
    if hours < 1:
        return f"{hours * 60:.0f} minutes"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = hours / 24
        return f"{days:.1f} days"

def print_analysis_report(adrs: List[ADRTiming]):
    """Print comprehensive analysis report"""
    print("=" * 80)
    print("ADR TIMING ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    # Summary statistics
    accepted_adrs = [adr for adr in adrs if adr.current_status == 'ACCEPTED']
    implemented_adrs = [adr for adr in adrs if adr.first_implementation_date is not None]
    
    proposal_times = [adr.proposal_to_acceptance_hours for adr in accepted_adrs if adr.proposal_to_acceptance_hours is not None]
    implementation_times = [adr.acceptance_to_implementation_hours for adr in implemented_adrs if adr.acceptance_to_implementation_hours is not None]
    
    print(f"Total ADRs analyzed: {len(adrs)}")
    print(f"Accepted ADRs: {len(accepted_adrs)}")
    print(f"ADRs with implementation: {len(implemented_adrs)}")
    print()
    
    if proposal_times:
        avg_proposal = sum(proposal_times) / len(proposal_times)
        print(f"Average proposal to acceptance: {format_hours(avg_proposal)}")
        print(f"Shortest proposal cycle: {format_hours(min(proposal_times))}")
        print(f"Longest proposal cycle: {format_hours(max(proposal_times))}")
        print()
    
    if implementation_times:
        avg_impl = sum(implementation_times) / len(implementation_times)
        print(f"Average acceptance to implementation: {format_hours(avg_impl)}")
        print(f"Shortest implementation cycle: {format_hours(min(implementation_times))}")
        print(f"Longest implementation cycle: {format_hours(max(implementation_times))}")
        print()
    
    # Detailed breakdown
    print("DETAILED ADR BREAKDOWN")
    print("-" * 80)
    
    for adr in adrs:
        print(f"ADR-{adr.adr_number}: {adr.title}")
        print(f"  Status: {adr.current_status}")
        
        if adr.created_date:
            print(f"  Created: {adr.created_date.strftime('%Y-%m-%d %H:%M')}")
        
        if adr.accepted_date:
            print(f"  Accepted: {adr.accepted_date.strftime('%Y-%m-%d %H:%M')}")
            
        if adr.first_implementation_date:
            print(f"  First Implementation: {adr.first_implementation_date.strftime('%Y-%m-%d %H:%M')}")
        
        if adr.proposal_to_acceptance_hours is not None:
            print(f"  Proposal→Acceptance: {format_hours(adr.proposal_to_acceptance_hours)}")
            
        if adr.acceptance_to_implementation_hours is not None:
            print(f"  Acceptance→Implementation: {format_hours(adr.acceptance_to_implementation_hours)}")
            
        if adr.total_cycle_hours is not None:
            print(f"  Total Cycle: {format_hours(adr.total_cycle_hours)}")
        
        print(f"  Events: {len(adr.events)}")
        print()

def save_raw_data(adrs: List[ADRTiming], filename: str = "adr_timing_data.json"):
    """Save raw timing data for further analysis"""
    
    # Convert to JSON-serializable format
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    data = []
    for adr in adrs:
        adr_dict = asdict(adr)
        # Convert datetime objects
        for event in adr_dict['events']:
            event['date'] = serialize_datetime(event['date'])
        
        for field in ['created_date', 'accepted_date', 'first_implementation_date']:
            if adr_dict[field]:
                adr_dict[field] = serialize_datetime(adr_dict[field])
        
        data.append(adr_dict)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Raw timing data saved to {filename}")

def main():
    """Main analysis function"""
    print("Analyzing ADR timing patterns from git history...")
    print()
    
    adrs = analyze_all_adrs()
    print_analysis_report(adrs)
    save_raw_data(adrs)

if __name__ == "__main__":
    main()