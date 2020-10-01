'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A class computing a set of metrics for the mixed UTXOs (backward-looking)
'''
from whirlpool_stats.utils.constants import *
from whirlpool_stats.services.snapshot import Snapshot


class TxScores(object):

  def __init__(self, snapshot):
    '''
    Constructor
    Parameters:
      snapshot = snapshot
    '''
    self.snapshot = snapshot
    self.s_processed_txs = set()


  def compute(self, txid, denom):
    '''
    Computes a set of scores
    for a transaction (tx0 or mix) identified by its TXID
    Parameters:
      txid = Transaction id
      denom (optional) = Pool denomination (05, 005, 001)
    '''
    print('Processing scores for transaction %s' % txid)

    if denom is None:
      denom = self.find_denom(txid)
      if denom is None:
        return None
    elif denom not in ALL_DENOMS:
      print('Invalid denomination code')
      return None

    self.snapshot.load(denom, False)

    txid_prefix = txid[0:2*TXID_PREFIX_LENGTH]

    if txid_prefix in self.snapshot.d_txids.keys():
      # Transaction is a mix
      fwd_scores = self.compute_fwd_scores(txid)
      bwd_scores = self.compute_bwd_scores(txid)
      return {
        'type': 'mix',
        'fwd_anonset': fwd_scores['anonset'],
        'fwd_spread': fwd_scores['spread'],
        'bwd_anonset': bwd_scores['anonset'],
        'bwd_spread': bwd_scores['spread']
      }
    elif txid_prefix in self.snapshot.d_tx0s.keys():
      # Transaction is a Tx0
      tx0_scores = self.compute_tx0_scores(txid)
      return {
        'type': 'tx0',
        'nb_outs': tx0_scores['nb_outs'],
        'nb_counterparties': tx0_scores['nb_counterparties']
      }


  def find_denom(self, txid):
    '''
    Searches a txid in available snapshots
    Returns the associated denom code if txid was found in a snapshot
            otherwise returns None
    Parameters:
      txid = Transaction id
    '''
    tmp_snapshot = Snapshot(self.snapshot.snapshots_dir)

    for denom in ALL_DENOMS:
      try:
        tmp_snapshot.load(denom, False)
        prefix = txid[0:2*TXID_PREFIX_LENGTH]
        if (prefix in tmp_snapshot.d_txids.keys()) or (prefix in tmp_snapshot.d_tx0s.keys()):
          return denom
      except:
        pass

    return None


  def compute_tx0_scores(self, txid):
    '''
    Computes a few metrics for a tx0 identified by its txid
    Parameters:
      txid = Transaction id
    '''
    txid_prefix = txid[0:2*TXID_PREFIX_LENGTH]
    tiid = self.snapshot.d_tx0s[txid_prefix]
    tx0_idx = self.snapshot.l_tx0s.index(tiid)
    # Gets the number of spent outputs for the current Tx0
    first_mixes = self.snapshot.d_links[tiid]
    nb_spent_txos = len(first_mixes)
    # Lists the Tx0s acting as counterparties 
    # for the first mixes of the current Tx0
    s_counterparties = set()
    for tiid_mix in first_mixes:
      prev_tiids = self.snapshot.d_reverse_links[tiid_mix]
      # Checks if counterparty comes from a Tx0
      for prev_tiid in prev_tiids:
        if prev_tiid in self.snapshot.s_tx0s:
          s_counterparties.add(prev_tiid)
    # Gets the number of tx0s counterparties for the current Tx0
    # (remove 1 for the current Tx0)
    nb_counterparties = len(s_counterparties) - 1
    # Returns the result
    return {
      'nb_outs': nb_spent_txos,
      'nb_counterparties': nb_counterparties
    }


  def compute_fwd_scores(self, txid):
    '''
    Computes the forward-looking anonset and spread
    Parameters:
      txid = Transaction id
    '''
    txid_prefix = txid[0:2*TXID_PREFIX_LENGTH]
    mix_round = self.snapshot.d_txids[txid_prefix]
    tiid = self.snapshot.l_mix_txs[mix_round]
    # Resets the set of txs already reached during this walk
    self.s_processed_txs.clear()
    # Computes the anonset
    anonset = self.get_nb_descendants(tiid)
    # Computes the spread
    nb_later_unmixed_txos = 0
    for j in range(mix_round, len(self.snapshot.l_mix_txs)):
      tiid_round_j = self.snapshot.l_mix_txs[j]
      nb_remixes = len(self.snapshot.d_links[tiid_round_j])
      nb_later_unmixed_txos += NB_PARTICIPANTS - nb_remixes
    spread = float(anonset) * 100.0 / float(nb_later_unmixed_txos)
    # Returns the result
    return {
      'anonset': anonset,
      'spread': spread
    }


  def compute_bwd_scores(self, txid):
    '''
    Computes the backward-looking anonset and spread
    Parameters:
      txid = Transaction id
    '''
    txid_prefix = txid[0:2*TXID_PREFIX_LENGTH]
    mix_round = self.snapshot.d_txids[txid_prefix]
    tiid = self.snapshot.l_mix_txs[mix_round]
    # Resets the set of txs already reached during this walk
    self.s_processed_txs.clear()
    # Computes the anonset
    anonset = self.get_nb_sources(tiid)
    # Computes the spread
    nb_past_tx0s = len(list(filter(lambda x: x < tiid, self.snapshot.l_tx0s)))
    spread = float(anonset) * 100.0 / float(nb_past_tx0s)
    # Returns the result
    return {
      'anonset': anonset,
      'spread': spread
    }


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
