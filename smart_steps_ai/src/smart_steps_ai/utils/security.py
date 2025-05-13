"""Security utilities for the Smart Steps AI module."""

import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_random_string(length: int = 32) -> str:
    """
    Generate a cryptographically secure random string.

    Args:
        length (int): Length of the random string (default: 32)

    Returns:
        str: Random string
    """
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): Password to hash

    Returns:
        str: Hashed password
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return string representation
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password (str): Password to verify
        hashed_password (str): Hashed password to check against

    Returns:
        bool: True if the password matches the hash
    """
    # Convert inputs to bytes
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Check password
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def generate_encryption_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Generate an encryption key from a password.

    Args:
        password (str): Password to derive key from
        salt (Optional[bytes]): Salt to use for key derivation (default: None, generates new salt)

    Returns:
        Tuple[bytes, bytes]: (key, salt) tuple
    """
    # Generate salt if not provided
    if salt is None:
        salt = os.urandom(16)
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Use PBKDF2 to derive a key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    
    key = kdf.derive(password_bytes)
    
    return key, salt


def encrypt_data(data: str, key: bytes) -> str:
    """
    Encrypt data using Fernet symmetric encryption.

    Args:
        data (str): Data to encrypt
        key (bytes): Encryption key

    Returns:
        str: Encrypted data as base64 string
    """
    # Create Fernet cipher
    cipher = Fernet(base64.urlsafe_b64encode(key))
    
    # Encrypt data
    encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
    
    # Return as base64 string
    return encrypted_bytes.decode('utf-8')


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Decrypt Fernet-encrypted data.

    Args:
        encrypted_data (str): Encrypted data as base64 string
        key (bytes): Encryption key

    Returns:
        str: Decrypted data
    """
    try:
        # Create Fernet cipher
        cipher = Fernet(base64.urlsafe_b64encode(key))
        
        # Decrypt data
        decrypted_bytes = cipher.decrypt(encrypted_data.encode('utf-8'))
        
        # Return as string
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt data: {str(e)}")


def generate_hmac(data: str, key: str, algorithm: str = 'sha256') -> str:
    """
    Generate an HMAC for data integrity and authentication.

    Args:
        data (str): Data to generate HMAC for
        key (str): Secret key for HMAC
        algorithm (str): Hash algorithm to use (default: 'sha256')

    Returns:
        str: HMAC digest as hexadecimal string
    """
    # Convert inputs to bytes
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')
    
    # Create HMAC
    if algorithm == 'sha256':
        mac = hmac.new(key_bytes, data_bytes, hashlib.sha256)
    elif algorithm == 'sha512':
        mac = hmac.new(key_bytes, data_bytes, hashlib.sha512)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    # Return digest as hex
    return mac.hexdigest()


def verify_hmac(data: str, signature: str, key: str, algorithm: str = 'sha256') -> bool:
    """
    Verify an HMAC signature.

    Args:
        data (str): Data to verify
        signature (str): HMAC signature to check
        key (str): Secret key for HMAC
        algorithm (str): Hash algorithm used (default: 'sha256')

    Returns:
        bool: True if the signature is valid
    """
    # Generate HMAC
    expected = generate_hmac(data, key, algorithm)
    
    # Compare signatures in constant time
    return hmac.compare_digest(expected, signature)


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        input_str (str): Input string to sanitize

    Returns:
        str: Sanitized string
    """
    # Remove common HTML/JavaScript injections
    sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
    
    # Remove potential SQL injection characters
    sanitized = sanitized.replace("'", '').replace('"', '').replace(';', '')
    
    return sanitized


def create_rate_limiter(max_calls: int, time_window: int = 60):
    """
    Create a rate limiter function.

    Args:
        max_calls (int): Maximum number of calls allowed in the time window
        time_window (int): Time window in seconds (default: 60)

    Returns:
        function: Rate limiter function that takes a key and returns (allowed, remaining, reset_time)
    """
    # Store call history as {key: [(timestamp, count), ...]}
    call_history = {}
    
    def rate_limit(key: str) -> Tuple[bool, int, int]:
        """
        Check if a call is allowed under the rate limit.

        Args:
            key (str): Identifier for the caller (e.g., user ID, IP address)

        Returns:
            Tuple[bool, int, int]: (allowed, remaining_calls, seconds_to_reset)
        """
        current_time = time.time()
        
        # Clean up expired entries
        if key in call_history:
            call_history[key] = [
                (ts, count) for ts, count in call_history[key] 
                if current_time - ts < time_window
            ]
        else:
            call_history[key] = []
        
        # Count recent calls
        recent_calls = sum(count for _, count in call_history[key])
        
        # Check if limit is reached
        if recent_calls >= max_calls:
            # Find time until oldest entry expires
            if call_history[key]:
                oldest_timestamp = min(ts for ts, _ in call_history[key])
                reset_time = int(oldest_timestamp + time_window - current_time)
            else:
                reset_time = time_window
                
            return False, 0, reset_time
        
        # Update call history
        call_history[key].append((current_time, 1))
        
        # Calculate remaining calls
        remaining = max_calls - recent_calls - 1
        
        # Calculate reset time for the current window
        reset_time = time_window
        
        return True, remaining, reset_time
    
    return rate_limit


def create_token_bucket_limiter(capacity: int, refill_rate: float, refill_interval: int = 1):
    """
    Create a token bucket rate limiter.

    Args:
        capacity (int): Maximum bucket capacity
        refill_rate (float): Tokens to add per refill_interval
        refill_interval (int): Interval in seconds between refills (default: 1)

    Returns:
        function: Rate limiter function that takes a key and token cost and returns (allowed, tokens_left)
    """
    # Store buckets as {key: (tokens, last_refill_time)}
    buckets = {}
    
    def consume(key: str, tokens: int = 1) -> Tuple[bool, float]:
        """
        Consume tokens from the bucket.

        Args:
            key (str): Identifier for the caller
            tokens (int): Number of tokens to consume (default: 1)

        Returns:
            Tuple[bool, float]: (allowed, tokens_left)
        """
        current_time = time.time()
        
        # Initialize bucket if it doesn't exist
        if key not in buckets:
            buckets[key] = (capacity, current_time)
        
        # Get current state
        current_tokens, last_refill = buckets[key]
        
        # Calculate time since last refill
        elapsed = current_time - last_refill
        
        # Refill tokens based on elapsed time
        periods = elapsed / refill_interval
        refill = periods * refill_rate
        
        # Update tokens (not exceeding capacity)
        current_tokens = min(capacity, current_tokens + refill)
        
        # Check if we have enough tokens
        if current_tokens < tokens:
            return False, current_tokens
        
        # Consume tokens
        current_tokens -= tokens
        
        # Update bucket
        buckets[key] = (current_tokens, current_time)
        
        return True, current_tokens
    
    return consume


def generate_timed_token(user_id: str, secret_key: str, expiry: int = 3600) -> str:
    """
    Generate a secure, time-limited token.

    Args:
        user_id (str): User identifier to include in the token
        secret_key (str): Secret key for signing
        expiry (int): Token validity period in seconds (default: 3600)

    Returns:
        str: Secure token
    """
    # Calculate expiry timestamp
    expiry_time = int(time.time()) + expiry
    
    # Create payload
    payload = f"{user_id}:{expiry_time}"
    
    # Generate signature
    signature = generate_hmac(payload, secret_key)
    
    # Combine payload and signature
    token = f"{payload}:{signature}"
    
    # Encode as URL-safe base64
    return base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')


def verify_timed_token(token: str, secret_key: str) -> Tuple[bool, Optional[str]]:
    """
    Verify a secure, time-limited token.

    Args:
        token (str): Token to verify
        secret_key (str): Secret key for verification

    Returns:
        Tuple[bool, Optional[str]]: (valid, user_id)
    """
    try:
        # Decode from URL-safe base64
        decoded = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
        
        # Split into parts
        parts = decoded.split(':')
        if len(parts) != 3:
            return False, None
        
        user_id, expiry_time, signature = parts
        
        # Check expiry
        if int(time.time()) > int(expiry_time):
            return False, None
        
        # Verify signature
        payload = f"{user_id}:{expiry_time}"
        if not verify_hmac(payload, signature, secret_key):
            return False, None
        
        return True, user_id
    
    except Exception:
        return False, None
