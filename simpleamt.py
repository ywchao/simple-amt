import argparse, json

from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import *
from jinja2 import Environment, FileSystemLoader


"""
A bunch of free functions that we use in all scripts.
"""


def get_jinja_env(config):
  """
  Get a jinja2 Environment object that we can use to find templates.
  """
  return Environment(loader=FileSystemLoader(config['template_directories']))


def json_file(filename):
  with open(filename, 'r') as f:
    return json.load(f)


def get_parent_parser():
  """
  Get an argparse parser with arguments that are always needed
  """
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--prod', action='store_false', dest='sandbox',
                      default=True,
                      help="Whether to run on the production AMT site.")
  parser.add_argument('--hit_ids_file')
  parser.add_argument('--reject_file')
  parser.add_argument('--reject_only', default=False)
  parser.add_argument('--auto_mode', default=False)
  parser.add_argument('--config', default='config.json',
                      type=json_file)
  return parser


def get_mturk_connection_from_args(args):
  """
  Utility method to get an MTurkConnection from argparse args.
  """
  aws_access_key = args.config.get('aws_access_key')
  aws_secret_key = args.config.get('aws_secret_key')
  return get_mturk_connection(sandbox=args.sandbox,
                              aws_access_key=aws_access_key,
                              aws_secret_key=aws_secret_key)


def get_mturk_connection(sandbox=True, aws_access_key=None,
                         aws_secret_key=None):
  """
  Get a boto mturk connection. This is a thin wrapper over the
  MTurkConnection constructor; the only difference is a boolean
  flag to indicate sandbox or not.
  """
  kwargs = {}
  if aws_access_key is not None:
    kwargs['aws_access_key_id'] = aws_access_key
  if aws_secret_key is not None:
    kwargs['aws_secret_access_key'] = aws_secret_key

  if sandbox:
    host = 'mechanicalturk.sandbox.amazonaws.com'
  else:
    host='mechanicalturk.amazonaws.com'
  return MTurkConnection(host=host, **kwargs)


def setup_qualifications(hit_properties):
  """
  Replace some of the human-readable keys from the raw HIT properties
  JSON data structure with boto-specific objects.
  """
  qual = Qualifications()
  if 'country' in hit_properties:
    qual.add(LocaleRequirement('EqualTo',
      hit_properties['country']))
    del hit_properties['country']

  if 'hits_approved' in hit_properties:
    qual.add(NumberHitsApprovedRequirement('GreaterThan',
      hit_properties['hits_approved']))
    del hit_properties['hits_approved']

  if 'percent_approved' in hit_properties:
    qual.add(PercentAssignmentsApprovedRequirement('GreaterThan',
      hit_properties['percent_approved']))
    del hit_properties['percent_approved']

  hit_properties['qualifications'] = qual
