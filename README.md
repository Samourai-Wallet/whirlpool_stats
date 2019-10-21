# whirlpool_stats

A set of python scripts allowing to compute statistics about Whirlpool.


## Python versions

Python >= 3.4.4


## Dependencies

TODO


## Installation

Manual installation
```
Gets the library from Github : https://github.com/Samourai-Wallet/whirlpool_stats.git
Unzips the archive in a temp directory
python setup.py install
```


## Usage

TODO


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

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

Tip: Don't forget to run `python setup.py clean && python setup.py build && python setup.py install` after modifying the source files.
