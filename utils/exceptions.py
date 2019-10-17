

class EmailError(Exception):
    """Base class for other email exceptions"""
    pass


class CouldNotSendEmailError(EmailError):
    """Generic error for error in email host user or password"""
    pass
