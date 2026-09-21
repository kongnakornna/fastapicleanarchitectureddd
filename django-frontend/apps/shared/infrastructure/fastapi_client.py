import httpx
from django.conf import settings


class FastAPIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.base_url = settings.FASTAPI_BASE_URL.rstrip("/")
        self.timeout = getattr(settings, "FASTAPI_TIMEOUT", 30)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"User-Agent": "DjangoBFF/2.1"},
        )

    def request(self, method, path, *, token=None, **kwargs):
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self._client.request(method, path, headers=headers, **kwargs)

    def get(self, path, **kw): return self.request("GET", path, **kw)
    def post(self, path, **kw): return self.request("POST", path, **kw)

    def json(self, method, path, **kw):
        return self.request(method, path, **kw).json()


fastapi = FastAPIClient()
