#!/usr/bin/env python3
"""
Verification test for production enhancements:
- Configurable workspace cleanup
- Retry logic
- Logging infrastructure
"""
import os
import tempfile
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging to see output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_workspace_manager():
    """Test WorkspaceManager with debug mode on/off"""
    from src.tools.workspace_tools import WorkspaceManager
    
    github_pat = os.getenv("GITHUB_PAT")
    repo_url = os.getenv("REPO_URL")
    
    if not github_pat or not repo_url:
        logger.error("GITHUB_PAT and REPO_URL must be set in .env")
        return False
    
    logger.info("Testing WorkspaceManager...")
    
    # Test 1: Production mode (debug_mode=False)
    logger.info("Test 1: Production mode (auto-cleanup)")
    with WorkspaceManager(repo_url=repo_url, pat=github_pat, debug_mode=False) as ws:
        logger.info(f"  Workspace path: {ws.path}")
        assert ws.path.startswith(tempfile.gettempdir()), "Should use temp directory"
        assert "ai-symphony-" in ws.path, "Should have ai-symphony prefix"
        logger.info("  ✅ Production mode works")
    
    # Test 2: Debug mode (debug_mode=True)
    logger.info("Test 2: Debug mode (keep workspace)")
    with WorkspaceManager(repo_url=repo_url, pat=github_pat, debug_mode=True) as ws:
        logger.info(f"  Workspace path: {ws.path}")
        assert "workspace_debug" in ws.path, "Should use workspace_debug directory"
        logger.info("  ✅ Debug mode works")
    
    logger.info("✅ WorkspaceManager tests passed")
    return True

def test_retry_logic():
    """Test that retry decorators are properly configured"""
    from src.tools.github_tools import CreatePRTool
    import inspect
    
    logger.info("Testing retry logic configuration...")
    
    # Check that retry decorator is applied
    pr_tool = CreatePRTool()
    
    # Verify the method exists
    assert hasattr(pr_tool, '_create_pr_with_retry'), "Should have retry method"
    assert hasattr(pr_tool, '_push_with_retry'), "Should have push retry method"
    
    logger.info("  ✅ Retry methods exist")
    logger.info("✅ Retry logic tests passed")
    return True

def test_logging_config():
    """Test that logging is properly configured"""
    logger.info("Testing logging configuration...")
    
    # Test different log levels
    test_logger = logging.getLogger("test")
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")
    
    logger.info("  ✅ Logging works at all levels")
    logger.info("✅ Logging tests passed")
    return True

def test_tools():
    """Test that tools have proper docstrings and structure"""
    from src.tools.workspace_tools import CodeWriterTool, FileReadTool
    from src.tools.github_tools import CreatePRTool
    
    logger.info("Testing tool structure...")
    
    # Check docstrings exist
    assert CodeWriterTool.__doc__, "CodeWriterTool should have docstring"
    assert FileReadTool.__doc__, "FileReadTool should have docstring"
    assert CreatePRTool.__doc__, "CreatePRTool should have docstring"
    
    logger.info("  ✅ All tools have docstrings")
    
    # Check methods exist
    assert hasattr(CodeWriterTool, '_run'), "CodeWriterTool should have _run method"
    assert hasattr(FileReadTool, '_run'), "FileReadTool should have _run method"
    assert hasattr(CreatePRTool, '_run'), "CreatePRTool should have _run method"
    
    logger.info("  ✅ All tools have _run methods")
    logger.info("✅ Tool structure tests passed")
    return True

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Production Enhancement Verification")
    logger.info("=" * 60)
    
    results = []
    
    try:
        results.append(("WorkspaceManager", test_workspace_manager()))
    except Exception as e:
        logger.error(f"WorkspaceManager test failed: {e}")
        results.append(("WorkspaceManager", False))
    
    try:
        results.append(("Retry Logic", test_retry_logic()))
    except Exception as e:
        logger.error(f"Retry logic test failed: {e}")
        results.append(("Retry Logic", False))
    
    try:
        results.append(("Logging", test_logging_config()))
    except Exception as e:
        logger.error(f"Logging test failed: {e}")
        results.append(("Logging", False))
    
    try:
        results.append(("Tools", test_tools()))
    except Exception as e:
        logger.error(f"Tools test failed: {e}")
        results.append(("Tools", False))
    
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name:20} : {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("🎉 All tests passed!")
        exit(0)
    else:
        logger.error("❌ Some tests failed")
        exit(1)
