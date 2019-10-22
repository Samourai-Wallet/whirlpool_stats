'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (backward-looking)
'''


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


  def compute(self):
    '''
    Computes the metrics (backward-looking)
    '''
    print('Start computing metrics (backward-looking)')

    # Resets data structures storing the results
    self.l_anonsets = []
    self.l_spreads = []

    # Iterates over the ordered list of mix txs
    # and computes their anonsets and spreads (backward-looking)
    mix_round = 0

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
      print('  Computed metrics for round %d' % mix_round)
      mix_round += 1

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


  def export_csv(self, export_dir):
    '''
    Exports the metrics in csv format
    Parameters:
      export_dir = export directory
    '''
    filename = 'whirlpool_%s_backward_metrics.csv' % self.snapshot.denom
    filepath = '%s/%s' % (export_dir, filename)

    f = open(filepath, 'w')
    line = 'mix_round;anonset;spread\n'
    f.write(line)

    for r in range(0, len(self.l_anonsets)):
      line = '%d;%d;%.2f\n' % (r, self.l_anonsets[r], self.l_spreads[r])
      f.write(line)
    f.close()
    
    print('Exported backward-looking metrics in %s' % filepath)
