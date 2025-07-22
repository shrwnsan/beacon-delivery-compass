#!/usr/bin/env python
"""
Development Analytics Reporter
Generates comprehensive development analytics and reports for the Crypto Analysis Dashboard project.
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class GitAnalytics:
    """Git repository analytics generator."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        
    def run_git_command(self, command: List[str]) -> str:
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                ["git", "--no-pager"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return ""
    
    def get_commit_stats(self, commit_hash: str = "HEAD") -> Dict:
        """Get detailed statistics for a specific commit."""
        # Basic commit info
        commit_info = {
            "hash": self.run_git_command(["rev-parse", commit_hash]),
            "short_hash": self.run_git_command(["rev-parse", "--short", commit_hash]),
            "author": self.run_git_command(["show", "-s", "--format=%an", commit_hash]),
            "email": self.run_git_command(["show", "-s", "--format=%ae", commit_hash]),
            "date": self.run_git_command(["show", "-s", "--format=%ci", commit_hash]),
            "message": self.run_git_command(["show", "-s", "--format=%s", commit_hash]),
        }
        
        # Get branch info
        branches = self.run_git_command(["branch", "--contains", commit_hash])
        current_branch = "unknown"
        for line in branches.split('\n'):
            if not line.strip().startswith('('):
                current_branch = line.strip().lstrip('* ')
                break
        commit_info["branch"] = current_branch
        
        # File statistics
        stat_output = self.run_git_command(["show", "--stat", commit_hash])
        stats = self._parse_git_stats(stat_output)
        
        # File changes
        name_status = self.run_git_command(["show", "--name-status", commit_hash])
        file_changes = self._parse_file_changes(name_status)
        
        # File type breakdown
        changed_files = self.run_git_command(["show", "--name-only", commit_hash]).split('\n')
        file_types = self._analyze_file_types(changed_files)
        
        # Component breakdown
        components = self._analyze_components(changed_files)
        
        return {
            "commit": commit_info,
            "statistics": stats,
            "file_changes": file_changes,
            "file_types": file_types,
            "components": components,
            "impact_analysis": self._analyze_impact(changed_files, stats)
        }
    
    def _parse_git_stats(self, stat_output: str) -> Dict:
        """Parse git --stat output."""
        lines = stat_output.split('\n')
        summary_line = lines[-1] if lines else ""
        
        stats = {
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0
        }
        
        # Parse summary line like "8 files changed, 455 insertions(+), 36 deletions(-)"
        if "files changed" in summary_line:
            parts = summary_line.split(',')
            for part in parts:
                part = part.strip()
                if "files changed" in part:
                    match = re.search(r'(\d+)', part)
                    if match:
                        stats["files_changed"] = int(match.group(1))
                elif "insertion" in part:
                    match = re.search(r'(\d+)', part)
                    if match:
                        stats["insertions"] = int(match.group(1))
                elif "deletion" in part:
                    match = re.search(r'(\d+)', part)
                    if match:
                        stats["deletions"] = int(match.group(1))
        
        return stats
    
    def _parse_file_changes(self, name_status: str) -> Dict:
        """Parse git --name-status output."""
        changes = {
            "added": [],
            "modified": [],
            "deleted": [],
            "renamed": []
        }
        
        for line in name_status.split('\n'):
            if not line.strip():
                continue
            
            parts = line.split('\t')
            if len(parts) < 2:
                continue
                
            status = parts[0]
            filename = parts[1]
            
            if status == 'A':
                changes["added"].append(filename)
            elif status == 'M':
                changes["modified"].append(filename)
            elif status == 'D':
                changes["deleted"].append(filename)
            elif status.startswith('R'):
                changes["renamed"].append(filename)
        
        return changes
    
    def _analyze_file_types(self, files: List[str]) -> Dict:
        """Analyze file types in the commit."""
        type_counts = Counter()
        
        for file in files:
            if not file.strip():
                continue
            
            # Get just the filename, not the full path
            filename = file.split('/')[-1]
            
            if '.' in filename and not filename.startswith('.'):
                ext = '.' + filename.split('.')[-1]
            elif filename.startswith('.') and '.' in filename[1:]:
                # Handle files like .gitignore, .env.example
                ext = '.' + filename.split('.')[-1] if filename.count('.') > 1 else 'dotfile'
            else:
                ext = 'no-extension'
            
            type_counts[ext] += 1
        
        return dict(type_counts)
    
    def _analyze_components(self, files: List[str]) -> Dict:
        """Analyze which product components were affected."""
        components = {
            "backend": 0,
            "frontend": 0,
            "api": 0,
            "documentation": 0,
            "configuration": 0,
            "tests": 0,
            "other": 0
        }
        
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.env'}
        
        for file in files:
            if not file.strip():
                continue
            
            file_lower = file.lower()
            filename = file.split('/')[-1]
            
            # Focus on product-related components
            if 'backend' in file_lower or file.startswith('src/'):
                components["backend"] += 1
            elif 'frontend' in file_lower or file.endswith(('.js', '.ts', '.tsx', '.jsx', '.css', '.html')):
                components["frontend"] += 1
            elif 'api' in file_lower or 'service' in file_lower:
                components["api"] += 1
            elif 'test' in file_lower or filename.endswith(('.test.js', '.spec.js', '.test.ts', '.spec.ts')):
                components["tests"] += 1
            elif file.startswith('docs/') or file.endswith('.md'):
                components["documentation"] += 1
            elif any(file.endswith(ext) for ext in config_extensions):
                components["configuration"] += 1
            else:
                components["other"] += 1
        
        return components
    
    def _analyze_impact(self, files: List[str], stats: Dict) -> Dict:
        """Analyze the impact level of changes."""
        high_impact_patterns = [
            r'main\.py$',
            r'app\.py$',
            r'index\.(js|ts|tsx)$',
            r'config\.(py|js|ts)$',
            r'requirements\.txt$',
            r'package\.json$'
        ]
        
        medium_impact_patterns = [
            r'api/',
            r'services/',
            r'components/',
            r'hooks/',
            r'utils/'
        ]
        
        impact = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for file in files:
            if not file.strip():
                continue
            
            is_high = any(re.search(pattern, file) for pattern in high_impact_patterns)
            is_medium = any(re.search(pattern, file) for pattern in medium_impact_patterns)
            
            if is_high:
                impact["high"].append(file)
            elif is_medium:
                impact["medium"].append(file)
            else:
                impact["low"].append(file)
        
        return {
            "high_impact": len(impact["high"]),
            "medium_impact": len(impact["medium"]),
            "low_impact": len(impact["low"]),
            "files": impact
        }
    
    def get_range_analytics(self, since: str = "1 week ago", until: str = "HEAD") -> Dict:
        """Get analytics for a range of commits."""
        # Get commit list
        commit_list = self.run_git_command([
            "rev-list", 
            f"--since={since}",
            f"--until={until}",
            "HEAD"
        ]).split('\n')
        
        commit_list = [c for c in commit_list if c.strip()]
        
        analytics = {
            "period": {"since": since, "until": until},
            "total_commits": len(commit_list),
            "commits": [],
            "summary": {
                "total_files_changed": 0,
                "total_insertions": 0,
                "total_deletions": 0,
                "authors": Counter(),
                "file_types": Counter(),
                "components": Counter()
            }
        }
        
        for commit_hash in commit_list:
            commit_stats = self.get_commit_stats(commit_hash)
            analytics["commits"].append(commit_stats)
            
            # Update summary
            stats = commit_stats["statistics"]
            analytics["summary"]["total_files_changed"] += stats["files_changed"]
            analytics["summary"]["total_insertions"] += stats["insertions"]
            analytics["summary"]["total_deletions"] += stats["deletions"]
            analytics["summary"]["authors"][commit_stats["commit"]["author"]] += 1
            
            for file_type, count in commit_stats["file_types"].items():
                analytics["summary"]["file_types"][file_type] += count
            
            for component, count in commit_stats["components"].items():
                analytics["summary"]["components"][component] += count
        
        return analytics

def format_commit_stats(stats: Dict, format_type: str = "standard") -> str:
    """Format commit statistics for display."""
    commit = stats["commit"]
    statistics = stats["statistics"]
    
    if format_type == "standard":
        output = f"""📊 Commit Stats:
{statistics['files_changed']} files changed
{statistics['insertions']} insertions, {statistics['deletions']} deletions
Commit Hash: {commit['short_hash']}
Branch: {commit['branch']}
Author: {commit['author']}
Date: {commit['date']}"""
        
        if stats.get("file_types"):
            output += "\nFiles by Type:"
            for file_type, count in stats["file_types"].items():
                output += f"\n  - {file_type}: {count} files"
    
    elif format_type == "extended":
        file_changes = stats["file_changes"]
        components = stats["components"]
        impact = stats["impact_analysis"]
        
        # Calculate net changes
        net_changes = statistics['insertions'] - statistics['deletions']
        change_indicator = "📈 Growth" if net_changes > 0 else "📉 Reduction" if net_changes < 0 else "⚖️ Balance"
        
        # Product-focused insights
        product_focus = []
        if components.get("frontend", 0) > 0:
            product_focus.append("UI/UX improvements")
        if components.get("backend", 0) > 0:
            product_focus.append("Core functionality")
        if components.get("api", 0) > 0:
            product_focus.append("API enhancements")
        
        output = f"""--📊 Product Development Summary:
{statistics['files_changed']} files updated
{statistics['insertions']} new lines, {statistics['deletions']} removed
{change_indicator}: {abs(net_changes)} net changes
{len(file_changes['added'])} new features/files added
{len(file_changes['modified'])} existing features improved"""
        
        if file_changes['deleted']:
            output += f"\n{len(file_changes['deleted'])} deprecated features removed"
        
        if product_focus:
            output += f"\n\n--🎯 Product Focus Areas:"
            for focus in product_focus:
                output += f"\n  • {focus}"
        
        output += f"\n\n--🏗️ Component Impact:"
        for component, count in components.items():
            if count > 0 and component in ["backend", "frontend", "api", "tests"]:
                output += f"\n{component.title()}: {count} files affected"
        
        output += f"\n\n--⚡ Development Impact:"
        if impact['high_impact'] > 0:
            output += f"\n🔴 High Impact: {impact['high_impact']} files (core services)"
        if impact['medium_impact'] > 0:
            output += f"\n🟡 Medium Impact: {impact['medium_impact']} files (features/components)"
        if impact['low_impact'] > 0:
            output += f"\n🟢 Low Impact: {impact['low_impact']} files (docs, config)"
        
        output += f"""
\n--📝 Commit Details:
Hash: {commit['short_hash']}
Branch: {commit['branch']}
Author: {commit['author']}
Date: {commit['date']}
Message: {commit['message']}"""
    
    elif format_type == "json":
        return json.dumps(stats, indent=2, default=str)
    
    return output

def main():
    parser = argparse.ArgumentParser(description="Generate development analytics")
    parser.add_argument("commit", nargs="?", default="HEAD", help="Commit hash to analyze")
    parser.add_argument("-f", "--format", choices=["standard", "extended", "json"], 
                       default="standard", help="Output format")
    parser.add_argument("-r", "--range", action="store_true", 
                       help="Analyze range of commits")
    parser.add_argument("--since", default="1 week ago", 
                       help="Start date for range analysis")
    parser.add_argument("--until", default="HEAD", 
                       help="End date for range analysis")
    parser.add_argument("--repo", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    analytics = GitAnalytics(args.repo)
    
    try:
        if args.range:
            stats = analytics.get_range_analytics(args.since, args.until)
            if args.format == "json":
                print(json.dumps(stats, indent=2, default=str))
            else:
                # Calculate weekly insights
                total_changes = stats['summary']['total_insertions'] + stats['summary']['total_deletions']
                avg_files_per_commit = stats['summary']['total_files_changed'] / max(stats['total_commits'], 1)
                
                # Product velocity indicators
                velocity_score = min(100, (stats['total_commits'] * 10) + (avg_files_per_commit * 5))
                
                print(f"🚀 Weekly Product Development Report")
                print(f"Period: {args.since} to {args.until}")
                print()
                print(f"📊 Development Velocity:")
                print(f"   {stats['total_commits']} commits this week")
                print(f"   {stats['summary']['total_files_changed']} files updated")
                print(f"   {total_changes} total code changes")
                print(f"   {avg_files_per_commit:.1f} files per commit (avg)")
                
                print(f"\n🎯 Product Impact Areas:")
                component_summary = stats['summary']['components']
                for component in ['frontend', 'backend', 'api', 'tests']:
                    count = component_summary.get(component, 0)
                    if count > 0:
                        print(f"   • {component.title()}: {count} files")
                
                print(f"\n👥 Team Contributions:")
                for author, count in stats['summary']['authors'].most_common():
                    print(f"   • {author}: {count} commits")
                
                print(f"\n📈 Key Insights:")
                if stats['total_commits'] > 10:
                    print("   ✅ High development velocity - great momentum!")
                elif stats['total_commits'] > 5:
                    print("   ⚡ Steady progress being made")
                else:
                    print("   🐌 Consider increasing development pace")
                
                if component_summary.get('frontend', 0) > component_summary.get('backend', 0):
                    print("   🎨 Focus on user-facing improvements")
                elif component_summary.get('backend', 0) > component_summary.get('frontend', 0):
                    print("   ⚙️ Emphasis on core functionality")
                
                print(f"\n💡 Recommendations:")
                if component_summary.get('tests', 0) < stats['total_commits'] * 0.5:
                    print("   • Consider adding more tests")
                if stats['summary']['total_files_changed'] > 50:
                    print("   • Large changes - ensure thorough review")
        else:
            stats = analytics.get_commit_stats(args.commit)
            print(format_commit_stats(stats, args.format))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()