'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (backward-looking)
'''
from collections import defaultdict
from datasketch import HyperLogLogPlusPlus
from whirlpool_stats.utils.constants import *
from whirlpool_stats.utils.date import get_datetime_of_day


class BackwardMetrics(object):

  def __init__(self, snapshot):
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
    # Dictionary date => nb_mixes
    self.d_nb_mixes = defaultdict(int)
    # Dictionary date => inflow
    self.d_inflow = defaultdict(int)
    # Dictionary date => nb_active_tx0s
    self.d_nb_active_tx0s = defaultdict(int)


  def compute(self):
    '''
    Computes the metrics (backward-looking)
    '''
    print('Start computing metrics (backward-looking)')

    # Number of mixes
    nb_mixes = len(self.snapshot.l_mix_txs)

    # Mapping mix_tiid => {
    #   'nb_refs": number of remaining refs from following mixes,
    #   'ancestors': HLL++ storing ancestors tx0s
    # }
    d_mix_ancestors = dict()

    # Mapping day => set od active tx0s
    d_tmp_active_tx0s = defaultdict(set)

    # Resets data structures storing the results
    self.l_anonsets = []
    self.l_spreads = []
    self.d_nb_mixes = defaultdict(int)
    self.d_inflow = defaultdict(int)
    self.d_nb_active_tx0s = defaultdict(int)

    # Iterates over the ordered list of mix txs
    mix_round = 0
    for tiid in self.snapshot.l_mix_txs:
      day = get_datetime_of_day(self.snapshot.l_ts_mix_txs[mix_round])
      hll = HyperLogLogPlusPlus(p=HLL_P)
      for prev_tiid in self.snapshot.d_reverse_links[tiid]:
        if prev_tiid in self.snapshot.s_tx0s:
          # Adds the tx0 to the HLL
          hll.update(str(prev_tiid).encode('utf8'))
          self.d_inflow[day] += 1
          d_tmp_active_tx0s[day].add(prev_tiid)
        else:
          prev_info = d_mix_ancestors[prev_tiid]
          # Merges the HLL with the HLL of the parent
          hll.merge(prev_info['ancestors'])
          if prev_info['nb_refs'] == 1:
            del d_mix_ancestors[prev_tiid]
          else:
            prev_info['nb_refs'] -= 1
            d_mix_ancestors[prev_tiid] = prev_info
      # Computes and stores the anonset
      anonset = round(hll.count())
      self.l_anonsets.append(anonset)
      # Computes and stores the spread
      nb_past_tx0s = len(list(filter(lambda x: x < tiid, self.snapshot.l_tx0s)))
      spread = float(anonset) * 100.0 / float(nb_past_tx0s)
      self.l_spreads.append(spread)
      # Increases the numbers of daily mixes
      self.d_nb_mixes[day] += 1
      # Stores info about current mix
      d_mix_ancestors[tiid] = {
        'nb_refs': len(self.snapshot.d_links[tiid]),
        'ancestors': hll
      }
      # Displays a trace
      if mix_round % 100 == 0:
        pct_progress = mix_round * 100 / nb_mixes
        print('  Computed metrics for round %d (%d%%)' % (mix_round, pct_progress))
      # Updates the mix round
      mix_round += 1

    # Fills d_nb_active_tx0s
    for k,v in d_tmp_active_tx0s.items():
      self.d_nb_active_tx0s[k] = len(v)

    d_mix_ancestors.clear()

    print('Done!')
