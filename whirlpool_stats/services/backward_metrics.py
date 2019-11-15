'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (backward-looking)
'''
from collections import defaultdict
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

    # Resets data structures storing the results
    self.l_anonsets = []
    self.l_spreads = []
    self.d_nb_mixes = defaultdict(int)
    self.d_inflow = defaultdict(int)
    self.d_nb_active_tx0s = defaultdict(int)

    # Dictionary day => set od active tx0s
    d_tmp_active_tx0s = defaultdict(set)

    # Iterates over the ordered list of mix txs
    # and computes their anonsets and spreads (backward-looking)
    mix_round = 0
    nb_mixes = len(self.snapshot.l_mix_txs)

    for tiid in self.snapshot.l_mix_txs:
      # Resets the set of txs already reached during this walk
      self.s_processed_txs.clear()
      # Computes the anonset
      anonset = self.get_nb_sources(tiid)
      self.l_anonsets.append(anonset)
      # Computes the spread
      nb_past_tx0s = len(list(filter(lambda x: x < tiid, self.snapshot.l_tx0s)))
      spread = float(anonset) * 100.0 / float(nb_past_tx0s)
      self.l_spreads.append(spread)
      # Updates activity metrics
      day = get_datetime_of_day(self.snapshot.l_ts_mix_txs[mix_round])
      self.d_nb_mixes[day] += 1
      prev_tiids = self.snapshot.d_reverse_links[tiid]
      for prev_tiid in prev_tiids:
        if prev_tiid in self.snapshot.s_tx0s:
          self.d_inflow[day] += 1
          d_tmp_active_tx0s[day].add(prev_tiid)
      # Displays a trace
      if mix_round % 100 == 0:
        pct_progress = mix_round * 100 / nb_mixes
        print('  Computed metrics for round %d (%d%%)' % (mix_round, pct_progress))
      mix_round += 1

    # Fills d_nb_active_tx0s
    for k,v in d_tmp_active_tx0s.items():
      self.d_nb_active_tx0s[k] = len(v)

    print('Done!')


  def get_nb_sources(self, tiid):
    '''
    Gets the number of ancestor tx0s found for a tx
    Parameters:
      tiid = id of the transaction
    '''
    nb_tx0s = 0
    prev_tiids = self.snapshot.d_reverse_links[tiid]
    
    for prev_tiid in prev_tiids:
      if prev_tiid not in self.s_processed_txs:
        if prev_tiid in self.snapshot.s_mix_txs:
          nb_tx0s += self.get_nb_sources(prev_tiid)
        elif prev_tiid in self.snapshot.s_tx0s:
          nb_tx0s += 1
          self.s_processed_txs.add(prev_tiid)
    
    self.s_processed_txs.add(tiid)
    return nb_tx0s
