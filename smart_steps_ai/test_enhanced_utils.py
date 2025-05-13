"""Test script for enhanced utilities."""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import enhanced utilities
from src.smart_steps_ai.utils.enhanced_logging import StructuredLogger
from src.smart_steps_ai.utils.enhanced_validation import (
    validate_type, validate_range, validate_email, validate_date
)
from src.smart_steps_ai.utils.security import (
    generate_random_string, hash_password, verify_password,
    encrypt_data, decrypt_data, generate_hmac, verify_hmac,
    create_rate_limiter, generate_timed_token, verify_timed_token
)
from src.smart_steps_ai.config.enhanced_config import ConfigManager


def test_structured_logger():
    """Test the structured logger."""
    print("\n===== Testing Structured Logger =====")
    
    # Create a structured logger
    logger = StructuredLogger(
        name="test_logger",
        level="debug",
        context={"app": "test_app", "version": "1.0.0"}
    )
    
    # Log at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message", context={"extra": "warning context"})
    
    # Test performance timing
    logger.start_timer("test_operation")
    time.sleep(1)  # Simulate work
    elapsed = logger.stop_timer("test_operation", level="info")
    
    logger.log_performance(
        operation="test_operation",
        elapsed=elapsed,
        success=True,
        details={"operation_type": "test", "items_processed": 42}
    )
    
    print("Structured logger test completed - check logs for output")
    return True


def test_enhanced_validation():
    """Test enhanced validation utilities."""
    print("\n===== Testing Enhanced Validation =====")
    
    # Test validate_type
    type_results = [
        validate_type("test", str, "string_value"),
        validate_type(123, int, "int_value"),
        validate_type(123, str, "should_be_string"),
        validate_type({"key": "value"}, dict, "dict_value")
    ]
    
    print("Type Validation Results:")
    for i, (success, error) in enumerate(type_results, 1):
        result = "PASSED" if success else f"FAILED: {error}"
        print(f"  {i}. {result}")
    
    # Test validate_range
    range_results = [
        validate_range(5, 0, 10, "in_range"),
        validate_range(15, 0, 10, "out_of_range"),
        validate_range(-5, 0, 10, "below_min"),
        validate_range(10, 0, 10, "at_max")
    ]
    
    print("\nRange Validation Results:")
    for i, (success, error) in enumerate(range_results, 1):
        result = "PASSED" if success else f"FAILED: {error}"
        print(f"  {i}. {result}")
    
    # Test validate_email
    email_results = [
        validate_email("test@example.com"),
        validate_email("invalid.email"),
        validate_email("test.email+tag@example.co.uk"),
        validate_email("not-an-email")
    ]
    
    print("\nEmail Validation Results:")
    for i, (success, error) in enumerate(email_results, 1):
        result = "PASSED" if success else f"FAILED: {error}"
        print(f"  {i}. {result}")
    
    # Test validate_date
    date_results = [
        validate_date("2023-01-01"),
        validate_date("2023/01/01"),
        validate_date("01/01/2023", format_str="%m/%d/%Y"),
        validate_date("not-a-date")
    ]
    
    print("\nDate Validation Results:")
    for i, (success, error, _) in enumerate(date_results, 1):
        result = "PASSED" if success else f"FAILED: {error}"
        print(f"  {i}. {result}")
    
    return True


def test_security():
    """Test security utilities."""
    print("\n===== Testing Security Utilities =====")
    
    # Test password hashing
    password = "SecurePassword123!"
    hashed = hash_password(password)
    
    verify_correct = verify_password(password, hashed)
    verify_wrong = verify_password("WrongPassword", hashed)
    
    print(f"Password Hashing:")
    print(f"  Original password verified: {'PASSED' if verify_correct else 'FAILED'}")
    print(f"  Wrong password rejected: {'PASSED' if not verify_wrong else 'FAILED'}")
    
    # Test encryption
    secret_key = os.urandom(32)
    original_text = "This is a secret message"
    
    encrypted = encrypt_data(original_text, secret_key)
    decrypted = decrypt_data(encrypted, secret_key)
    
    print(f"\nEncryption/Decryption:")
    print(f"  Encryption successful: {'PASSED' if encrypted else 'FAILED'}")
    print(f"  Decryption matches original: {'PASSED' if decrypted == original_text else 'FAILED'}")
    
    # Test HMAC
    message = "Verify this message integrity"
    secret = "my_secret_key"
    
    signature = generate_hmac(message, secret)
    valid_hmac = verify_hmac(message, signature, secret)
    invalid_hmac = verify_hmac("Modified message", signature, secret)
    
    print(f"\nHMAC Verification:")
    print(f"  Valid HMAC accepted: {'PASSED' if valid_hmac else 'FAILED'}")
    print(f"  Invalid HMAC rejected: {'PASSED' if not invalid_hmac else 'FAILED'}")
    
    # Test rate limiter
    rate_limiter = create_rate_limiter(max_calls=3, time_window=5)
    
    print(f"\nRate Limiter:")
    
    # Make 4 calls, expecting the 4th to be rejected
    results = []
    for i in range(4):
        allowed, remaining, reset = rate_limiter("test_user")
        results.append(allowed)
        print(f"  Call {i+1}: {'Allowed' if allowed else 'Rejected'}, Remaining: {remaining}, Reset: {reset}s")
    
    print(f"  Rate limiter working correctly: {'PASSED' if results == [True, True, True, False] else 'FAILED'}")
    
    return True


def test_enhanced_config():
    """Test enhanced configuration manager."""
    print("\n===== Testing Enhanced Configuration Manager =====")
    
    # Create temp config directory
    config_dir = Path("./temp_config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "test_config.json"
    
    # Create configuration manager
    config_manager = ConfigManager(
        config_file=config_file,
        env_prefix="TEST_",
        auto_save=True
    )
    
    # Set default configuration
    default_config: Dict[str, Any] = {
        "app": {
            "name": "Test App",
            "version": "1.0.0"
        },
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
    
    config_manager.set_defaults(default_config)
    
    # Test getting configuration
    app_name = config_manager.get("app.name")
    db_host = config_manager.get("database.host")
    
    print(f"Config Values:")
    print(f"  app.name = {app_name}")
    print(f"  database.host = {db_host}")
    
    # Test setting configuration
    config_manager.set("app.debug", True)
    config_manager.set("database.username", "testuser")
    
    # Test nested configuration
    config_manager.set("logging.levels.console", "info")
    config_manager.set("logging.levels.file", "debug")
    
    # Save configuration
    config_manager.save()
    
    # Verify file was created
    file_exists = config_file.exists()
    print(f"\nConfig File Created: {'PASSED' if file_exists else 'FAILED'}")
    
    if file_exists:
        # Test reload and verify values
        config_manager.reload()
        
        debug_value = config_manager.get("app.debug")
        username = config_manager.get("database.username")
        
        print(f"Reloaded Config Values:")
        print(f"  app.debug = {debug_value}")
        print(f"  database.username = {username}")
        
        # Clean up temp config
        try:
            config_file.unlink()
            config_dir.rmdir()
            print("\nCleaned up temporary config files")
        except Exception as e:
            print(f"\nError cleaning up config files: {e}")
    
    return True


if __name__ == "__main__":
    # Run all tests
    test_structured_logger()
    test_enhanced_validation()
    test_security()
    test_enhanced_config()
    print("\nAll utility tests completed!")
