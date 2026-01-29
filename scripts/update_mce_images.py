#!/usr/bin/env python

"""
Copyright 2026 Red Hat, Inc.

usage: update_mce_images.py [-h] (-f FILE | -u URL) [-m MCE_VERSION] [-o OVERRIDES] [-r] -v VALUES_FILE

Extract images from an MCE image manifest and update MCE Helm chart values

options:
  -h, --help            show this help message and exit
  -f, --file FILE       Path to MCE image manifest JSON file
  -u, --url URL         URL to MCE image manifest JSON
  -m, --mce-version MCE_VERSION
                        MCE operator version
  -o, --overrides OVERRIDES
                        Path to overrides config file
  -r, --replace-images  Replace operand images instead of merging
  -v, --values-file VALUES_FILE
                        Helm values file to create or update
"""

import argparse
import json
import os
import sys
import requests
import yaml

def parse_arguments():
  """
  Parse command line arguments

  Returns: Dictionary of argument values
  """

  parser = argparse.ArgumentParser(description='Extract images from an MCE image manifest and update MCE Helm chart values')
  manifest_arg = parser.add_mutually_exclusive_group(required=True)
  manifest_arg.add_argument('-f', '--file', help='Path to MCE image manifest JSON file')
  manifest_arg.add_argument('-u', '--url', help='URL to MCE image manifest JSON')
  parser.add_argument('-m', '--mce-version', default='2.10.0', help='MCE operator version')
  parser.add_argument('-o', '--overrides', help='Path to overrides config file')
  parser.add_argument('-r', '--replace-images', default=False, action='store_true', help='Replace operand images instead of merging')
  parser.add_argument('-v', '--values-file', required=True, help='Helm values file to create or update')

  return vars(parser.parse_args())

def read_json_file(file):
  """
  Read a JSON file

  Args:
    file (str): name of JSON file

  Returns: Dictionary representing JSON data
  """

  if not os.path.exists(file):
    print(f"File does not exist: {file}")
    sys.exit(1)

  with open(file, 'r') as json_file:
    try:
      json_data = json.load(json_file)
    except json.JSONDecodeError as e:
      print(f"Could not decode JSON: {e}")
      sys.exit(1)

    json_file.close()

  return json_data

def read_json_url(url):
  """
  Read a JSON URL

  Args:
    url (str): URL of JSON file

  Returns: Dictionary representing JSON data
  """

  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"Could not download file: {e}")
    sys.exit(1)

  try:
    json_data = json.loads(response.text)
  except json.JSONDecodeError as e:
    print(f"Could not decode JSON: {e}")
    sys.exit(1)

  return json_data

def read_yaml_file(file):
  """
  Read a YAML file

  Args:
    file (str): name of YAML file

  Returns: Dictionary representing YAML data
  """

  if not os.path.exists(file):
    print(f"File does not exist: {file}")
    sys.exit(1)

  with open(file, 'r') as yaml_file:
    try:
      yaml_data = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
      print(f"Could not decode YAML: {e}")
      sys.exit(1)

    yaml_file.close()

  return yaml_data

def merge_manifest_into_values(manifest, values, overrides, replace_images, operator_version):
  """
  Merge image manifest into chart values

  Args:
    manifest (dict): image manifest data
    values (dict): chart values
    overrides (dict): registry and image overrides
    replace_images (bool): replace images instead of merging
    operator_version (str): MCE operator version

  Returns: Dictionary containing merged values
  """

  if replace_images:
    values['operand_images'] = {}

  values['operator_version'] = operator_version

  for image in manifest:
    if 'image_overrides' in overrides and image['image-key'] in overrides['image_overrides']:
      image_ref = overrides['image_overrides'][image['image-key']]
    elif 'registry_overrides' in overrides and image['image-remote'] in overrides['registry_overrides']:
      image_ref = "{}/{}@{}".format(overrides['registry_overrides'][image['image-remote']], image['image-name'], image['image-digest'])
    else:
      image_ref = "{}/{}@{}".format(image['image-remote'], image['image-name'], image['image-digest'])

    if image['image-key'] == "backplane_operator":
      values['operator_image'] = image_ref

    values['operand_images'][image['image-key']] = image_ref

  return values

def write_yaml_file(file, data):
  """
  Write a YAML file

  Args:
    file (str): name of YAML file
  """

  with open(file, 'w') as yaml_file:
    yaml.dump(data, yaml_file, sort_keys=True)
    yaml_file.close()

def main():
  """
  main
  """

  manifest = {}
  overrides = {}
  values = {}

  default_values = {
    "components": {
      "assisted_service": False,
      "cluster_api": False,
      "cluster_api_provider_metal3": False,
      "cluster_api_provider_openshift_assisted": False,
      "cluster_lifecycle": False,
      "cluster_manager": True,
      "cluster_proxy_addon": False,
      "console_mce": False,
      "discovery": False,
      "hive": False,
      "hypershift": False,
      "hypershift_local_hosting": False,
      "image_based_install_operator_preview": False,
      "local_cluster": False,
      "managedserviceaccount": False,
      "server_foundation": False
    },
    "external_components": [],
    "monitoring": True,
    "operand_images": {
    },
    "pull_secret": "e30K"
    }

  args = parse_arguments()

  if args['overrides']:
    overrides = read_json_file(args['overrides'])

  if args['file']:
    manifest = read_json_file(args['file'])
  else:
    manifest = read_json_url(args['url'])

  if os.path.exists(args['values_file']):
    values = read_yaml_file(args['values_file'])
  else:
    values = default_values

  updated_values = merge_manifest_into_values(manifest, values, overrides, args['replace_images'], args['mce_version'])
  write_yaml_file(args['values_file'], updated_values)

  sys.exit(0)

if __name__ == "__main__":
  main()
