"""
Pytest configuration for box assembly tests.

This configuration provides:
- Logging setup (console + file)
- Shared fixtures (box_assembly, detected_hinge)
- Report generation (HTML + snapshots)
"""

import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_run.log')
    ]
)

logger = logging.getLogger(__name__)

# Make test utilities available
sys.path.insert(0, str(Path(__file__).parent))

import pytest

logger.info("="*70)
logger.info("PYTEST CONFIGURATION LOADED")
logger.info("="*70)


def pytest_sessionfinish(session, exitstatus):
    """Generate report after test session completes."""
    logger.info("\n" + "="*70)
    logger.info("TEST SESSION SUMMARY")
    logger.info("="*70)
    
    # Try to generate HTML report if visualizer is available
    try:
        from visualizer import ensure_failure_dir, create_html_report
        
        failure_dir = ensure_failure_dir()
        
        # Collect all PNG files from failures
        failures = []
        if os.path.exists(failure_dir):
            for filename in sorted(os.listdir(failure_dir)):
                if filename.endswith('.png'):
                    failures.append({
                        'test_name': filename.replace('.png', ''),
                        'image_path': os.path.join(failure_dir, filename)
                    })
        
        # Generate report
        if failures:
            create_html_report(failures)
            logger.info(f"✓ HTML report generated with {len(failures)} image(s)")
        else:
            logger.info("✓ No failures captured")
    
    except ImportError:
        logger.warning("Visualizer not available for HTML report")
    except Exception as e:
        logger.warning(f"Could not generate HTML report: {e}")
    
    logger.info("="*70)
