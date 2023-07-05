class TenantNotFoundError(Exception):
    def __init__(self, tenant_id):
        self.message = f"Tenant {tenant_id} not found!"
        super().__init__(self.message)
