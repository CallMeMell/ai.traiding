#!/usr/bin/env python3
"""
test_workflow_syntax.py - Test GitHub Actions Workflow Syntax
=============================================================
Simple test to verify workflow YAML can be parsed.
"""

import yaml
import sys
from pathlib import Path


def test_workflow_syntax():
    """Test that workflow YAML is valid."""
    workflow_path = Path(__file__).parent / ".github" / "workflows" / "session-smoke.yml"
    
    print(f"Testing workflow syntax: {workflow_path}")
    
    # Try to load the YAML
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Basic structure checks
        assert 'name' in workflow, "Workflow must have a name"
        # Note: YAML parses 'on:' as boolean True
        assert 'on' in workflow or True in workflow, "Workflow must have triggers (on)"
        assert 'jobs' in workflow, "Workflow must have jobs"
        
        # Check required jobs exist
        jobs = workflow['jobs']
        required_jobs = ['setup', 'deps', 'smoke', 'validate', 'artifacts', 'summary']
        for job_name in required_jobs:
            assert job_name in jobs, f"Job '{job_name}' is required"
        
        # Check triggers (YAML parses 'on:' as True)
        triggers = workflow.get('on') or workflow.get(True)
        assert 'workflow_dispatch' in triggers, "workflow_dispatch trigger required"
        assert 'pull_request' in triggers, "pull_request trigger should be present"
        
        # Check workflow_dispatch inputs
        dispatch = triggers['workflow_dispatch']
        if 'inputs' in dispatch:
            inputs = dispatch['inputs']
            assert 'duration_secs' in inputs, "duration_secs input required"
            assert 'mode' in inputs, "mode input required"
        
        print("✓ Workflow YAML is valid")
        print(f"✓ Found {len(jobs)} jobs: {', '.join(jobs.keys())}")
        print("✓ All required jobs present")
        print("✓ Triggers configured correctly")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"✗ YAML syntax error: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Workflow structure error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    success = test_workflow_syntax()
    sys.exit(0 if success else 1)
