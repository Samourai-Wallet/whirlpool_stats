'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

Python script allowing to download the latest snapshot of Whirpool's transaction graph.
'''
import sys
import getopt
import requests
from whirlpool_stats.whirlpool_stats.constants import *



def main(target_dir, denoms, socks5=None):
  '''
  Main function
  Parameters:
    target_dir = path of the directory that will store the snapshot files
    denoms     = list of codes identifying the mix denominations of interest
    socks5     = url of the socks5 proxy to use (or None)
  '''
  # Create a requests session
  session = requests.session()
  session.proxies = {}

  # Set the tor proxy if needed
  if socks5 is not None:
    session.proxies['http'] = 'socks5h://' + socks5
    session.proxies['https'] = 'socks5h://' + socks5

  # Download snaphshot files for the requested denoms
  for d in denoms:
    print('Start download of snapshot for %s denomination' % d)
    # Iterate over the 3 files composing the snapshot for a given denom 
    for f in FILENAME_TEMPLATES:
      filename = '%s_%s.csv' % (f, d)
      url = '%s/%s' % (BASE_URL_SNAPSHOTS, filename)
      target_path = '%s/%s' % (target_dir, filename)
      # Download the file and save to disk
      r = session.get(url)
      with open(target_path, 'wb') as tmp_file:
        tmp_file.write(r.content)
        print('  %s downloaded' % filename)
    print('Download complete\n')


def usage():
  '''
  Usage message for this module
  '''
  sys.stdout.write('python download_snapshot.py [--target_dir=/tmp] [--denoms=05,005,001] [--socks5=localhost:9050]\n')
  sys.stdout.write('\n\n[-t OR --target_dir] = Path of the directory that will store the snapshot files.')
  sys.stdout.write('\n\n[-d OR --denoms] = List of codes identifying the mix denominations of interest.')
  sys.stdout.write('\n    Available denomination codes are :')
  sys.stdout.write('\n    05 (O.5 BTC pools')
  sys.stdout.write('\n    005 (O.05 BTC pools')
  sys.stdout.write('\n    001 (O.01 BTC pools')
  sys.stdout.write('\n\n[-s OR --socks5] = Url of the socks5 proxy to use for downloading the snapshot.')
  sys.stdout.flush()


if __name__ == '__main__':
  # Initializes parameters
  target_dir = '/tmp'
  denoms = ['05', '005', '001']
  socks5 = None
  argv = sys.argv[1:]

  # Processes arguments
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
