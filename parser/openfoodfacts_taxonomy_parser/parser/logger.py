import logging


class ParserConsoleLogger:
    @staticmethod
    def ellipsis(text, max=1000):
        """Cut a text adding eventual ellipsis if we do not display it fully"""
        return text[:max] + ("..." if len(text) > max else "")

    def __init__(self):
        self.parsing_warnings = []  # Stores all warning logs
        self.parsing_errors = []  # Stores all error logs

    def info(self, msg, *args, **kwargs):
        """Stores all parsing info logs"""
        logging.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Stores all parsing warning logs"""
        self.parsing_warnings.append(msg % args)
        logging.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Stores all parsing error logs"""
        self.parsing_errors.append(msg % args)
        logging.error(msg, *args, **kwargs)
