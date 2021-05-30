"""
Tree class
"""

import os
from datetime import datetime
from html.buffer import Buffer
from html.content import Content
from typing import List, Dict, Union


class Tree:

    # To find out how long ago a page was created
    current_time = datetime.now()

    # Html is wield
    white_space: str = "&nbsp "

    # Display used parameters in html format
    run_param_page_icon = f"""<i style="float:right; color:#A9A9A9; font-size:13px" class="fa"> &#xf013 {white_space}</i>"""
    used_param_file_name = "used_parameters.html"

    # Link and icon for morphology page
    morphology_page_icon = f"""<i style="float:right; color:#FF8C00; font-size:18px" class="fa">&#xf06e {white_space}</i>"""
    morphology_file_name = "morphology.html"

    # Categories to look for
    individual = "individual_runs"
    comparison = "comparisons"

    def __init__(self, tabs=None, plot_webpage_name: str = "index.html"):
        if tabs is None:
            tabs = {}

        self.tabs: Dict[str, Dict[str, Union[str, List]]] = {
            key: {"data": [], "directory": value} for (key, value) in tabs.items()
        }
        self.data = Buffer()
        self.name: str = plot_webpage_name

        self.uploads_days_ago: List[int] = []
        self.uploads_z: List[float] = []
        self.run_links: List[str] = []

        self.N_individual_runs: int = 0
        self.N_comparisons: int = 0
        self.N_ongoing_runs: int = 0

    def find_creating_time(self, path_to_dir: str) -> int:
        """
        Compute the time difference between one and when the __plot_webpage_name
        file was created

        Parameters
        -------
        path_to_dir: str

        Returns
        -------
        output: int
        Number of days ago
        """

        time = os.stat(f"{path_to_dir}/{self.name}").st_mtime
        dt = datetime.fromtimestamp(time)
        days_ago = (self.current_time - dt).days

        return days_ago

    def days_ago_to_string(self, days_ago: int) -> str:
        """
        Formats the number of days ago

        Parameters
        -------
        days_ago: int

        Returns
        -------
        output: str
        Number of days ago formatted
        """

        if days_ago > 1:
            string = Content(f"{days_ago:d} days ago")
        elif days_ago == 1:
            string = Content(f"{days_ago:d} day ago")
        else:
            string = Content(f"{days_ago:d} New")

        string.wrap_text(block="i")
        string.wrap_text(block="span", span_style="float:right; color:#0000FF")

        return string.getter()

    def walk(
        self,
        abs_path: str,
        depth: int = 0,
        visual_line: str = "",
        prefix: str = "/cosma/home/www/swift.dur.ac.uk/public_html",
    ):
        """
        This function traverses the directory tree collecting necessary information in
        order to create a general html page with the runs' info and statistics
        """

        relative_path = abs_path.replace(prefix, "")

        # Number of sub-directions in the current directory
        list_dir = sorted(os.listdir(abs_path))
        N_of_dir = sum(
            [1 for d in list_dir if os.path.isdir(os.path.join(abs_path, d))]
        )

        # Loop over all sub-directories and files in the current directory
        for dir_counter, dir_name in enumerate(list_dir):

            # Absolute path to the file/sub-directory
            absolute_dir_path = os.path.join(abs_path, dir_name)

            # Do not do anything if it is a file
            if os.path.isdir(absolute_dir_path):

                if absolute_dir_path.find(self.individual) > -1:
                    self.N_individual_runs += 1
                elif absolute_dir_path.find(self.comparison) > -1:
                    self.N_comparisons += 1
                else:
                    continue

                # Number of sub-directories in a given sub-directory of this directory.
                # Zero means leaf node
                N_of_subdir = sum(
                    [
                        1
                        for sub_dir in os.scandir(absolute_dir_path)
                        if os.path.isdir(os.path.join(abs_path, sub_dir))
                    ]
                )

                is_leaf = N_of_subdir == 0

                # Check if the directory is a leaf node
                if is_leaf:

                    # Time data
                    days_ago = self.find_creating_time(absolute_dir_path)
                    modified = self.days_ago_to_string(days_ago=days_ago)
                    self.uploads_days_ago.append(days_ago)

                    link_to_plots = f"{relative_path}/{dir_name}/{self.name}"
                    morphology = ""
                    settings = ""

                    if os.path.isfile(
                        f"{absolute_dir_path:}/{self.used_param_file_name}"
                    ):
                        settings = f"""<a href="{relative_path}/{dir_name}/{self.used_param_file_name}" target="_blank">
                          {self.run_param_page_icon}</a>"""

                    if os.path.isfile(
                        f"{absolute_dir_path:}/{self.morphology_file_name}"
                    ):
                        settings = f"""<a href="{relative_path}/{dir_name}/{self.morphology_file_name}" target="_blank">
                          {self.morphology_page_icon}</a>"""

                    text = f"{dir_name}{modified}"
                    link_list = f"<li><a href={link_to_plots}>{text}</a>{settings}{morphology}</li>"
                    self.run_links.append(link_list)

                    text = f"{visual_line} |_{dir_name}{modified}"
                    link_tree = f"<li><a href={link_to_plots}>{text}</a>{settings}{morphology}</li>"
                    self.data.write_to_buffer(link_tree)

                    try:
                        redshift = float(dir_name[1:4])
                        self.uploads_z.append(redshift)
                    except ValueError:
                        pass

                    # Extra tabs
                    for (tab_name, tab_content) in self.tabs.items():
                        if link_to_plots.find(tab_content["directory"]) > -1:
                            string_split = text.split()
                            if (
                                string_split[:3]
                                == f"{self.white_space} {self.white_space} |".split()
                            ):
                                arg = text.find("|")
                                text = f" {self.white_space * 3}{text[arg + 2:]}"

                            elif string_split[:3] == f"| {self.white_space} |".split():
                                indent = 8
                                arg = text[indent:].find("|")
                                text = f" | {self.white_space * 2}{text[indent + arg + 1:]}"

                            string = f"<li><a href={link_to_plots}>{text}</a>{settings:s}{morphology:s}</li>"
                            self.tabs[tab_name]["data"].append(string)

                # Not a leaf
                else:
                    text = f"{visual_line} |_<b> {dir_name} </b>"
                    string = f"<li>{text}</li>"
                    self.data.write_to_buffer(string)
                    rel_path_dir = f"{relative_path}/{dir_name}"

                    # Extra tabs
                    if dir_name == self.individual or dir_name == self.comparison:
                        for tab_name in self.tabs.keys():
                            self.tabs[tab_name]["data"].append(string)

                    for (tab_name, tab_content) in self.tabs.items():
                        if rel_path_dir.find(tab_content["directory"]) > -1:
                            string_split = text.split()

                            if (
                                string_split[:3]
                                == f"{self.white_space} {self.white_space} |".split()
                            ):
                                arg = text.find("|")
                                text = f" {self.white_space * 3}{text[arg + 2:]}"

                            elif string_split[:3] == f"| {self.white_space} |".split():
                                indent = 8
                                arg = text[indent:].find("|")
                                text = f" | {self.white_space * 2}{text[indent + arg + 1:]}"

                            self.tabs[tab_name]["data"].append(f"<li>{text}</li>")

                # Evolve tree representation
                if dir_counter < N_of_dir - 1:
                    new_visual_line = f"{visual_line} | {self.white_space} "
                else:
                    new_visual_line = f"{visual_line} {self.white_space * 2}"

                # Recurse
                self.walk(
                    absolute_dir_path,
                    depth + 1,
                    new_visual_line,
                )
