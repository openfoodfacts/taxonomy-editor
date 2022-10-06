"""
Custom exceptions for Taxonomy Editor API
"""
class TransactionMissingError(RuntimeError):
    """
    Raised when attempting to run a query using null transaction context variable
    """

    def __init__(self):
        exception_message = f"Transaction context variable is null/missing"
        return super().__init__(exception_message)
