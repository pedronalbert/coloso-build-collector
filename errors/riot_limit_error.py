class RiotLimitError(Exception):
    def __init__(self, retryAfter):
        self.message = "RiotLimitError, retry after {} seconds".format(retryAfter)
        self.retryAfter = retryAfter
