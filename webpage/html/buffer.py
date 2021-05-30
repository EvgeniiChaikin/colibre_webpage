"""
Buffer class
"""

import io


class Buffer:

    def __init__(self):
        """
        Initialises the text content
        """
        self.__buffer = io.StringIO()

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


