# Data to test with [`light-curve`](https://github.com/light-curve/) feature extraction codes

Data format is CSV files, mandatory columns are `time,band,mag,magerr` or `time,band,flux,fluxerr`.
Any other columns may exist

Folder content:
- `RRLyrae/light-curves' contains SDSS Stride 82 light curves of RR Lyrae stars, described by [Sesar et al. (2010)](https://ui.adsabs.harvard.edu/abs/2010ApJ...708..717S/abstract), data are from [Vizier](https://cdsarc.cds.unistra.fr/viz-bin/cat/J/ApJ/708/717)
- `SNIa/light-curves` contains ZTF light curves of SN Ia of [the Bright Transient Survey (BTS)](https://sites.astro.caltech.edu/ztf/bts/bts.php), light-curve data are from [ANTARES broker](https://antares.noirlab.edu)
- `from-issues` contains non-trivial test data needed to reproduce past, current (and we hope future) issues. The paths follow this notation: `{repository-name}-{issue-number}/filename.csv`, for example `light-curve-3/640202200001881.csv`
