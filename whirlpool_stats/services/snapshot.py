'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class storing the snapshot for a given denom
'''
import csv
from collections import defaultdict
from whirlpool_stats.utils.constants import *


class Snapshot(object):

  def __init__(self, snapshots_dir):
    '''
    Constructor
    Parameters:
      snapshots_dir = path of the directory that will store snapshot files
    '''
    self.snapshots_dir = snapshots_dir
    self.denom = None
    # Data reset
    self.reset_data()


  def reset_data(self):
    '''
    Resets the data
    '''
    # Set of Tx0s
    self.s_tx0s = set()
    # Set of mix txs
    self.s_mix_txs = set()
    # Ordered list of tx0s
    self.l_tx0s = []
    # Ordered list of tx0s block timestamps
    self.l_ts_tx0s = []
    # Ordered list of #utxoscreated by tx0s
    self.l_utxos_tx0s = []
    # Ordered list of mix txs
    self.l_mix_txs = []
    # Ordered list of mix txs block timestamps
    self.l_ts_mix_txs = []
    # Dictionary of links between txs (src => tgt)
    self.d_links = defaultdict(list)
    # Dictionary of reverse links between txs (tgt => src)
    self.d_reverse_links = defaultdict(list)
    # Dictionary txid => mix_round
    self.d_txids = defaultdict(int)
    # Dictionary txid => tiid tx0
    self.d_tx0s = defaultdict(int)


  def set_dir(self, snapshots_dir):
    '''
    Sets the directory storing the snapshots
    Parameter:
      snapshots_dir = directory path
    '''
    self.snapshots_dir = snapshots_dir


  def load(self, denom):
    '''
    Loads the snapshot for a given denomination
    Parameters:
      denom = codes identifying the mix denomination
    '''
    # Data reset
    self.reset_data()
    self.denom = denom

    print('Start loading snapshot for %s denomination' % self.denom)

    # Loads the mix txs
    filename = '%s_%s.csv' % (FN_MIX_TXS, self.denom)
    filepath = '%s/%s' % (self.snapshots_dir, filename)

    with open(filepath, newline='\n') as csvfile:
      file_reader = csv.reader(csvfile, delimiter=';')
      next(file_reader, None)  # skips the headers
      mix_round = 0
      for row in file_reader:
        tiid = int(row[0])
        self.l_mix_txs.append(tiid)
        self.s_mix_txs.add(tiid)
        txid_prefix = row[1][0:2*TXID_PREFIX_LENGTH]
        self.d_txids[txid_prefix] = mix_round
        ts = int(row[2])
        self.l_ts_mix_txs.append(ts)
        mix_round += 1
    
    print('  Mix txs loaded')

    # Loads the tx0s
    filename = '%s_%s.csv' % (FN_TX0S, self.denom)
    filepath = '%s/%s' % (self.snapshots_dir, filename)

    with open(filepath, newline='\n') as csvfile:
      file_reader = csv.reader(csvfile, delimiter=';')
      next(file_reader, None)  # skips the headers
      for row in file_reader:
        tiid = int(row[0])
        self.l_tx0s.append(tiid)
        self.s_tx0s.add(tiid)
        txid_prefix = row[1][0:2*TXID_PREFIX_LENGTH]
        self.d_tx0s[txid_prefix] = tiid
        ts = int(row[2])
        self.l_ts_tx0s.append(ts)
        nb_utxos = int(row[3])
        self.l_utxos_tx0s.append(nb_utxos)

    print('  Tx0s loaded')

    # Loads the relationships between txs
    filename = '%s_%s.csv' % (FN_LINKS, self.denom)
    filepath = '%s/%s' % (self.snapshots_dir, filename)

    with open(filepath, newline='\n') as csvfile:
      file_reader = csv.reader(csvfile, delimiter=';')
      next(file_reader, None)  # skips the headers
      for row in file_reader:
        src = int(row[0])
        tgt = int(row[1])
        self.d_links[src].append(tgt)
        self.d_reverse_links[tgt].append(src)

    print('  Tx links loaded')
    
    print('Done!')

