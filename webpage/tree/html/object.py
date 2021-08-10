from os import path
import webbrowser
from .buffer import Buffer
from .content import Content
from typing import Dict, Optional, Union


class HtmlPage:

    white_space: str = "&nbsp "

    def __init__(self, filename: str, debug=False):

        self._html_style = """"""

        # Open head and body streams (for reading and writing)
        self._html_head = Buffer()
        self._html_body = Buffer()

        self._debug = debug

        # Name of the output file
        self._webpage_filename = filename

        # Webpage content following build
        self._webpage_content: Union[None, str] = None

    def __del__(self):

        if self._debug:
            print("Destruction: Closing head and body streams")

        # Close the streams
        del self._html_head, self._html_body

        return

    def write_head(self, text: str):
        """
        Writes to head of webpage


        Parameters
        -------

        text: str
        text to write to the head
        """

        self._html_head.write_to_buffer(text=text)
        return

    def write_body(self, text: str):
        """
        Writes to the body of webpage


        Parameters
        -------

        text: str
        text to write to the body
        """
        self._html_body.write_to_buffer(text=text)
        return

    def build_webpage(self):
        """
        Builds the html page
        """

        if self._debug:
            print("Building webpage...")

        if self._webpage_content is None:

            webpage = f"""
                      <!DOCTYPE html>
                      <html>
                        <head>
                          {self._html_style}
                          {self._html_head.get_content()}
                        </head>
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                        <body>
                          {self._html_body.get_content()}
                        </body>
                      </html>
                      """

            self._webpage_content = webpage

        else:
            raise RuntimeError("Webpage cannot be build because already exists!")

        return

    def set_style(self, style: str):
        """
        Sets up webpage style

        Parameters
        -------

        style: str
        style in the html format
        """

        self._html_style = style
        return

    def load_style(self, path_to_file: str):
        """
        Loads page style from the provided file and applies it to the webpage

        Parameters
        -------

        path_to_file: str
        path to the file with the style for webpage
        """

        if path.exists(path_to_file):
            with open(path_to_file) as f:

                # Read style
                loaded_style = f.read()

                # Apply style
                self.set_style(style=loaded_style)
        else:
            raise IOError(f"File '{path_to_file}' does not exist!")

        return

    def save_webpage(self):
        """
        Saves the webpage into a file. If the file
        already exists, overwrites it. The webpage has to be built first!
        """

        if self._webpage_content is not None:

            with open(self._webpage_filename, "w+") as out:

                if self._debug:
                    print(f"Saving webpage into {self._webpage_filename}...")

                out.write(self._webpage_content)

        return

    def open_in_browser(self):
        """
        Opens the webpage using the default browser.
        """

        if path.isfile(self._webpage_filename):
            webbrowser.open_new_tab(self._webpage_filename)
        else:
            raise RuntimeError("The webpage can only be visualised after it has been built and saved into a file!")

        return

    def create_tab_panel_open(self, tabs: Optional[Dict[str, str]] = None):
        """
        Creates tabs with different content. Start the tab panel block

        Parameters
        -------
        tabs: Optional[Dict[str, str]]
        Dictionary containing the tabs
        """

        if tabs is None:
            tabs = {}

        self._html_body.write_to_buffer("""<div class="tab">""")

        for (name, display_name) in tabs.items():

            button_attrs = f"""tablinks" onclick="openTab(event, '{name}')"""
            button = Content(display_name)
            button.wrap_text(block="button", button_class=button_attrs)

            self._html_body.write_to_buffer(button.getter())

        self._html_body.write_to_buffer("""</div>""")

        return

    def create_tab_panel_close(self, tab_content: str = "tabcontent"):
        """
        Finish the tab panel block

        Parameters
        -------

        tab_content: str
        Tab content object
        """
        self._html_body.write_to_buffer(
            f"""<script>
                  function openTab(evt, TabName) 
                  {{
                    var i, {tab_content}, tablinks;
                    tabcontent = document.getElementsByClassName("{tab_content}");
                    for (i = 0; i < {tab_content}.length; i++) {{
                      {tab_content}[i].style.display = "none";
                    }}
                  
                    tablinks = document.getElementsByClassName("tablinks");
                  
                    for (i = 0; i < tablinks.length; i++) {{
                      tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }}
                  
                    document.getElementById(TabName).style.display = "block";
                    evt.currentTarget.className += " active";
                  }}
                </script>
            """
        )

        return
