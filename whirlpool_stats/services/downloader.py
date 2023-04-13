'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class allowing to download the latest snapshots of Whirpool's transaction graph.
'''
import sys
import getopt
import requests
from random import randint
from whirlpool_stats.utils.constants import *


class Downloader(object):

  def __init__(self):
    '''
    Constructor
    '''
    self.snapshots_dir = ''
    self.denoms = []
    self.socks5 = None


  def download(self, snapshots_dir, denoms=ALL_DENOMS, socks5=None):
    '''
    Downloads a list of snapshots
    Parameters:
      snapshots_dir = path of the directory that will store snapshot files
      denoms        = list of codes identifying mix denominations of interest
      socks5        = url of the socks5 proxy to use (or None)
    '''
    self.snapshots_dir = snapshots_dir
    self.denoms = denoms
    self.socks5 = socks5

    # Creates a requests session
    session = requests.session()
    session.proxies = {}
  
    # Sets the tor proxy if needed
    if self.socks5 is not None:
      session.proxies['http'] = 'socks5h://' + self.socks5
      session.proxies['https'] = 'socks5h://' + self.socks5
  
    # Downloads snaphshot files for the requested denoms
    for d in self.denoms:
      print('Start download of snapshot for %s denomination' % d)
      # Iterates over the 3 files composing the snapshot for a given denom 
      for f in FILENAME_TEMPLATES:
        filename = '%s_%s.csv' % (f, d)
        url = '%s/%s?rand=%d' % (BASE_URL_SNAPSHOTS, filename, randint(1, 10000))
        snapshot_path = '%s/%s' % (self.snapshots_dir, filename)
        # Downloads the file and save to disk
        r = session.get(url)
        with open(snapshot_path, 'wb') as tmp_file:
          tmp_file.write(r.content)
          print('  %s downloaded' % filename)
      print('Download complete\n')


  def download_txids(self, snapshots_dir, socks5=None):
    '''
    Downloads the list of txids for mixes and Tx0s of all pools
    Parameters:
      snapshots_dir = path of the directory that will store snapshot files
      socks5        = url of the socks5 proxy to use (or None)
    '''
    self.snapshots_dir = snapshots_dir
    self.socks5 = socks5

    # Creates a requests session
    session = requests.session()
    session.proxies = {}
  
    # Sets the tor proxy if needed
    if self.socks5 is not None:
      session.proxies['http'] = 'socks5h://' + self.socks5
      session.proxies['https'] = 'socks5h://' + self.socks5

    # Downloads txids files for all denoms
    for d in ALL_DENOMS:
      print('Start download of txids for %s denomination' % d)
      # Iterates over the 3 files composing the snapshot for a given denom 
      for f in TXIDS_FILENAME_TEMPLATES:
        filename = '%s_%s.csv' % (f, d)
        url = '%s/%s?rand=%d' % (BASE_URL_SNAPSHOTS, filename, randint(1, 10000))
        snapshot_path = '%s/%s' % (self.snapshots_dir, filename)
        # Downloads the file and save to disk
        r = session.get(url)
        with open(snapshot_path, 'wb') as tmp_file:
          tmp_file.write(r.content)
          print('  %s downloaded' % filename)
      print('Download complete\n')


def main(snapshots_dir, denoms=ALL_DENOMS, socks5=None):
  '''
  Main function
  Parameters:
    snapshots_dir = path of the directory that will store snapshot files
    denoms        = list of codes identifying mix denominations of interest
    socks5        = url of the socks5 proxy to use (or None)
  '''
  downloader = Downloader()
  downloader.download(snapshots_dir, denoms, socks5)


def usage():
  '''
  Usage message for this module
  '''
  sys.stdout.write('python download_snapshot.py [--target_dir=/tmp] [--denoms=05,005,001,0001] [--socks5=localhost:9050]\n')
  sys.stdout.write('\n\n[-t OR --target_dir] = Path of the directory that will store the snapshot files.')
  sys.stdout.write('\n\n[-d OR --denoms] = List of codes identifying the mix denominations of interest.')
  sys.stdout.write('\n    Available denomination codes are :')
  sys.stdout.write('\n    05 (O.5 BTC pools')
  sys.stdout.write('\n    005 (O.05 BTC pools')
  sys.stdout.write('\n    001 (O.01 BTC pools')
  sys.stdout.write('\n    0001 (O.001 BTC pools')
  sys.stdout.write('\n\n[-s OR --socks5] = Url of the socks5 proxy to use for downloading the snapshot.')
  sys.stdout.flush()


if __name__ == '__main__':
  # Initializes the parameters
  target_dir = '/tmp'
  denoms = ALL_DENOMS
  socks5 = None
  argv = sys.argv[1:]

  # Processes the command line arguments
  try:
    opts, args = getopt.getopt(
      argv,
      'ht:d:s:',
      ['help', 'target_dir', 'denoms', 'socks5']
    )
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('-t', '--target_dir'):
      target_dir = arg
    elif opt in ('-d', '--denoms'):
      denoms = [d.strip() for d in arg.split(',')]
    elif opt in ('-s', '--socks5'):
      socks5 = arg

  # Processes computations
  main(target_dir, denoms, socks5)
