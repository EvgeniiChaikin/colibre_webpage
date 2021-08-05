#!/usr/bin/env python3

"""
Builds an html page using various blocks of data
"""

from html.object import HtmlPage
from html.content import Content
from html.buffer import Buffer
from tree.object import Tree
from datetime import datetime
from typing import Dict, Tuple, List
import subprocess
import json
import numpy as np
import glob
import os
import argparse

from plots.plot_style import import_style, create_plot_with_style
import matplotlib.pylab as plt


def traverse_tree(initial_path: str, tabs: Dict[str, str], debug: False) -> Tree:
    """
    Create the webpage step by step

    Parameters
    -------
    initial_path: str
    Path to the root of the directory tree

    tabs: Dict[str, str]
    Extra tabs

    debug: bool
    Running in debug mode?

    Returns
    -------
    output: Tree
    A tree object
    """

    if debug:
        print("Creating a tree...")
        print("")
    tree = Tree(tabs=tabs, debug=debug)

    if debug:
        print("Starting traversal...")
        print("")

    tree.walk(abs_path=initial_path)

    if debug:
        print("")
        print("Finishing traversal...")
        print("")

    return tree


def create_table_with_links_to_reports(file_name: str = "reports.json") -> str:
    """
    Reads off reports' titles and the links to the reports.
    Creates a table with this info on the main html webpage.

    Parameters
    -------
    file_name: str
    File with the report names and links

    Returns
    -------
    output: str
    """

    try:
        with open(file_name, "r") as f:
            data = json.load(f)

    except FileNotFoundError as err:
        error_message = (
            f"The file with the reports' links '{file_name:s}' is not found."
        )
        raise RuntimeError(error_message) from err

    buffer = Buffer()
    buffer.write_to_buffer("<h2>Reports</h2>")

    for author, reports in data.items():
        if reports:
            buffer.write_to_buffer(f"<i>Author: {author:s}</i><ol>")
            for name, link in reports.items():
                buffer.write_to_buffer(f"<li><a href={link:s}>{name:s}</a></li>")
            buffer.write_to_buffer("</ol>")

    return buffer.get_content()


def create_plots(
    tree: Tree,
    ongoing_runs=None,
    size_x: float = 8,
    size_y: float = 8,
    z_max: float = 127,
    prefix: str = "/cosma/home/www/swift.dur.ac.uk/public_html",
) -> str:

    # Absolute path to where the script is executed!
    abs_path = os.getcwd()
    relative_path = abs_path.replace(prefix, "")

    # Import pretty style for plotting
    import_style(style=f"{abs_path}/plots/style.mplstyle")

    if ongoing_runs is None:
        ongoing_runs = []

    # Figure 1
    fig, ax = create_plot_with_style(size_x, size_y)
    ongoing_runs_z = [float(z) if z != "Enqueued" else z_max for z in ongoing_runs]
    ax.hist(
        ongoing_runs_z,
        bins=np.linspace(-0.125, 5.375, 23),
        rwidth=0.94,
        alpha=0.9,
        color="green",
    )
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    plt.xlabel("Redshift")
    plt.ylabel("Number of ongoing runs")
    num_of_ongoing_runs_z = f"{relative_path}/plots/Number_of_ongoing_runs_z.png"
    plt.savefig(num_of_ongoing_runs_z, bbox_inches="tight", pad_inches=0.1)
    plt.close()

    # Figure 2
    fig, ax = create_plot_with_style(size_x, size_y)
    ax.hist(
        tree.uploads_days_ago,
        bins=np.linspace(-0.5, 150.5, 152),
        rwidth=0.90,
        alpha=0.9,
    )
    ax.set_xticks([0, 30, 60, 90, 120, 150])
    plt.xlabel("Days since last update")
    plt.ylabel("Number of analysis pages")
    num_of_uploads = f"{relative_path}/plots/Number_of_uploads.png"
    plt.savefig(num_of_uploads, bbox_inches="tight", pad_inches=0.1)
    plt.close()

    # Figure 3
    fig, ax = create_plot_with_style(size_x, size_y)
    plt.hist(
        tree.uploads_z,
        bins=np.linspace(-0.125, 5.375, 23),
        rwidth=0.94,
        alpha=0.9,
        color="orange",
    )
    plt.xticks([0, 1, 2, 3, 4, 5])
    ax.yaxis.set_tick_params()
    plt.xlabel("Redshift")
    plt.ylabel("Number of pages with plots")
    num_of_analysed_runs_z = f"{relative_path}/plots/Number_of_analysed_runs_z.png"
    plt.savefig(num_of_analysed_runs_z, bbox_inches="tight", pad_inches=0.1)
    plt.close()

    # Block with figures
    tab = Content(
        f"""<h2>Run statistics</h2>
            <ul>
            <li><b>Redshifts of ongoing runs:</b><br>
            <img src="{num_of_ongoing_runs_z:s}" 
            alt="Num of ongoing runs vs z" width="325" height="325"></li>
            <li><b>Num of uploads in the last 2 months:</b><br>
            <img src="{num_of_uploads:s}" 
            alt="Num of run uploads" width="325" height="325"></li><br>
            <li><b>Redshifts of statistics pages:</b><br>
            <img src="{num_of_analysed_runs_z:s}" 
            alt="Num of analysed runs vs z" width="325" height="325"></li>
            </ul>"""
    )

    return tab.getter()


def fetch_current_runs_names(
    user: str, file_with_redshifts: str, file_pattern: str,
) -> Tuple[str, List[str]]:
    """
    Find currently ongoing runs

    Parameters
    -------
    user: str
    Name of user's cosma account

    file_with_redshifts: str
    File containing the redshifts

    file_pattern: str
    File patter to use when looking for matches

    Returns
    -------
    output: str
    """

    run_names = []
    run_redshifts = []

    # Open file with output redshifts
    output_z = open(file_with_redshifts, "r")

    run_z_list = []
    for line in output_z.readlines():
        try:
            redshift = "{:.2f}".format(float(line.split(", ")[0]))
            run_z_list.append(redshift)
        # Skip header if there is one
        except ValueError:
            pass

    paths = []
    # See the ongoing runs
    try:
        process = subprocess.run(
            ["squeue", "-u", user, "-o", "%Z"], stdout=subprocess.PIPE
        )
        paths = process.stdout.decode("utf-8").split("\n")

    except Exception:
        print("Cannot run the slurm command 'squeue'")

    # Loop over paths to ongoing runs
    for path in paths:

        # Looking for names
        file_paths = [
            name for name in glob.glob(f"{path}/*.yml") if name.find("used") == -1
        ]
        if file_paths:
            with open(file_paths[0], "r") as f:
                file_lines = f.readlines()
                for l in file_lines:
                    if l.__contains__("run_name:"):
                        run_names.append(l.split()[-1])
        else:
            run_names.append("None")

        # Looking for redshifts
        file_paths = sorted(glob.glob(f"{path}/*{file_pattern}*.hdf5"))

        if file_paths:
            # The path must be of the form "*/*_????.hdf5"
            snp_nums = [int(path.split("/")[-1][-9:-5]) for path in file_paths]

            # Snapshot with the highest number corresponds to the lowest redshift
            N_latest_snp = sorted(snp_nums)[-1]

            try:
                z = run_z_list[N_latest_snp]
            except IndexError:
                z = "-1.0"

            run_redshifts.append(z)
        else:
            run_redshifts.append("Enqueued")

    # return run_names, run_redshifts
    run_names = run_names[1:-1]
    run_redshifts = run_redshifts[1:-1]

    # Block with the info on ongoing runs
    buffer = Buffer()
    buffer.write_to_buffer(
        """
        <h2>Names of ongoing runs<span style="float:right; color:black">Current z</span></h2>
        <ol>"""
    )

    for idx in np.argsort(run_redshifts):
        if run_names[idx] != "None":
            buffer.write_to_buffer(
                f"""<li>{run_names[idx]:s} 
            <span style="float:right;">{ run_redshifts[idx]:s}</span></li>"""
            )
    buffer.write_to_buffer("</ol>")

    return buffer.get_content(), run_redshifts


def create_webpage(
    path_to_root: str,
    user: str,
    snapshot_name: str,
    path_to_file_with_redshifts: str,
    path_to_output: str,
    extra_tab_names: List[str] = "",
    htmlfile_name: str = "index.html",
    path_to_style: str = "./html/style.html",
    debug: bool = False,
):
    """
    Create the webpage step by step

    Parameters
    -------
    path_to_root: str
    Path to the root of the three with directories

    user: str
    Name of user's cosma account

    snapshot_name:str
    Name patter of snapshot files

    path_to_file_with_redshifts: str
    Path to the file with redshifts used in the simulations

    path_to_output: str
    Path to the directory containing the output html file

    extra_tab_names: List[str]
    List of names of extra tabs

    htmlfile_name: str
    Name(s) of html files for webpages with plots

    path_to_style: str
    Path to file with a style for webpage

    debug: bool
    Extra output and checks for debugging?
    """

    today_pretty_format = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")

    obj = HtmlPage(filename=f"{path_to_output}/{htmlfile_name}", debug=debug)
    obj.load_style(path_to_file=path_to_style)

    tabs = {
        "full_tree": "Full tree",
        "date": "Sort by date",
        "redshift": "Sort by redshift",
    }
    extra_tabs = {
        str(count): tab_name for count, tab_name in enumerate(extra_tab_names)
    }
    tabs.update(extra_tabs)

    # Traverse tree
    tree = traverse_tree(initial_path=path_to_root, tabs=tabs, debug=debug)
    tree_content = Content(tree.data.get_content())

    # Compute additional properties
    reports = create_table_with_links_to_reports()
    current_runs, redshifts_ongoing = fetch_current_runs_names(
        user=user,
        file_with_redshifts=path_to_file_with_redshifts,
        file_pattern=snapshot_name,
    )
    plots = create_plots(tree, ongoing_runs=redshifts_ongoing)

    # Flex container
    obj.write_body(
        """<div class="container" style="display: flex; max-width: 2500px;">"""
    )
    obj.write_body("""<div class="content">""")

    # Open tabs
    obj.create_tab_panel_open(tabs=tabs)

    tab_tree_top = f"""<h1>Path to root: {path_to_root} 
                      <span style="float:right; color:blue;"> Uploaded
                      </span>
                      </h1>"""

    # Tab 1
    tab1 = Content(tab_tree_top)
    tree_content.wrap_text(block="ul")
    tab1.append_text(tree_content.getter())
    tab1.wrap_text(
        block="div",
        div_id="full_tree",
        div_class="tabcontent",
        div_style="display:none",
    )
    obj.write_body(tab1.getter())

    # Tab 2
    tab2 = Content(tab_tree_top)
    buffer2 = Buffer()
    for item_arg in np.argsort(tree.uploads_days_ago):
        buffer2.write_to_buffer(tree.run_links[item_arg])
    buffer2_out = Content(buffer2.get_content())
    buffer2_out.wrap_text("ol")
    tab2.append_text(buffer2_out.getter())
    tab2.wrap_text(
        block="div", div_id="date", div_class="tabcontent", div_style="display:none"
    )
    obj.write_body(tab2.getter())

    # Tab 3
    tab3 = Content(tab_tree_top)
    buffer3 = Buffer()
    for item_arg in np.argsort(tree.uploads_z):
        buffer3.write_to_buffer(tree.run_links[item_arg])
    buffer3_out = Content(buffer3.get_content())
    buffer3_out.wrap_text("ol")
    tab3.append_text(buffer3_out.getter())
    tab3.wrap_text(
        block="div", div_id="redshift", div_class="tabcontent", div_style="display:none"
    )
    obj.write_body(tab3.getter())

    # Extra tabs
    for tab_name in extra_tabs:
        tabn = Content(tab_tree_top)
        buffern = Buffer()
        for string in tree.tabs[tab_name]["data"]:
            buffern.write_to_buffer(string)
        buffern_out = Content(buffern.get_content())
        buffern_out.wrap_text("ul")
        tabn.append_text(buffern_out.getter())
        tabn.wrap_text(
            block="div",
            div_id=tab_name,
            div_class="tabcontent",
            div_style="display:none",
        )
        obj.write_body(tabn.getter())

    # Close left column
    obj.write_body("</div>")
    # Add script to make tab panel interactive
    obj.create_tab_panel_close(tab_content="tabcontent")

    # Open middle column
    obj.write_body(
        """<div class="content"; style="margin-left: 1em; max-width: 550px;">"""
    )

    # Block with general information
    tab = Content(
        f"""
        <h2>General information</h2><ul>
        <li>The page was last updated on 
        <b>{today_pretty_format:s}</b></li>
        <li>Number of ongoing runs: <b>{len(redshifts_ongoing):d}</b></li>
        <li>Number of analysed runs [individual]: 
        <b>{tree.N_individual_runs:d}</b></li>
        <li>Number of analysed runs [comparisons]: 
        <b>{tree.N_comparisons:d}</b></li><p>{tree.white_space}</p>
        </ul>"""
    )
    tab.wrap_text(block="div", div_class="content1")
    obj.write_body(tab.getter())

    obj.write_body(reports)
    obj.write_body(current_runs)

    # Close middle column
    obj.write_body("""</div>""")

    # Plots to the third column
    obj.write_body(
        """<div class="content"; style="margin-left: 1em; max-width: 330px">"""
    )
    obj.write_body(plots)
    obj.write_body("</div>")

    obj.finish_webpage()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""DESCRIPTION:
        Generate a tree with html pages containing plots from COLIBRE runs.
        The script assumes that the run directories begin with z?.?_ prefix where 
        the first and second question marks are the first and second digit in the value 
        of the redshift at which plots for the respective directory are made.
        There is also division into "individual_runs" and "comparisons" sub-trees. The
        former contains plots with data from single runs, while in the latter data from 
        multiple runs is shown."""
    )

    parser.add_argument(
        "-r",
        "--root_dir",
        required=True,
        type=str,
        nargs="?",
        action="store",
        help="Absolute (not relative) path to top folder from which to start tree traversal.",
    )

    parser.add_argument(
        "-u",
        "--user",
        required=True,
        type=str,
        nargs="?",
        action="store",
        help="Name of user's cosma account",
    )

    parser.add_argument(
        "-s",
        "--snp-name",
        required=True,
        type=str,
        nargs="?",
        action="store",
        help="Snapshot name pattern. Example: if you use 'colibre_????.hdf5', then provide 'colibre'",
    )

    parser.add_argument(
        "-z",
        "--path-to-redshifts",
        required=True,
        type=str,
        nargs="?",
        action="store",
        help="Path to the file containing the redshifts for simulation output",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        nargs="?",
        action="store",
        help="Path to the output directory where the html file will be saved",
    )

    parser.add_argument(
        "-t",
        "--tabs",
        type=str,
        required=False,
        default="",
        help="Names of extra tabs on a tab bar. These are also the names of the subdirectories these tabs will refer to",
        nargs="*",
    )

    parser.add_argument(
        "-d",
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Run the script in debug mode if this flag is present. Default: no debug.",
    )

    config = parser.parse_args()

    print("Creating webpage...")
    print("")

    if config.debug:
        print("Running in the debug mode...")
        print(" ")

    print(f"Root dir: {config.root_dir}")
    print(f"Output dir: {config.output}")
    print(f"User name: {config.user}")
    print(f"Path to file with redshifts: {config.path_to_redshifts}")
    print(f"Snapshot name pattern: {config.snp_name}")
    print(" ")

    print(f"Extra tabs:")
    for count, tab in enumerate(config.tabs, start=1):
        print(f"{count}. {tab}")

    print(" ")

    create_webpage(
        path_to_root=config.root_dir,
        user=config.user,
        snapshot_name=config.snp_name,
        path_to_file_with_redshifts=config.path_to_redshifts,
        path_to_output=config.output,
        extra_tab_names=config.tabs,
        debug=config.debug,
    )
