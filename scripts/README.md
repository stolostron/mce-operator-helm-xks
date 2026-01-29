# Overview

This directory contains utility scripts and configuration files for managing the MCE (Multicluster Engine) operator and Helm charts.

## Requirements

- Python 3.x
- Python packages listed in `requirements.txt`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Scripts

### MCE Image Update Script

**File:** `update_mce_images.py`

A Python script that extracts container images from an MCE image manifest and updates Helm chart values files with the appropriate image references.

#### Purpose

The script automates the process of:
- Reading MCE image manifests (from local files or URLs)
- Applying registry and image overrides
- Updating or creating Helm values files with the correct image references
- Managing operator and operand image configurations

#### Usage

```bash
./update_mce_images.py [OPTIONS] -v VALUES_FILE
```

#### Options

| Option | Description | Required |
|--------|-------------|----------|
| `-f, --file FILE` | Path to MCE image manifest JSON file | One of `-f` or `-u` |
| `-u, --url URL` | URL to MCE image manifest JSON | One of `-f` or `-u` |
| `-m, --mce-version MCE_VERSION` | MCE operator version (default: 2.10.0) | No |
| `-o, --overrides OVERRIDES` | Path to overrides config file | No |
| `-r, --replace-images` | Replace operand images instead of merging | No |
| `-v, --values-file VALUES_FILE` | Helm values file to create or update | Yes |

#### Examples

**Update values from a local manifest file:**
```bash
./update_mce_images.py -f ~/manifest-2.11.0.json -v ../charts/multicluster-engine/values.yaml
```

**Download manifest from URL and apply overrides:**
```bash
./update_mce_images.py \
  -u https://github.com/stolostron/mce-operator-bundle/blob/backplane-2.11/extras/2.11.0.json \
  -o overrides.downstream.json \
  -m 2.11.0 \
  -v ../charts/multicluster-engine/values.yaml
```

**Replace all images instead of merging:**
```bash
./update_mce_images.py \
  -f ~/manifest-2.11.0.json \
  -o overrides.downstream.json \
  -r \
  -v ../charts/multicluster-engine/values.yaml
```

#### How It Works

1. **Reads Image Manifest**: Loads the MCE image manifest from a file or URL
2. **Loads Overrides**: If specified, reads registry and image override configurations
3. **Reads/Creates Values File**: Loads existing Helm values file or creates a new one with defaults
4. **Applies Transformations**: For each image in the manifest:
   - Checks for specific image overrides
   - Applies registry overrides if no image override exists
   - Uses original image reference if no overrides apply
5. **Updates Values**: 
   - Sets `operator_version` to the specified MCE version
   - Sets `operator_image` for the backplane_operator
   - Adds/updates all images in the `operand_images` section
6. **Writes Output**: Saves the updated values to the specified YAML file

#### Default Values

When creating a new values file, the script initializes it with:
- Component flags (most disabled by default, only `cluster_manager: True`)
- Empty operand images dictionary
- Monitoring enabled
- Base64-encoded empty pull secret

#### Configuration File

**File:** `overrides.downstream.json`

This configuration file defines registry and image overrides for downstream builds.

#### Purpose

This file allows you to:
- Redirect images from upstream registries to downstream/internal registries
- Override specific images with custom references
- Support air-gapped or disconnected deployments

**Structure:**

```json
{
  "registry_overrides": {
    "<source-registry>": "<target-registry>"
  },
  "image_overrides": {
    "<image-key>": "<full-image-reference>"
  }
}
```

#### Configuration Details

**`registry_overrides`**: Maps source registry domains to target registries. When an image uses a source registry, it will be replaced with the target registry while preserving the image name and digest.

Current configuration redirects:
- `registry.redhat.io/multicluster-engine` → `quay.io:443/acm-d`
- `registry.redhat.io/openshift4` → `quay.io:443/acm-d`
- `registry.stage.redhat.io/openshift4` → `quay.io:443/acm-d`

**`image_overrides`**: Provides explicit image references for specific image keys, taking precedence over registry overrides.

**Example Override Scenarios:**

**Registry Override Applied:**
```
Source: registry.redhat.io/multicluster-engine/console-mce@sha256:abc123
Result: quay.io:443/acm-d/console-mce@sha256:abc123
```

**Image Override (if configured):**
```json
{
  "image_overrides": {
    "console_mce": "custom.registry.io/custom-console:v2.11"
  }
}
```
Result: Uses `custom.registry.io/custom-console:v2.11` regardless of source

#### Typical Workflow

1. Obtain the MCE image manifest for your target version
2. Configure `overrides.downstream.json` for your environment
3. Run the update script to generate or update your Helm values file
4. Use the generated values file with your Helm deployment

```bash
# Example complete workflow
./update_mce_images.py \
  -u https://github.com/stolostron/mce-operator-bundle/blob/backplane-2.11/extras/2.11.0.json \
  -m 2.11.0 \
  -o overrides.downstream.json \
  -v ../charts/multicluster-engine/values.yaml
```

#### Notes

- The script preserves existing values when updating, merging new images by default
- Use `-r/--replace-images` to completely replace the operand images section
- Registry overrides are applied at the domain level, preserving image paths and digests
- Image overrides take precedence over registry overrides
- The script always sorts YAML output keys alphabetically for consistency

## License

Copyright 2026 Red Hat, Inc.
