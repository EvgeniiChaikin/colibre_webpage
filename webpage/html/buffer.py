"""
Buffer class
"""

import io


class Buffer:

    def __init__(self, text: str = ""):
        """
        Initialises the text content

        Parameters
        -------
        text: str
        Initial text to build the class for
        """
        self.__buffer = io.StringIO(initial_value=text)

    def __del__(self):

        self.__buffer.close()

        return

    def get_content(self) -> str:
        """
        Returns buffer content
        """
        return self.__buffer.getvalue()

    def write_to_buffer(self, text: str = ""):
        """
        Write to buffer

        Parameters
        -------
        text: str
        Text to add
        """
        self.__buffer.write(text)

        return


