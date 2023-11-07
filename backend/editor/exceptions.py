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


class SessionMissingError(RuntimeError):
    """
    Raised when attempting to run a query using null session context variable
    """

    def __init__(self):
        exception_message = "Session context variable is null/missing"
        return super().__init__(exception_message)


class TaxonomyImportError(RuntimeError):
    """
    Raised when attempting to fetch a taxonomy from GitHub
    """

    def __init__(self):
        exception_message = "Unable to fetch the given taxonomy from GitHub"
        return super().__init__(exception_message)


class TaxonomyParsingError(RuntimeError):
    """
    Raised when attempting to parse a taxonomy imported from GitHub
    """

    def __init__(self):
        exception_message = "Unable to parse the requested taxonomy file imported from GitHub"
        return super().__init__(exception_message)


class TaxonomyUnparsingError(RuntimeError):
    """
    Raised when attempting to unparse a taxonomy exported from Neo4j
    """

    def __init__(self):
        exception_message = "Unable to unparse the requested taxonomy exported from Neo4j"
        return super().__init__(exception_message)


class GithubUploadError(RuntimeError):
    """
    Raised when attempting to upload a taxonomy to Github
    """

    def __init__(self):
        exception_message = "Unable to upload the given taxonomy file to Github"
        return super().__init__(exception_message)


class GithubBranchExistsError(RuntimeError):
    """
    Raised when attempting to create an existing branch in Github
    """

    def __init__(self):
        exception_message = "The new branch to be created already exists"
        return super().__init__(exception_message)
