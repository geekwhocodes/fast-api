class UpgradeAlembicHeadError(Exception):
    """Exception raised for errors in the input salary.
    Attributes:
        message -- explanation of the error
    """

    pass


class TenantNameNotAvailableError(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        message -- explanation of the error
    """

    def __init__(
        self,
        schema,
        message="Tenant name '{}' is not available. Please use different tenant name.",
    ):
        self.message = message.format(schema)
        super().__init__(self.message)
