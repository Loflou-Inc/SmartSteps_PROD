# Smart Steps Security Configuration Guide

## Introduction

This guide provides detailed instructions for configuring security settings in the Smart Steps AI Professional Persona module. It covers authentication, authorization, encryption, logging, and compliance configurations for different deployment environments.

## Configuration File Structure

The Smart Steps security configuration uses a hierarchical structure in JSON or YAML format:

```yaml
security:
  authentication:
    # Authentication settings
  authorization:
    # Authorization settings
  encryption:
    # Encryption settings
  logging:
    # Security logging settings
  compliance:
    # Compliance settings
  monitoring:
    # Security monitoring settings
```

The configuration file is located at `config/security.yaml` by default.

## Authentication Configuration

### Basic Authentication Settings

```yaml
security:
  authentication:
    password_policy:
      min_length: 12
      require_uppercase: true
      require_lowercase: true
      require_numbers: true
      require_special_chars: true
      max_age_days: 90
      prevent_reuse: 10  # Remember last 10 passwords
    
    session:
      timeout_minutes: 30
      max_concurrent_sessions: 3
      refresh_token_validity_days: 7
      access_token_validity_minutes: 60
```

### Multi-Factor Authentication

```yaml
security:
  authentication:
    mfa:
      enabled: true
      required_for_roles: ["admin", "supervisor"]
      recommended_for_roles: ["therapist", "facilitator"]
      methods:
        - type: "totp"
          enabled: true
          issuer: "Smart Steps"
        - type: "email"
          enabled: true
          expiry_minutes: 15
        - type: "sms"
          enabled: false  # Enable if SMS provider is configured
      grace_period_days: 7  # Time to set up MFA after account creation
      remember_device_days: 30
```

### Authentication Providers

```yaml
security:
  authentication:
    providers:
      local:
        enabled: true
        primary: true
      oauth:
        enabled: false
        providers:
          google:
            enabled: false
            client_id: ""
            client_secret: ""
            allowed_domains: []
          microsoft:
            enabled: false
            client_id: ""
            client_secret: ""
            tenant_id: ""
      saml:
        enabled: false
        metadata_url: ""
        entity_id: ""
```

## Authorization Configuration

### Role Definitions

```yaml
security:
  authorization:
    roles:
      admin:
        description: "System administrator with full access"
        permissions: ["*"]
      supervisor:
        description: "Supervises therapists and reviews sessions"
        permissions: [
          "session:read", "session:list", 
          "client:read", "client:list",
          "report:read", "report:create", 
          "therapist:read", "therapist:list"
        ]
      therapist:
        description: "Conducts therapy sessions"
        permissions: [
          "session:read", "session:create", "session:update", 
          "client:read", "client:create", "client:update",
          "report:read", "report:create"
        ]
```

### Permission Sets

```yaml
security:
  authorization:
    permission_sets:
      session_management:
        description: "Session management permissions"
        permissions: [
          "session:create", "session:read", "session:update", 
          "session:delete", "session:list"
        ]
      client_management:
        description: "Client management permissions"
        permissions: [
          "client:create", "client:read", "client:update", 
          "client:delete", "client:list"
        ]
      reporting:
        description: "Reporting permissions"
        permissions: [
          "report:create", "report:read", "report:export", 
          "report:share", "report:delete"
        ]
```

### Custom Role Assignment

```yaml
security:
  authorization:
    custom_roles:
      research_therapist:
        description: "Therapist with research capabilities"
        inherit_from: ["therapist"]
        additional_permissions: [
          "analytics:read", "research:access", "anonymized_data:export"
        ]
      limited_supervisor:
        description: "Supervisor with limited access"
        inherit_from: ["supervisor"]
        excluded_permissions: ["therapist:list"]
```

## Encryption Configuration

### Data Encryption

```yaml
security:
  encryption:
    algorithm: "AES-256-GCM"
    key_management:
      key_rotation_days: 90
      minimum_key_versions: 3  # Keep at least 3 previous key versions
      auto_rotation: true
    
    encrypted_fields:
      client:
        - "full_name"
        - "date_of_birth"
        - "address"
        - "contact_information"
        - "medical_record_number"
      session:
        - "notes"
        - "assessment"
        - "diagnosis"
      message:
        - "content"
```

### Transport Layer Security

```yaml
security:
  encryption:
    tls:
      minimum_version: "TLS1.3"
      preferred_cipher_suites: [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256"
      ]
      hsts_enabled: true
      hsts_max_age_seconds: 31536000  # 1 year
      certificate_path: "/etc/ssl/certs/smartsteps.crt"
      private_key_path: "/etc/ssl/private/smartsteps.key"
```

### Database Encryption

```yaml
security:
  encryption:
    database:
      transparent_data_encryption: true
      connection_encryption: true
      connection_ssl_mode: "verify-full"
      ca_certificate_path: "/etc/ssl/certs/db-ca.crt"
```

## Logging and Monitoring

### Security Logging

```yaml
security:
  logging:
    enabled: true
    level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    retention_days: 365  # Log retention period
    
    log_events:
      authentication:
        successes: true
        failures: true
      authorization:
        successes: true
        failures: true
      data_access:
        reads: true
        writes: true
        exports: true
      configuration:
        changes: true
      api:
        requests: true
```

### Log Formats and Storage

```yaml
security:
  logging:
    format: "json"  # text, json, cef
    outputs:
      file:
        enabled: true
        path: "/var/log/smartsteps/security.log"
        rotation:
          max_size_mb: 100
          backups: 10
      syslog:
        enabled: false
        host: ""
        port: 514
        protocol: "TCP"
      api:
        enabled: false
        endpoint: ""
        auth_token: ""
```

### Security Monitoring

```yaml
security:
  monitoring:
    alerting:
      enabled: true
      channels:
        email:
          enabled: true
          recipients: ["security@smartsteps.example.com"]
        webhook:
          enabled: false
          url: ""
        sms:
          enabled: false
          recipients: []
    
    alert_rules:
      authentication_failures:
        threshold: 5  # Alert after 5 failures
        time_window_minutes: 10
        cooldown_minutes: 60
      suspicious_access:
        enabled: true
        sensitivity: "medium"  # low, medium, high
      data_export:
        volume_threshold_mb: 50
        record_threshold: 1000
```

## Compliance Configuration

### HIPAA Configuration

```yaml
security:
  compliance:
    hipaa:
      enabled: true
      audit_trail:
        enabled: true
        include_phi_access: true
      emergency_access:
        enabled: true
        approval_required: true
        notify_on_use: true
      automatic_logoff:
        enabled: true
        timeout_minutes: 15
```

### GDPR Configuration

```yaml
security:
  compliance:
    gdpr:
      enabled: true
      data_protection:
        automatic_anonymization_days: 730  # 2 years
        right_to_access:
          enabled: true
          delivery_method: "encrypted_email"
        right_to_be_forgotten:
          enabled: true
          soft_delete: true  # Mark as deleted but retain for compliance
          permanent_delete_days: 90  # Permanently delete after 90 days
```

### Data Anonymization

```yaml
security:
  compliance:
    anonymization:
      profiles:
        research:
          description: "Anonymization for research purposes"
          techniques:
            - "pseudonymization"
            - "generalization"
          fields:
            client.name: "pseudonym"
            client.date_of_birth: "age_range"
            client.address: "redact"
            client.contact_information: "redact"
        analytics:
          description: "Anonymization for analytics dashboards"
          techniques:
            - "aggregation"
            - "generalization"
          fields:
            client.name: "remove"
            client.date_of_birth: "age_range"
            session.notes: "summarize"
```

## API Security

### API Authentication

```yaml
security:
  api:
    authentication:
      methods:
        jwt:
          enabled: true
          issuer: "SmartSteps"
          audience: "SmartSteps API"
          access_token_expiry_minutes: 60
          refresh_token_expiry_days: 7
        api_key:
          enabled: true
          key_prefix: "sk_ss_"
          expiration: true
          expiry_days: 90
```

### Rate Limiting

```yaml
security:
  api:
    rate_limiting:
      enabled: true
      default_limit: "100/minute"
      per_endpoint:
        "/api/auth/login": "20/minute"
        "/api/auth/password/reset": "10/hour"
      per_user:
        default: "1000/hour"
        admin: "5000/hour"
      ip_whitelist: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
```

### API Security Headers

```yaml
security:
  api:
    security_headers:
      enabled: true
      headers:
        "Content-Security-Policy": "default-src 'self'"
        "X-Content-Type-Options": "nosniff"
        "X-Frame-Options": "DENY"
        "X-XSS-Protection": "1; mode=block"
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        "Referrer-Policy": "strict-origin-when-cross-origin"
```

## Environment-Specific Configurations

### Development Environment

```yaml
security:
  environment: "development"
  authentication:
    mfa:
      enabled: false
    password_policy:
      min_length: 8
  encryption:
    use_dummy_keys: true  # Use predictable keys for development
  logging:
    level: "DEBUG"
```

### Testing Environment

```yaml
security:
  environment: "testing"
  authentication:
    mfa:
      enabled: true
      required_for_roles: ["admin"]
  encryption:
    use_dummy_keys: false
  logging:
    level: "INFO"
```

### Production Environment

```yaml
security:
  environment: "production"
  authentication:
    mfa:
      enabled: true
      required_for_roles: ["admin", "supervisor", "therapist"]
    session:
      timeout_minutes: 15
  api:
    rate_limiting:
      enabled: true
  logging:
    level: "WARNING"
    outputs:
      file:
        enabled: true
      syslog:
        enabled: true
```

## Configuration Management

### Secure Configuration Handling

The Smart Steps system includes tools for secure configuration management:

```bash
# Encrypt sensitive configuration
python -m smart_steps_ai.security.config_encrypt \
  --input config/security.yaml \
  --output config/security.enc.yaml \
  --key-path /path/to/master.key

# Decrypt configuration (in memory only)
python -m smart_steps_ai.security.config_decrypt \
  --input config/security.enc.yaml \
  --key-path /path/to/master.key
```

### Configuration Validation

```bash
# Validate configuration
python -m smart_steps_ai.security.config_validate \
  --config config/security.yaml

# Test configuration against compliance requirements
python -m smart_steps_ai.security.config_validate \
  --config config/security.yaml \
  --compliance hipaa,gdpr
```

## Configuration Templates

### Minimal Configuration Template

```yaml
security:
  environment: "production"
  authentication:
    password_policy:
      min_length: 12
      require_uppercase: true
      require_lowercase: true
      require_numbers: true
      require_special_chars: true
    mfa:
      enabled: true
      required_for_roles: ["admin"]
      methods:
        - type: "totp"
          enabled: true
  encryption:
    algorithm: "AES-256-GCM"
  logging:
    enabled: true
    level: "INFO"
```

### High-Security Template

```yaml
security:
  environment: "production"
  authentication:
    password_policy:
      min_length: 16
      require_uppercase: true
      require_lowercase: true
      require_numbers: true
      require_special_chars: true
      max_age_days: 60
      prevent_reuse: 24
    mfa:
      enabled: true
      required_for_roles: ["admin", "supervisor", "therapist", "facilitator"]
      methods:
        - type: "totp"
          enabled: true
    session:
      timeout_minutes: 15
  encryption:
    algorithm: "AES-256-GCM"
    key_management:
      key_rotation_days: 30
  logging:
    enabled: true
    level: "INFO"
    log_events:
      data_access:
        reads: true
  compliance:
    hipaa:
      enabled: true
    gdpr:
      enabled: true
```

## Security Configuration Checklist

Use this checklist to verify your security configuration:

- [ ] Strong password policy configured
- [ ] Multi-factor authentication enabled for administrative roles
- [ ] Session timeout set appropriately for environment
- [ ] Encryption configured for sensitive data fields
- [ ] TLS 1.3 enforced for all connections
- [ ] Comprehensive security logging enabled
- [ ] API security measures implemented (authentication, rate limiting)
- [ ] Necessary compliance features enabled
- [ ] Environment-specific configurations reviewed

## Troubleshooting

### Common Configuration Issues

1. **MFA Configuration Errors**
   - Symptom: Unable to complete MFA setup
   - Solution: Verify TOTP issuer is correct and timeserver is synchronized

2. **Encryption Key Issues**
   - Symptom: Decryption failures after key rotation
   - Solution: Ensure old key versions are retained in the key store

3. **Logging Configuration Issues**
   - Symptom: Missing security logs
   - Solution: Verify log path is writable and log rotation is configured properly

### Configuration Diagnostic Tool

```bash
# Run configuration diagnostics
python -m smart_steps_ai.security.config_diagnose \
  --config config/security.yaml \
  --verbose

# Test specific configuration section
python -m smart_steps_ai.security.config_diagnose \
  --config config/security.yaml \
  --section encryption
```

## Additional Resources

- Security Configuration API Documentation: `/docs/api/security-config.md`
- Security Configuration Schema: `/schemas/security-config.json`
- Example Configurations: `/examples/security/`

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-05-11 | Security Team | Initial creation |

**Review Schedule**: This document should be reviewed and updated at least quarterly or after significant security configuration changes.