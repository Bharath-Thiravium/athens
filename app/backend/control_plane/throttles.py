from rest_framework.throttling import SimpleRateThrottle


class TenantLookupThrottle(SimpleRateThrottle):
    scope = 'tenant_lookup'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        if not ident:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }
