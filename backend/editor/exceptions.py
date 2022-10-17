"""
Custom exceptions for Taxonomy Editor API
"""
class TransactionMissingError(RuntimeError):
    """
    Raised when attempting to run a query using null transaction context variable
    """

    def __init__(self):
        exception_message = "Transaction context variable is null/missing"
        return super().__init__(exception_message)

class TaxnonomyImportError(RuntimeError):
    """
    Raised when attempting to fetch a taxonomy from GitHub
    """
    def __init__(self):
        exception_message = "Unable to fetch the given taxonomy from GitHub"
        return super().__init__(exception_message)

class TaxonomyParsingError(RuntimeError):
    """
    Raised whem attempting to parse a taxonomy imported from GitHub
    """
    def __init__(self):
        exception_message = "Unable to parse the requested taxonomy file imported from GitHub"
        return super().__init__(exception_message)