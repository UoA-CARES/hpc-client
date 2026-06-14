class HPCClientError(RuntimeError):
    pass


class HPCAuthenticationError(HPCClientError):
    pass


class HPCRequestError(HPCClientError):
    pass
