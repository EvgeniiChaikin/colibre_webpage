"""
Content class
"""


class Content:
    def __init__(self, text: str = ""):
        """
        Initialises the text content

        Parameters
        -------
        text: str
        Initial text to build the class for
        """
        self.__content: str = f"{text}"

    def wrap_text(self, block: str, **kwargs: str):
        """
        Wraps text into a block with a style specified by keyword parameters

        Parameters
        -------

        block: str
        block to wrap the text into. Examples: div, p, ul

        kwargs: str
        Attributes of the div object
        """

        attributes = " ".join([f'{key}="{value}"' for (key, value) in kwargs.items()])

        # class keyword is reserved
        attributes = attributes.replace(f"{block}_", "")

        self.__content = f"""<{block} {attributes}>
                              {self.__content}
                              </{block}>"""

        return

    def append_text(self, text: str):
        """
        Appends text to content


        Parameters
        -------

        text: str
        text to append
        """
        self.__content = f"""{self.__content}
                             {text}"""
        return

    def getter(self) -> str:
        """
        Fetch the class content

        Returns
        -------

        output: str
        """
        return self.__content
