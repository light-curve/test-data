#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from astropy.io import ascii
from astropy.table import Table

BASE_VIZIER_URL = "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/708/717"
PHOT_VIZIER_URL = f"{BASE_VIZIER_URL}/phot"

PASSBANDS = "ugriz"


def table1(root: Path) -> dict[int, Table]:
    subdir = root / "apj326724t1"
    readme = subdir / "ReadMe"
    assert readme.exists()
    paths = sorted(subdir.glob("*.dat"))
    assert len(paths) > 0
    return {int(path.stem): ascii.read(path, format="basic", readme=readme) for path in paths}


def table1_light_curve(id: int) -> Table:
    obj_url = f"{PHOT_VIZIER_URL}/{id}.dat"
    return ascii.read(
        obj_url,
        names=[
            "RAdeg",
            "DEdeg",
            "JDu",
            "umag",
            "e_umag",
            "JDg",
            "gmag",
            "e_gmag",
            "JDr",
            "rmag",
            "e_rmag",
            "JDi",
            "imag",
            "e_imag",
            "JDz",
            "zmag",
            "e_zmag",
        ],
    )


def convert_sesar_t1(table: Table) -> Table:
    time = np.concatenate([table[f"JD{band}"] for band in PASSBANDS])
    mag = np.concatenate([table[f"{band}mag"] for band in PASSBANDS])
    magerr = np.concatenate([table[f"e_{band}mag"] for band in PASSBANDS])
    passbands = np.concatenate([[band] * len(table) for band in PASSBANDS])
    flat_table = Table(dict(time=time, mag=mag, magerr=magerr, band=passbands))
    # missed values are -99.99
    flat_table = flat_table[mag > 0]
    flat_table.sort("time")
    return flat_table


def table2(root: Path) -> Table:
    return ascii.read(root / "apj326724t2.txt")


def main():
    root = Path(__file__).parent
    output = root / "light-curves"
    output.mkdir(exist_ok=True)

    objects = table2(root)
    objects[["Num", "Type", "Per"]].write(root / "periods.csv", overwrite=True)

    for id in objects["Num"]:
        table = table1_light_curve(id)
        converted_table = convert_sesar_t1(table)
        converted_table.write(output / f"{id}.csv", overwrite=True)


if __name__ == "__main__":
    main()
