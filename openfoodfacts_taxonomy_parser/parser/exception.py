class FileError(ValueError):
    ''' Raised when attempting to change id before adding the related node i.e. when the .txt file is missing a new line '''

    def __init__(self,line):
        msg = 'missing new line at line {}'
        exception_message = msg.format(line)
        superinit = super().__init__
        superinit(exception_message)