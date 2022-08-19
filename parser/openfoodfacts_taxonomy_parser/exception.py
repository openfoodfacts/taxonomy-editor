class DuplicateIDError(Exception):
    """Raised when attempting to change id before adding the related node i.e. when the .txt file is missing a new line"""

    def __init__(self, line):
        exception_message = f"missing new line at line {line}"
        superinit = super().__init__(exception_message)
