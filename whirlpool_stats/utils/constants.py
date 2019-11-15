'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

Set of constants used by the scripts
'''

# OXT base url for whirpool snapshots
BASE_URL_SNAPSHOTS = 'https://oxt.me/static/share/whirlpool'

# Filename templates composing the snapshot for a given denomination
FN_MIX_TXS = 'whirlpool_mix_txs'
FN_TX0S = 'whirlpool_tx0s'
FN_LINKS = 'whirlpool_links'

FILENAME_TEMPLATES = [
  FN_MIX_TXS,
  FN_TX0S,
  FN_LINKS
]

# Denomination codes
DENOM_05 = '05'
DENOM_005 = '005'
DENOM_001 = '001'

ALL_DENOMS = [
  DENOM_05,
  DENOM_005,
  DENOM_001
]

# Number of participants per mix
NB_PARTICIPANTS = 5

# TXID prefix length (in bytes)
TXID_PREFIX_LENGTH = 8
