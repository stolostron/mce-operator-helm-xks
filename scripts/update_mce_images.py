#!/usr/bin/env python

import yaml
import json
import os
import pathlib
import argparse
import tempfile
from podman import PodmanClient

def parse_args():
  parser = argparse.ArgumentParser(description='Extract images from an MCE operator bundle and Update MCE Helm chart values')
  parser.add_argument('-b', '--bundle-image', required=true, help='Registry location of an MCE operator bundle')
  parser.add_argument('-f', '--values-file', required=true, help='Helm values file to create or update')

  return parser.parse_args()

def extract_images(bundle_image):
  with tempfile.TemporaryDirectory() as staging_dir:
    with open(os.path.join(staging_dir, 'bundle.tar', 'wb') as bundle_file:
      with PodmanClient() as client:
        image = client.images.pull(bundle_image)
        bundle_file.write(client.images.save(image))
      bundle_file.close()


  extractLayers()
  readManifests()

def main():
  values = {}

  args = parse_args()

  images = extract_images(args.bundle_image)

  if os.path.exists(args.values_file):
    with open(args.values_file, 'r') as yaml_file:
    values = yaml.safe_load(file)
    yaml_file.close()



