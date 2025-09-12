# Migration Guide: Enhanced-Extended to Extended Format

This guide helps users transition from the `enhanced-extended` format to the updated `extended` format in Beacon. All features from `enhanced-extended` have been merged into the standard `extended` format for a more streamlined experience.

## What's Changed

- The `enhanced-extended` format has been removed
- All its features are now part of the standard `extended` format
- The command-line interface has been simplified
- The output format remains backward compatible

## Before and After

### Before (Old Command)

```bash
beaconled --format enhanced-extended --since "2w"
```

### After (New Command)

```bash
beaconled --format extended --since "2w"
```

## Key Changes

### 1. Simplified Format Selection

| Old | New |
|-----|-----|
| `--format enhanced-extended` | `--format extended` |
| `--format extended` (basic) | `--format extended` (now includes all features) |

### 2. Output Structure

The output structure remains the same, but with improved organization and additional metrics:

- Time-Based Analytics
- Team Collaboration
- Code Quality
- Risk Assessment

### 3. Backward Compatibility

All existing scripts using `--format extended` will continue to work, but with enhanced output. Scripts using `--format enhanced-extended` should be updated to use `--format extended`.

## Migration Steps

1. **Update Your Commands**
   - Replace all instances of `--format enhanced-extended` with `--format extended`
   - Remove any conditional logic that checks for `enhanced-extended` format

2. **Update Documentation**
   - Update any internal or external documentation referencing `enhanced-extended`
   - Update CI/CD pipelines and automation scripts

3. **Test Your Workflows**
   - Run your existing workflows with the new command
   - Verify that all expected metrics are present in the output
   - Update any parsing logic if needed (output format may have minor improvements)

## Example Migration

### Before

```bash
# Old command with enhanced-extended
beaconled --format enhanced-extended --since "1m" > monthly_report.txt

# Script checking for enhanced-extended
if [ "$FORMAT" = "enhanced-extended" ]; then
    # Special handling
fi
```

### After

```bash
# New command with extended
beaconled --format extended --since "1m" > monthly_report.txt

# Updated script
# No need for special handling - all features are in extended
```

## Troubleshooting

### I'm getting an error about invalid format 'enhanced-extended'

Update your command to use `--format extended` instead of `--format enhanced-extended`.

### Some metrics seem to be missing

All metrics from `enhanced-extended` are now in the standard `extended` format. If you're missing something, please check:

1. You're using the latest version of Beacon
2. Your repository has sufficient history
3. The metrics might have been renamed or reorganized

### My scripts parse the output and now they're broken

The output format has been improved but remains backward compatible. However, if you were parsing specific sections, you might need to update your parsing logic. The main changes are:

- Section headers now include emojis by default
- Some metrics might be in a different order
- Additional metrics have been added

## Need Help?

If you encounter any issues during migration, please:

1. Check the [extended format documentation](../extended-format-guide.md)
2. Review the [troubleshooting guide](../troubleshooting.md)
3. [Open an issue](https://github.com/shrwnsan/beacon-delivery-compass/issues) if you need further assistance
