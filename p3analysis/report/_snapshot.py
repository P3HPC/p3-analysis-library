# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import collections
import os

import matplotlib.pyplot as plt

import p3analysis.metrics
import p3analysis.plot
from p3analysis._utils import _require_columns
from p3analysis.metrics._divergence import _coverage_string_to_json


def _tmpdir(prefix):
    """
    Return the next unused directory name of the form prefix000
    """
    suffix = 0
    while True:
        name = f"{prefix}{suffix:0>3}"
        if not os.path.exists(name):
            break
        suffix += 1
    return name


def _block_symlinks(path):
    """
    Refuse to create files via symbolic links.
    """
    if not os.path.islink(path):
        return
    raise PermissionError("Refusing to create files via symbolic link.")


def _sort_by_app_order(df, app_order):
    """
    Sort the DataFrame such that the order of applications matches that
    specified in app_order.
    """

    def index_function(row):
        return app_order.tolist().index(row["application"])

    sort_index = df.apply(index_function, axis=1)
    sort_index.name = "sort_index"

    order = df.join(sort_index).sort_values(by=["sort_index"]).index
    df = df.loc[order]
    df.reset_index(inplace=True, drop=True)  # add style change
    return df


def snapshot(df, cov=None, directory=None):
    """
    Generate an HTML report representing a snapshot of P3 characteristics.

    The report includes:
    - A cascade plot (see :py:func:`p3analysis.plot.cascade`)
    - A navigation chart (see :py:func:`p3analysis.plot.navchart`)
    - A table breaking down the lines of code shared between applications

    .. _Code Base Investigator: https://github.com/P3HPC/code-base-investigator

    Parameters
    ----------
    df: DataFrame
        A pandas DataFrame storing performance efficiency data.
        The following columns are always required: "problem", "platform",
        "application". At least one of the following columns
        is required: "app eff" or "arch eff".

        If `cov` is None, a "coverage" column is required. Values of the
        "coverage" column must be coverage traces adhering to the P3 Analysis
        Library coverage schema. Otherwise, a "coverage_key" column is
        required.

    cov: DataFrame, optional
        A pandas DataFrame storing coverage data. The following columns are
        required: "coverage_key", "coverage".

        Values of the "coverage" column must be coverage traces adhering to the
        P3 Analysis Library coverage schema.

    directory: string, optional
        The directory in which to generate the HTML report. If no value is
        provided, a directory name of the form snapshot000 will be chosen
        automatically.

    Raises
    ------
    ValueError
        If any of the required columns are missing.
        If any coverage string fails to validate against the P3 coverage
        schema.

    TypeError
        If any of the values in the "fom" column of `df` are non-numeric.
        If any of the values in the "coverage" is not a JSON string.

    PermissionError
        If the directory specified by `directory` or any of the files generated
        by the snapshot cannot be written.

    FileExistsError
        If the directory specified by `directory` already exists.
    """
    _require_columns(
        df,
        ["problem", "platform", "application"],
    )
    if cov is None:
        _require_columns(df, ["coverage"])
    else:
        _require_columns(df, ["coverage_key"])
        _require_columns(cov, ["coverage_key", "coverage"])

    if len(df["problem"].unique()) > 1:
        raise NotImplementedError(
            "Handling multiple problems is currently not implemented.",
        )

    cwd = os.getcwd()
    if not directory:
        directory = _tmpdir("snapshot")
    else:
        directory = os.path.join(cwd, directory)
    _block_symlinks(directory)
    os.makedirs(directory, exist_ok=False)

    # Always open files relative to the snapshot directory,
    # without following symbolic links
    dir_fd = os.open(directory, os.O_RDONLY | os.O_NOFOLLOW)

    def _safe_opener(path, flags):
        safe_flags = flags | os.O_TRUNC | os.O_NOFOLLOW
        return os.open(path, safe_flags, 0o666, dir_fd=dir_fd)

    # Identify a consistent application order to use across all plots
    app_order = df["application"].unique()

    # Calculate the efficiencies using all available data
    effs = p3analysis.metrics.application_efficiency(df)

    # Limit the plots to the latest results
    snap = effs.drop_duplicates(
        ["platform", "application"],
        keep="last",
        ignore_index=True,
    ).dropna()
    snap = _sort_by_app_order(snap, app_order)

    plt.figure(figsize=(6, 5))
    p3analysis.plot.cascade(snap)
    with open("cascade.png", "xb", opener=_safe_opener) as fp:
        plt.savefig(fp, bbox_inches="tight")

    plt.clf()

    pp = p3analysis.metrics.pp(snap)
    pp = _sort_by_app_order(pp, app_order)

    div = p3analysis.metrics.divergence(df, cov)
    div = _sort_by_app_order(div, app_order)

    plt.figure(figsize=(5, 5))
    p3analysis.plot.navchart(pp, div)
    plt.tight_layout()
    with open("navchart.png", "xb", opener=_safe_opener) as fp:
        plt.savefig(fp, bbox_inches="tight")

    p3df = df.join(cov.set_index("coverage_key"), on="coverage_key")
    p3df["coverage"] = p3df["coverage"].apply(_coverage_string_to_json)
    p3df = p3df.drop_duplicates(
        ["platform", "application"],
        keep="last",
        ignore_index=True,
    ).dropna()

    # This function is defined inline so that it can access the platform name.
    def coverage_to_setmap(maps):
        """
        Fold a list of coverage maps into a setmap.
        """
        linemap = collections.defaultdict(set)
        for index, coverage in maps.items():
            platform = p3df.loc[index]["platform"]
            for entry in coverage:
                fn = entry["file"]
                for region in entry["regions"]:
                    linemap[(fn, tuple(region))].add(platform)

        setmap = collections.defaultdict(int)
        for key, platforms in linemap.items():
            fn, triple = key
            start, end, num_lines = triple
            setmap[frozenset(platforms)] += num_lines

        return setmap

    groups = p3df[["problem", "application", "coverage"]].groupby(
        ["problem", "application"],
    )
    setmaps = groups.agg(coverage_to_setmap)
    setmaps.reset_index(inplace=True)
    setmaps.rename(columns={"coverage": "setmap"}, inplace=True)

    # Generate an HTML report
    # this is a minified CSS to be embedded in the HTML report
    css = """
td,th{padding-left:10px;padding-right:10px}body{margin:24px}html{font-family:'Gill Sans','Gill Sans MT',Calibri,'Trebuchet MS',sans-serif}@media only screen and (min-width:768px){html{width:auto}}.cascade-navchart{display:inline-flex;align-content:end;margin:auto;gap:15px;min-width:100%}.cascade-navchart>figure>img{max-width:40vw;max-height:40vw}figcaption::before{content:"Figure:"}figcaption{font-style:italic}table{border-collapse:collapse;max-width:60%}th{font-size:1.1rem}tr:nth-of-type(2n){background-color:rgba(0,0,0,.15)}tr:first-of-type{border-top:2px solid #000}tr:last-of-type{border-bottom:2px solid #000}    # noqa: E501
    """
    html = []
    html += ["<html>"]
    html += ['<meta charset="UTF-8">']
    html += [
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',  # noqa: E501
    ]
    html += ['<meta http-equiv="X-UA-Compatible" content="ie=edge">']
    html += [
        "<title>Performance, Portability & Productivity (P3) Snapshot</title>",
    ]
    html += [f"<style>{css}</style>"]

    # now start working on the material
    html += ["<body>"]
    html += ["<header>"]
    html += ["<h1>Performance, Portability & Productivity (P3) Snapshot</h1>"]
    html += ["</header>"]

    # section containing the plots
    html += [
        """<section>
        <h2>Performance Portability, Code Convergence</h2>
        <div class="cascade-navchart">
            <figure>
                <img src="cascade.png" alt="cascade-plot" />
                <figcaption>
                    <p>Performance Portability</p>
                </figcaption>
            </figure>
            <figure>
                <img src="navchart.png" alt="navchart" />
                <figcaption>
                    <p>Performance Portability vs Code Convergence</p>
                </figcaption>
            </figure>
        </div>
    </section>""",
    ]

    html += ["<section>"]
    html += ["<h2>Code Divergence</h2>"]
    html += ["<table>"]
    # table header
    html += [
        """<tr>
                <th>Application</th>
                <th>Platform Set</th>
                <th>LOC</th>
            </tr>""",
    ]
    for index, row in setmaps.iterrows():
        application = row["application"]
        for platforms, lines in row["setmap"].items():
            pstring = "{" + ", ".join(platforms) + "}"
            html += ["<tr>"]
            html += [
                f"<td>{application}</td><td>{pstring}</td><td>{lines}</td>",
            ]
            html += ["</tr>"]
    html += ["</table>"]
    html += ["</body>"]
    html += ["</html>"]
    with open("index.html", "x", opener=_safe_opener) as fp:
        fp.write("\n".join(html))

    os.close(dir_fd)
