#!/usr/bin/env python3
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import antares_client
import numpy as np
import pandas as pd
import requests

try:
    from tqdm.auto import tqdm as progress_bar
except ImportError:

    def progress_bar(it, *args, **kwargs):
        yield from it


COLUMN_NAME_MAPPER = {
    "ant_mjd": "time",
    "ant_mag": "mag",
    "ant_magerr": "magerr",
    "ant_passband": "band",
}


BTS_URL = "https://sites.astro.caltech.edu/ztf/bts/explorer.php?f=s&subsample=snia&classstring=&classexclude=&quality=y&covok=y&visok=y&purity=y&snlc=y&ztflink=lasair&lastdet=&startsavedate=&startpeakdate=&startra=&startdec=&startz=&startdur=&startrise=&startfade=&startpeakmag=&startabsmag=&starthostabs=&starthostcol=&startb=&startav=&endsavedate=&endpeakdate=&endra=&enddec=&endz=&enddur=&endrise=&endfade=&endpeakmag=&endabsmag=&endhostabs=&endhostcol=&endb=&endav=&format=csv"


def download(url: str, path: Path) -> None:
    with open(path, "wb") as fh, requests.get(url, stream=True) as resp:
        for chunk in resp.iter_content(chunk_size=1 << 13):
            fh.write(chunk)


def download_light_curve(ztf_id: str) -> Optional[pd.DataFrame]:
    locus = antares_client.search.get_by_ztf_object_id(ztf_id)
    if locus is None:
        return None
    lc = locus.lightcurve

    # Remove NaNs
    lc = lc[~np.isnan(lc["ant_mag"])]

    # Time sort
    lc = lc.sort_values("ant_mjd")

    # Remove duplicate times
    passband_ids = lc["ant_passband"].map({"g": 1, "R": 2})
    lc = lc[
        (np.diff(lc["ant_mjd"], append=np.inf) != 0)
        & (np.diff(passband_ids, append=-1) != 0)
    ]

    return lc


def get_light_curves(ids: Iterable[str], folder: Path) -> Dict[str, pd.DataFrame]:
    lcs = {}
    for ztf_id in progress_bar(ids):
        lc_path = folder.joinpath(f"{ztf_id}.csv")
        if lc_path.exists():
            lc = pd.read_csv(lc_path)
        else:
            lc = download_light_curve(ztf_id)
            if lc is None or lc.size == 0:
                continue
            lc = lc[list(COLUMN_NAME_MAPPER)]
            lc.rename(columns=COLUMN_NAME_MAPPER, inplace=True, errors="raise")
            lc[list(COLUMN_NAME_MAPPER.values())].to_csv(lc_path, index=False)
        lcs[ztf_id] = lc
    return lcs


def output_selected_objects(
    lcs: Dict[str, pd.DataFrame],
    folder: Path,
    bts_table: pd.DataFrame,
    *,
    band: str,
    min_n_obs: int,
    min_obs_before_peak: int,
    min_obs_after_peak: int,
) -> Tuple[Path, int]:
    count_outputs = 0
    path = folder.joinpath(
        f"snIa_band{band}_minobs{min_n_obs}_beforepeak{min_obs_before_peak}_afterpeak{min_obs_after_peak}.csv"
    )
    with open(path, "w") as fh:
        for ztf_id, lc in progress_bar(lcs.items()):
            one_band = lc[lc["band"] == band]
            if one_band.shape[0] < min_n_obs:
                continue
            peak_mjd = 2458000 - 2400000.5 + bts_table.loc[ztf_id]["peakt"]
            if np.count_nonzero(one_band["time"] < peak_mjd) < min_obs_before_peak:
                continue
            if np.count_nonzero(one_band["time"] > peak_mjd) < min_obs_after_peak:
                continue
            fh.write(f"{ztf_id}\n")
            count_outputs += 1
    return path, count_outputs


def main():
    folder = Path(__file__).parent
    lc_folder = folder.joinpath("light-curves")
    if not lc_folder.exists():
        lc_folder.mkdir()

    bts_table_path = folder.joinpath("bts.csv")
    if not bts_table_path.exists():
        download(BTS_URL, bts_table_path)
    bts_table = pd.read_csv(bts_table_path, index_col="ZTFID")
    lcs = get_light_curves(bts_table.index, lc_folder)

    selected_path, count = output_selected_objects(
        lcs,
        folder,
        bts_table,
        band="g",
        min_n_obs=10,
        min_obs_before_peak=3,
        min_obs_after_peak=4,
    )
    print(f"{count} ZTF IDs are written to {selected_path}")


if __name__ == "__main__":
    main()
