# Performance CLI Commands

This section provides detailed documentation for the Smart Steps AI performance command-line interface.

## Overview

The performance commands provide tools for optimizing and monitoring system performance.

## Command Structure

```
smart-steps-ai performance [COMMAND] [OPTIONS]
```

## Available Commands

### optimize

Optimize system performance.

```
smart-steps-ai performance optimize [OPTIONS]
```

#### Options

- `--clear-cache, -c`: Clear all caches
- `--compress-vectors, -v`: Compress vector embeddings
- `--optimize-memory, -m`: Optimize memory usage
- `--report, -r PATH`: Save optimization report to file

#### Examples

```bash
# Run all optimizations
smart-steps-ai performance optimize

# Clear caches only
smart-steps-ai performance optimize --clear-cache

# Compress vectors and save report
smart-steps-ai performance optimize --compress-vectors --report "optimization_report.json"
```

### status

Display current performance status.

```
smart-steps-ai performance status [OPTIONS]
```

#### Options

- `--detailed, -d`: Show detailed performance metrics
- `--watch, -w`: Watch performance metrics in real time
- `--interval, -i INTEGER`: Update interval in seconds (for watch mode)

#### Examples

```bash
# Show basic status
smart-steps-ai performance status

# Show detailed status
smart-steps-ai performance status --detailed

# Watch status in real time
smart-steps-ai performance status --watch

# Watch with 5-second intervals
smart-steps-ai performance status --watch --interval 5
```

### configure

Configure performance settings.

```
smart-steps-ai performance configure [OPTIONS]
```

#### Options

- `--cache-size, -c INTEGER`: Maximum memory cache size
- `--disk-cache-size, -d INTEGER`: Maximum disk cache size (MB)
- `--compression, -v BOOLEAN`: Enable vector compression
- `--batch-size, -b INTEGER`: Batch processing size

#### Examples

```bash
# Configure memory cache size
smart-steps-ai performance configure --cache-size 2000

# Configure disk cache size
smart-steps-ai performance configure --disk-cache-size 500

# Enable vector compression
smart-steps-ai performance configure --compression true

# Configure batch size
smart-steps-ai performance configure --batch-size 20
```

### reset

Reset all performance metrics.

```
smart-steps-ai performance reset [OPTIONS]
```

#### Options

- `--confirm, -c`: Confirm reset without prompt

#### Examples

```bash
# Reset with prompt
smart-steps-ai performance reset

# Reset without prompt
smart-steps-ai performance reset --confirm
```

## Performance Report

The performance report from the `optimize` and `status` commands includes the following metrics:

### Operation Performance

| Operation          | Avg Time (ms) | Min Time (ms) | Max Time (ms) | Count |
|-------------------|---------------|---------------|---------------|-------|
| embed_text        | 0.50          | 0.25          | 1.20          | 150   |
| calculate_similarity | 0.20        | 0.10          | 0.50          | 1250  |
| search            | 10.50         | 5.30          | 25.40         | 45    |
| retrieve_context  | 100.20        | 80.50         | 150.30        | 30    |

### Memory Usage

| Metric            | Value         |
|-------------------|---------------|
| Total Objects     | 12500         |
| Total Size (MB)   | 850.25        |

### Cache Status

| Cache Type        | Items         | Hit Rate      |
|-------------------|---------------|---------------|
| Memory Cache      | 1250          | 85%           |
| Disk Cache        | 3500          | 92%           |

## Best Practices

1. **Regular Optimization**: Run the `optimize` command regularly for long-running applications:

```bash
# In a cron job or scheduled task
smart-steps-ai performance optimize
```

2. **Monitor Performance**: Use the `status` command to monitor performance:

```bash
# Check performance before and after optimizations
smart-steps-ai performance status --detailed
```

3. **Adjust Cache Sizes**: Configure cache sizes based on available resources:

```bash
# For systems with more memory
smart-steps-ai performance configure --cache-size 5000 --disk-cache-size 1000
```

4. **Enable Compression**: Enable vector compression for memory-constrained environments:

```bash
smart-steps-ai performance configure --compression true
```

5. **Adjust Batch Size**: Optimize batch size for specific workloads:

```bash
# For CPU-intensive operations
smart-steps-ai performance configure --batch-size 10

# For I/O-intensive operations
smart-steps-ai performance configure --batch-size 50
```

## Troubleshooting

### Command Not Found

If you get a "command not found" error:

```bash
# Verify that the package is installed
pip list | grep smart-steps-ai

# Verify that the package is in your PATH
which smart-steps-ai
```

### High Memory Usage

If you're experiencing high memory usage:

```bash
# Check memory usage
smart-steps-ai performance status --detailed

# Optimize memory
smart-steps-ai performance optimize --optimize-memory

# Reduce cache sizes
smart-steps-ai performance configure --cache-size 1000 --disk-cache-size 250
```

### Slow Performance

If you're experiencing slow performance:

```bash
# Check performance metrics
smart-steps-ai performance status --detailed

# Optimize all components
smart-steps-ai performance optimize

# Adjust batch size
smart-steps-ai performance configure --batch-size <value>
```
