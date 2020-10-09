# whirlpool_stats

Whirlpool Stats Tools (WST for short) is a command line tool allowing to compute privacy-oriented statistics related to Whirlpool.

Main features:
- download of snapshots of the transaction graph for all the pools in a given denomination (downloads from OXT - snapshots refreshed daily)
- support of downloads through SOCKS5
- computation of metrics for a downloaded snapshot
- export (CSV format) of statistics computed for the active snapshot
- generation of dynamic charts for the active snapshot
- display of computed metrics for a mix transaction stored in the active snapshot

## Metrics

### Anonymity sets

#### Backward-looking anonymity set

The entry point to Whirlpool is a 'tx0'.

Backward-looking anonymity set for a selected utxo is defined as the number of 'tx0' ancestors that feed into the transaction of the selected utxo.

Every mixed utxo can backtrace a path to the initial mix in its own pool because every mix after the initial mix in each pool contains at least one remixed utxo. This ensures that the anonymity set for any pool goes back to the pool's inception.

#### Forward-looking anonymity set

Forward-looking anonymity set for a selected utxo is defined as the number of un-remixed utxos created in the pool starting from the selected utxo's own transaction.

## Python versions

Python >= 3.4.4

pip3


## Dependencies

PySocks

requests[socks]

plotly >= 4.1.0

numpy >= 1.11.0

datasketch


## Installation

Manual installation
```
# Clone the git repository under the current directory
git clone https://github.com/Samourai-Wallet/whirlpool_stats.git

# Move to /whirlpool_stats directory
cd whirlpool_stats

# Install the dependencies with pip3
pip3 install -r ./requirements.txt

# Move to /whirlpool_stats subdirectory
cd whirlpool_stats

# Start WST
python3 wst.py
```


## Usage

Start a WST session
```
> python wst.py

Starting Whirlpool Stats Tool...
Type "help" for a list of available commands.

wst#/tmp>
```

Show help
```
wst#/tmp> help

Documented commands (type help <topic>):
========================================
download  export  help  load  plot  quit  score  socks5  workdir

wst#/tmp>
```

Set Socks5 proxy before downloading data from OXT
```
wst#/tmp> socks5 127.0.0.1:9150

wst#/tmp>
```
Note: default SOCKS port is  9150 for the Tor Browser Bundle and 9050 for the Tor Expert Bundle.


Change the working directory for this WST session
```
wst#/tmp> workdir /home/laurent/whirlpool

wst#/home/laurent/whirlpool>
```

Download in the working directory a snaphot for the 0.5BTC pools
```
wst#/home/laurent/whirlpool> download 05

Start download of snapshot for 05 denomination
  whirlpool_mix_txs_05.csv downloaded
  whirlpool_tx0s_05.csv downloaded
  whirlpool_links_05.csv downloaded
Download complete

wst#/home/laurent/whirlpool>
```

Load and compute the statistcs for the snaphot
```
wst#/home/laurent/whirlpool> load 05

Start loading snapshot for 05 denomination
  Mix txs loaded
  Tx0s loaded
  Tx links loaded
Done!
Start computing metrics (forward-looking)
  Computed metrics for round 0
  Computed metrics for round 1
  Computed metrics for round 2
  Computed metrics for round 3
  Computed metrics for round 4
  ...
Done!

wst#/home/laurent/whirlpool>
```

Plot a chart for a given metrics of the active snapshot (e.g.: forward-looking anonset)
```
wst#/home/laurent/whirlpool> plot fwd anonset

Preparing the chart... 

wst#/home/laurent/whirlpool>
```

Display the metrics computed for a transaction stored in the active snapshot 
```
wst#/home/laurent/whirlpool> score 4e72519d391ce83e0659c9022a00344bedbb253de1747cf290162b3d3ea51479

Backward-looking metrics for the outputs of this mix:
  anonset = 92
  spread = 89%

Forward-looking metrics for the outputs of Tx0s having this transaction as their first mix:
  anonset = 127
  spread = 76%

wst#/home/laurent/whirlpool>
```

Quit WST
```
wst#/home/laurent/whirlpool> quit

Good bye!

>
```


## Troubleshooting

This project requires python 3. If your default `python` points to python 2, substitute `python3` for all instructions in this README.


## Data Sources

These scripts rely on snapshots of Whirpool's transaction graph computed by the OXT platform.

These snapshots can be downloaded at the urls:
- https://oxt.me/static/share/whirlpool/whirlpool_mix_txs_`denom`.csv (list of mix transactions)
- https://oxt.me/static/share/whirlpool/whirlpool_tx0s_`denom`.csv (list of mix tx0s)
- https://oxt.me/static/share/whirlpool/whirlpool_links_`denom`.csv (list of edges between the transactions)
where `denom` is a code identifying the pool denomination (valid codes = 05, 005, 001)


## Contributors
@LaurentMT 
@SamouraiDev


## Contributing

WST is still a very basic tool. All contributions are welcome!

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

Tip: Don't forget to run `python setup.py clean && python setup.py build && python setup.py install` after modifying the source files.
