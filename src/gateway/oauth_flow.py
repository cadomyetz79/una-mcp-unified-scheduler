"""Pending OAuth authorization-code transactions for a research web gateway.

This is NOT a Microsoft Entra client or login provider. It creates a
short-lived, one-use PKCE S256 / state request. A future approved server-side
token exchange must use a supported Microsoft library (MSAL).

No student identity or session is granted by starting/finishing this flow.
"""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import secrets
import threading
import time
from urllib.parse import urlencode, urlsplit
from uuid import UUID


OAUTH_STATE_COOKIE = "__Host-una_oauth_flow"
OAUTH_STATE_COOKIE_SAMESITE = "lax"  # OAuth's cross-site top-level GET callback
OAUTH_STATE_COOKIE_MAX_AGE = 300


@dataclass(frozen=True)
class StudentOAuthConfig:
    tenant_id: str
    web_client_id: str
    api_app_id: str
    redirect_uri: str

    def __post_init__(self):
        try:
            tenant = str(UUID(self.tenant_id))
            client = str(UUID(self.web_client_id))
            resource = str(UUID(self.api_app_id))
        except (TypeError, ValueError, AttributeError):
            raise ValueError("Exact tenant, client and API GUIDs required.") from None
        callback = urlsplit(self.redirect_uri)
        if (
            callback.scheme != "https"
            or not callback.netloc
            or callback.username is not None
            or callback.password is not None
            or callback.path != "/auth/callback"
            or callback.query
            or callback.fragment
            or callback.hostname in (None, "")
            or self.redirect_uri != (
                f"{callback.scheme}://{callback.netloc}/auth/callback"
            )
            or tenant != self.tenant_id
            or client != self.web_client_id
            or resource != self.api_app_id
            or client == resource
        ):
            raise ValueError("Exact approved HTTPS OAuth configuration required.")

    @property
    def origin(self):
        parsed = urlsplit(self.redirect_uri)
        return f"{parsed.scheme}://{parsed.netloc}"

    @property
    def scope(self):
        return f"api://{self.api_app_id}/academic.read"

    @property
    def authorize_endpoint(self):
        return (
            "https://login.microsoftonline.com/"
            f"{self.tenant_id}/oauth2/v2.0/authorize"
        )


@dataclass(frozen=True)
class OAuthStart:
    authorization_url: str
    state_cookie: str = field(repr=False)
    expires_at: float


@dataclass(frozen=True)
class _Pending:
    cookie_digest: bytes = field(repr=False)
    code_verifier: str = field(repr=False)
    expires_at: float


class StudentOAuthFlowStore:
    """One-use, bounded in-memory OAuth state tied to a browser cookie."""

    def __init__(self, *, config: StudentOAuthConfig, max_flows=128):
        if (
            not isinstance(config, StudentOAuthConfig)
            or type(max_flows) is not int
            or not 1 <= max_flows <= 10000
        ):
            raise ValueError("Invalid OAuth flow store configuration.")
        self.config = config
        self._max_flows = max_flows
        self._pending: dict[str, _Pending] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _digest(secret: str) -> bytes:
        return hashlib.sha256(secret.encode("utf-8")).digest()

    def begin(self) -> OAuthStart:
        state = secrets.token_urlsafe(32)
        browser_cookie = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")

        now = time.time()
        deadline = now + OAUTH_STATE_COOKIE_MAX_AGE
        with self._lock:
            self._pending = {
                key: value for key, value in self._pending.items()
                if value.expires_at > now
            }
            if len(self._pending) >= self._max_flows:
                raise RuntimeError("OAuth initiation capacity exceeded.")
            self._pending[self._digest(state).hex()] = _Pending(
                cookie_digest=self._digest(browser_cookie),
                code_verifier=verifier,
                expires_at=deadline,
            )

        url = self.config.authorize_endpoint + "?" + urlencode({
            "client_id": self.config.web_client_id,
            "response_type": "code",
            "redirect_uri": self.config.redirect_uri,
            "response_mode": "query",
            "scope": self.config.scope,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })
        return OAuthStart(
            authorization_url=url,
            state_cookie=browser_cookie,
            expires_at=deadline,
        )

    def consume(
        self, *, state: str | None, browser_cookie: str | None
    ) -> str:
        """Consume state atomically, then return private PKCE verifier.

        Replays or malformed/browser-unbound state never reach token exchange.
        Even an invalid cookie consumes a matching state to prevent replay.
        """
        if (
            not isinstance(state, str)
            or not 30 <= len(state) <= 256
            or not isinstance(browser_cookie, str)
            or not 30 <= len(browser_cookie) <= 256
        ):
            raise PermissionError("Invalid OAuth correlation.")

        key = self._digest(state).hex()
        with self._lock:
            pending = self._pending.pop(key, None)

        if (
            pending is None
            or pending.expires_at <= time.time()
            or not hmac.compare_digest(
                pending.cookie_digest, self._digest(browser_cookie)
            )
        ):
            raise PermissionError("Invalid OAuth correlation.")

        return pending.code_verifier
