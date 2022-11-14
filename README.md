# Data to test with [`light-curve`](https://github.com/light-curve/) feature extraction codes

Data format is CSV files, mandatory columns are `time,band,mag,magerr` or `time,band,flux,fluxerr`.
Any other columns may exist

Folder content:
- `SNIa/light-curves` contains ZTF light curves of SN Ia of [the Bright Transient Survey (BTS)](https://sites.astro.caltech.edu/ztf/bts/bts.php), light-curve data are from [ANTARES broker](https://antares.noirlab.edu)
- `from-issues` contains non-trivial test data needed to reproduce past, current (and we hope future) issues. The paths follow this notation: `{repository-name}-{issue-number}/filename.csv`, for example `light-curve-3/640202200001881.csv`
