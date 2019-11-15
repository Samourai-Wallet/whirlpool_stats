'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the Tx0s
'''


class Tx0sMetrics(object):

  def __init__(self, snapshot= None):
    '''
    Constructor
    Parameters:
      snapshot = snapshot
    '''
    self.snapshot = snapshot
    # Dictionary txid_prefix => (nb_outputs_tx0, nb_counterparties)
    self.d_metrics = dict()


  def compute(self):
    '''
    Computes the metrics
    '''
    print('Start computing metrics for the Tx0s')

    # Resets data structures storing the results
    self.d_metrics = dict()

    nb_processed = 0

    # Iterates over the Tx0s
    nb_tx0s = len(self.snapshot.d_tx0s.keys())

    for prefix, tiid in self.snapshot.d_tx0s.items():
      s_counterparties = set()
      # Gets the number of mixed outputs for the current Tx0
      tx0_outs = self.snapshot.d_links[tiid]
      nb_outs = len(tx0_outs)
      # Lists the Tx0s acting as counterparties 
      # for the first mixes of the current Tx0
      for tiid_mix in tx0_outs:
        prev_tiids = self.snapshot.d_reverse_links[tiid_mix]
        # Checks if counterparty comes from a Tx0
        for prev_tiid in prev_tiids:
          if prev_tiid in self.snapshot.s_tx0s:
            s_counterparties.add(prev_tiid)
      # Gets number of counterparties for the current Tx0
      # (remove 1 for the current Tx0)
      nb_counterparties = len(s_counterparties) - 1
      # Stores the results
      self.d_metrics[prefix] = (nb_outs, nb_counterparties)

      nb_processed += 1
      if nb_processed % 100 == 0:
        pct_progress = nb_processed * 100 / nb_tx0s
        print('  Computed metrics for %d tx0s (%d%%)' % (nb_processed, pct_progress))

    print('Done!')
