"""Performance benchmarks for large repository analysis."""
import os
import time
import tempfile
import shutil
import pytest
import git
from pathlib import Path
from datetime import datetime, timedelta

# Skip these tests by default as they're performance benchmarks
pytestmark = pytest.mark.performance

# Constants for test repository generation
NUM_COMMITS = 1000
NUM_FILES = 100
NUM_BRANCHES = 10
NUM_TAGS = 10


def generate_test_file(content_length=1000):
    """Generate a test file with random content."""
    import random
    import string
    
    chars = string.ascii_letters + string.digits + '\n'
    # Generate random content
    content = ''.join(random.choices(chars, k=content_length))
    
    # Add some predictable patterns to make compression less effective
    content += '\n' + 'x' * 1000 + '\n'
    return content


def create_test_repo(path, num_commits, num_files, num_branches, num_tags):
    """Create a test git repository with specified parameters."""
    repo = git.Repo.init(path)
    
    # Create initial commit
    readme_path = os.path.join(path, 'README.md')
    with open(readme_path, 'w') as f:
        f.write("# Test Repository\n\nThis is a test repository for performance benchmarking.")
    
    repo.index.add([readme_path])
    repo.index.commit("Initial commit")
    
    # Create branches
    for i in range(1, num_branches + 1):
        repo.create_head(f'feature-{i}')
    
    # Create commits across all branches
    for commit_num in range(1, num_commits + 1):
        # Switch to a random branch
        branch_num = (commit_num % num_branches) + 1
        branch_name = f'feature-1' if num_branches == 0 else f'feature-{branch_num}'
        
        if branch_name in repo.heads:
            repo.heads[branch_name].checkout()
        else:
            repo.create_head(branch_name)
            repo.heads[branch_name].checkout()
        
        # Create or modify files
        for file_num in range(1, num_files + 1):
            file_path = os.path.join(path, f'file_{file_num}.txt')
            with open(file_path, 'a') as f:
                f.write(f"Commit {commit_num} - {datetime.utcnow().isoformat()}\n")
                f.write(generate_test_file())
            
            repo.index.add([file_path])
        
        # Create a commit
        commit_message = f"Commit {commit_num} on {branch_name}"
        repo.index.commit(commit_message)
        
        # Create tags occasionally
        if commit_num % (num_commits // num_tags) == 0 and commit_num > 0:
            repo.create_tag(f'v{commit_num//(num_commits//num_tags)}')
    
    # Return to a default branch (support both 'master' and 'main')
    try:
        default_head = getattr(repo.heads, "master")
    except AttributeError:
        # Prefer 'main' if present; otherwise, use the current head's reference
        default_head = getattr(repo.heads, "main", None)
        if default_head is None:
            try:
                default_head = repo.head.reference
            except Exception:
                # Fallback: pick the first available head if any exist
                default_head = repo.heads[0] if len(repo.heads) > 0 else None
    if default_head is not None:
        default_head.checkout()
    
    return repo


def test_benchmark_large_repo_analysis(benchmark):
    """Benchmark analysis of a large repository."""
    from beaconled.core.analyzer import GitAnalyzer
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test repository
        repo_path = os.path.join(temp_dir, 'test-repo')
        print(f"Creating test repository at {repo_path}...")
        
        # Use smaller numbers for the actual test to keep it fast
        test_commits = NUM_COMMITS // 10
        test_files = NUM_FILES // 10
        test_branches = min(3, NUM_BRANCHES)
        test_tags = min(3, NUM_TAGS)
        
        create_test_repo(repo_path, test_commits, test_files, test_branches, test_tags)
        
        # Initialize analyzer
        analyzer = GitAnalyzer(repo_path)
        
        # Define the function to benchmark
        def analyze():
            # Get analytics for different time ranges
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Run analytics
            analytics = analyzer.get_range_analytics(
                start_date=start_date,
                end_date=end_date
            )
            
            # Get commit stats
            stats = analyzer.get_commit_stats()
            
            return analytics, stats
        
        # Run the benchmark
        result = benchmark(analyze)
        
        # Basic assertions to ensure the benchmark ran correctly
        analytics, stats = result
        assert analytics is not None
        assert stats is not None


if __name__ == '__main__':
    # This is for manual testing of the benchmark
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-test-repo':
        repo_path = sys.argv[2] if len(sys.argv) > 2 else 'test-repo-large'
        print(f"Creating large test repository at {repo_path}...")
        
        if os.path.exists(repo_path):
            print(f"Error: {repo_path} already exists")
            sys.exit(1)
        
        create_test_repo(repo_path, NUM_COMMITS, NUM_FILES, NUM_BRANCHES, NUM_TAGS)
        print(f"Created test repository at {os.path.abspath(repo_path)}")
    else:
        print("Usage: python -m tests.performance.test_large_repo_benchmark --create-test-repo [path]")
        print("This will create a large test repository for performance testing.")
