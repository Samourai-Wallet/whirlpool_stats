'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (forward-looking)
'''
import sys
from datasketch import HyperLogLogPlusPlus
from whirlpool_stats.utils.constants import *


class ForwardMetrics(object):

  def __init__(self, snapshot= None):
    '''
    Constructor
    Parameters:
      snapshot = snapshot
    '''
    self.snapshot = snapshot
    # List of anonsets ordered by mix round
    self.l_anonsets = []
    # List of spreads ordered by mix round
    self.l_spreads = []


  def compute(self):
    '''
    Computes the metrics (forward-looking)
    '''
    print('Start computing metrics (forward-looking)')

    # Number of mixes
    nb_mixes = len(self.snapshot.l_mix_txs)

    # Forward number of utxos
    # (number of UTXOs created after current mix included)
    fwd_nb_utxos = 0

    # Mapping mix_tiid => {
    #   'nb_refs": number of remaining refs from previous mixes,
    #   'descendants': HLL++ storing descendants UTXOs
    # }
    d_mix_descendants = dict()

    # Resets data structures storing the results
    self.l_anonsets = []
    self.l_spreads = []

    # Iterates over the ordered list of mix txs
    mix_round = nb_mixes - 1
    for tiid in reversed(self.snapshot.l_mix_txs):
      hll = HyperLogLogPlusPlus(p=HLL_P)
      next_tiids = self.snapshot.d_links[tiid]
      is_large_mix = tiid in self.snapshot.d_mix_txs_utxos
      nb_txos = self.snapshot.d_mix_txs_utxos[tiid] if is_large_mix else DEFAULT_NB_PARTICIPANTS
      nb_utxos = nb_txos - len(next_tiids)
      # Adds an entry in the HLL for each UTXO
      for i in range(0, nb_utxos):
        utxo_id = '%d-%d' % (tiid, i)
        hll.update(utxo_id.encode('utf8'))
      # Updates the forward number of utxos
      fwd_nb_utxos += nb_utxos
      # Computes the set of descendants mixes (current mix included)
      for next_tiid in next_tiids:
        next_info = d_mix_descendants[next_tiid]
        # Merges the HLL with the HLL of the parent
        hll.merge(next_info['descendants'])
        if next_info['nb_refs'] == 1:
          del d_mix_descendants[next_tiid]
        else:
          next_info['nb_refs'] -= 1
          d_mix_descendants[next_tiid] = next_info
      # Computes and stores the anonset
      anonset = round(hll.count())
      self.l_anonsets.append(anonset)
      # Computes and stores the spread
      spread = float(anonset) * 100.0 / float(fwd_nb_utxos)
      self.l_spreads.append(spread)
      # Stores info about current mix
      prev_tiids = self.snapshot.d_reverse_links[tiid]
      nb_refs = sum([1 if p_tiid in self.snapshot.s_mix_txs else 0 for p_tiid in prev_tiids])
      d_mix_descendants[tiid] = {
        'nb_refs': nb_refs,
        'descendants': hll
      }
      # Displays a trace
      if (nb_mixes - mix_round) % 100 == 0:
        pct_progress = (nb_mixes - mix_round) * 100 / nb_mixes
        print('  Computed metrics for round %d (%d%%)' % (mix_round, pct_progress))

      mix_round -= 1

    # Reverses the lists
    self.l_anonsets = list(reversed(self.l_anonsets))
    self.l_spreads = list(reversed(self.l_spreads))

    d_mix_descendants.clear()

    print('Done!')
