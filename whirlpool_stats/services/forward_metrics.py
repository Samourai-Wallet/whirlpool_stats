'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (forward-looking)
'''
from whirlpool_stats.utils.constants import *


class ForwardMetrics(object):

  def __init__(self, snapshot= None):
    '''
    Constructor
    Parameters:
      snapshot = snapshot
    '''
    self.snapshot = snapshot
    # Set of txs that have been processed
    self.s_processed_txs = set()
    # List of anonsets ordered by mix round
    self.l_anonsets = []
    # List of spreads ordered by mix round
    self.l_spreads = []


  def compute(self):
    '''
    Computes the metrics (forward-looking)
    '''
    print('Start computing metrics (forward-looking)')

    # Resets data structures storing the results
    self.l_anonsets = []
    self.l_spreads = []

    # Iterates over the ordered list of mix txs
    # and computes their anonset
    mix_round = 0
    nb_mixes = len(self.snapshot.l_mix_txs)

    for tiid in self.snapshot.l_mix_txs:
      # Resets the set of txs already reached during this walk
      self.s_processed_txs.clear()
      # Computes the anonset
      anonset = self.get_nb_descendants(tiid)
      self.l_anonsets.append(anonset)
      # Computes the spread
      nb_later_unmixed_txos = 0
      for j in range(mix_round, len(self.snapshot.l_mix_txs)):
        tiid_round_j = self.snapshot.l_mix_txs[j]
        nb_remixes = len(self.snapshot.d_links[tiid_round_j])
        nb_later_unmixed_txos += NB_PARTICIPANTS - nb_remixes
      spread = float(anonset) * 100.0 / float(nb_later_unmixed_txos)
      self.l_spreads.append(spread)
      # Displays a trace
      if mix_round % 100 == 0:
        pct_progress = mix_round * 100 / nb_mixes
        print('  Computed metrics for round %d (%d%%)' % (mix_round, pct_progress))
      mix_round += 1

    print('Done!')


  def get_nb_descendants(self, tiid):
    '''
    Gets the number of descendant UTXOs composing the forward-looking anonset of a tx
    (= number of unspents + number of mixed txos that have left the pool) 
    Parameters:
      tiid = id of the transaction
    '''
    next_tiids = self.snapshot.d_links[tiid]
    nb_utxos = NB_PARTICIPANTS - len(next_tiids)
    
    for next_tiid in next_tiids:
      if next_tiid not in self.s_processed_txs:
        if next_tiid in self.snapshot.s_mix_txs:
          nb_utxos += self.get_nb_descendants(next_tiid)
  
    self.s_processed_txs.add(tiid)
    return nb_utxos
