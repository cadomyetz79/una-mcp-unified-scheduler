"""Testable server-side student web session store (research prototype).

An opaque browser cookie identifies a record held only in the trusted Python
process. The delegated bearer token never goes in a browser cookie, HTML,
localStorage, or model prompt.

IMPORTANT: issue() must be called ONLY by an approved server-side login
callback after the incoming Entra token has been cryptographically verified.
This module does NOT perform OAuth, verify JWT signatures, issue a login
endpoint, persist sessions, or make the browser interface interactive.
"""

from dataclasses import dataclass, field, replace
import hashlib
import hmac
import math
import secrets
import threading
import time

from mcp.server.auth.provider import AccessToken

from src.gateway.plan_context import PlanContext

from src.gateway.authenticated_session import (
    AuthenticatedStudentSession,
    session_from_verified_token,
)


SESSION_COOKIE_NAME = "__Host-una_student_session"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "strict"


@dataclass(frozen=True)
class IssuedStudentWebSession:
    """Opaque cookie and anti-CSRF token for a trusted server-side callback.

    Both fields are secret; neither appears in repr or error messages.
    Only a *future verified login callback* should set the HttpOnly cookie.
    """
    cookie_value: str = field(repr=False)
    csrf_token: str = field(repr=False)
    expires_at: float


@dataclass(frozen=True)
class _StoredSession:
    authenticated_session: AuthenticatedStudentSession = field(repr=False)
    csrf_digest: bytes = field(repr=False)
    expires_at: float
    plan_context: PlanContext | None = field(
        default=None, repr=False
    )


class StudentWebSessionStore:
    """Short-lived, revocable, in-process sessions for synthetic testing.

    Not suitable for multi-worker / production deployment; a durable server-
    side store with encryption at rest and centralized revocation is needed.
    """

    def __init__(
        self,
        *,
        student_lookup,
        allowed_issuer: str,
        ttl_seconds: int = 900,
        max_sessions: int = 128,
    ):
        if (
            not allowed_issuer
            or student_lookup is None
            or type(ttl_seconds) is not int
            or not 60 <= ttl_seconds <= 3600
            or type(max_sessions) is not int
            or not 1 <= max_sessions <= 10000
        ):
            raise ValueError("Invalid trusted session configuration.")

        # A snapshot prevents later external dict mutation from granting
        # students access to records through existing browser sessions.
        self._student_lookup = dict(student_lookup)
        self._allowed_issuer = allowed_issuer
        self._ttl_seconds = ttl_seconds
        self._max_sessions = max_sessions
        self._sessions: dict[str, _StoredSession] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _digest(secret: str) -> str:
        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    def issue(
        self, *, verified_access_token: AccessToken | None
    ) -> IssuedStudentWebSession:
        """Issue an opaque session from *previously verified* access context.

        The caller has to verify JWT signature, issuer, audience, scope,
        delegated identity and lifetime before invoking this function.
        This method additionally resolves student authorization and expiry.
        """
        authenticated = session_from_verified_token(
            access_token=verified_access_token,
            student_lookup=self._student_lookup,
            allowed_issuer=self._allowed_issuer,
        )

        expires_at = verified_access_token.expires_at
        now = time.time()
        if (
            type(expires_at) not in (int, float)
            or not math.isfinite(expires_at)
            or expires_at <= now
        ):
            raise PermissionError("Valid expiring token required.")

        # Session expiration never exceeds delegated token expiration.
        deadline = min(now + self._ttl_seconds, float(expires_at))
        cookie = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)

        with self._lock:
            # Expired records do not count against bounded capacity.
            self._sessions = {
                key: item for key, item in self._sessions.items()
                if item.expires_at > now
            }
            if len(self._sessions) >= self._max_sessions:
                raise RuntimeError("Session capacity exceeded.")

            self._sessions[self._digest(cookie)] = _StoredSession(
                authenticated_session=authenticated,
                csrf_digest=hashlib.sha256(
                    csrf.encode("utf-8")
                ).digest(),
                expires_at=deadline,
            )

        return IssuedStudentWebSession(
            cookie_value=cookie,
            csrf_token=csrf,
            expires_at=deadline,
        )

    def resolve(
        self, *, cookie_value: str | None, csrf_token: str | None = None,
        require_csrf: bool = False
    ) -> AuthenticatedStudentSession:
        """Return session only when cookie and optional CSRF proof are valid.

        For state-changing browser operations always require CSRF. GET
        status/CSRF discovery must be same-origin and Cache-Control no-store.
        """
        if (
            not isinstance(cookie_value, str)
            or not 30 <= len(cookie_value) <= 256
            or any(char.isspace() for char in cookie_value)
        ):
            raise PermissionError("Session authentication required.")

        now = time.time()
        key = self._digest(cookie_value)
        with self._lock:
            session = self._sessions.get(key)
            if session is None or session.expires_at <= now:
                if session is not None:
                    del self._sessions[key]
                raise PermissionError("Session authentication required.")

            if require_csrf:
                if (
                    not isinstance(csrf_token, str)
                    or not 30 <= len(csrf_token) <= 256
                ):
                    raise PermissionError("CSRF verification required.")
                actual = hashlib.sha256(
                    csrf_token.encode("utf-8")
                ).digest()
                if not hmac.compare_digest(
                    session.csrf_digest, actual
                ):
                    raise PermissionError("CSRF verification required.")

            return session.authenticated_session

    def rotate_csrf(self, *, cookie_value: str | None) -> str:
        """Issue a fresh browser-only anti-CSRF secret for an active session.

        A same-origin authenticated GET handler may return this secret with
        Cache-Control: no-store. Store only the digest server-side. This
        invalidates earlier CSRF values, including any at session issuance.
        """
        self.resolve(cookie_value=cookie_value)
        key = self._digest(cookie_value)
        with self._lock:
            current = self._sessions.get(key)
            if current is None or current.expires_at <= time.time():
                raise PermissionError("Session authentication required.")

            csrf = secrets.token_urlsafe(32)
            self._sessions[key] = _StoredSession(
                authenticated_session=current.authenticated_session,
                csrf_digest=hashlib.sha256(csrf.encode("utf-8")).digest(),
                expires_at=current.expires_at,
                plan_context=current.plan_context,
            )
            return csrf

    def read_plan_context(
        self,
        *,
        cookie_value: str | None,
        term_id: str,
    ) -> PlanContext | None:
        """Read only this active browser session's context."""
        self.resolve(cookie_value=cookie_value)

        with self._lock:
            current = self._sessions.get(
                self._digest(cookie_value)
            )

            if (
                current is None
                or current.expires_at <= time.time()
            ):
                raise PermissionError(
                    "Session authentication required."
                )

            context = current.plan_context
            if context is None or context.term_id != term_id:
                return None

            return context

    def write_plan_context(
        self,
        *,
        cookie_value: str | None,
        context: PlanContext,
    ) -> None:
        """Store trusted, structured plan data.

        The caller must already have authenticated
        the request and checked CSRF. This method
        is not exposed as an HTTP endpoint.
        """
        if type(context) is not PlanContext:
            raise TypeError("Validated PlanContext required.")

        self.resolve(cookie_value=cookie_value)

        with self._lock:
            key = self._digest(cookie_value)
            current = self._sessions.get(key)

            if (
                current is None
                or current.expires_at <= time.time()
            ):
                raise PermissionError(
                    "Session authentication required."
                )

            self._sessions[key] = replace(
                current, plan_context=context
            )

    def clear_plan_context(
        self,
        *,
        cookie_value: str | None,
    ) -> None:
        """Clear only this active session's plan context."""
        self.resolve(cookie_value=cookie_value)

        with self._lock:
            key = self._digest(cookie_value)
            current = self._sessions.get(key)

            if (
                current is None
                or current.expires_at <= time.time()
            ):
                raise PermissionError(
                    "Session authentication required."
                )

            self._sessions[key] = replace(
                current, plan_context=None
            )

    def revoke(self, *, cookie_value: str | None) -> None:
        """Invalidate an opaque browser session without exposing its token."""
        if not isinstance(cookie_value, str) or not cookie_value:
            return
        key = self._digest(cookie_value)
        with self._lock:
            self._sessions.pop(key, None)

    def count(self) -> int:
        """Diagnostic size only; never expose token/session identifiers."""
        with self._lock:
            return len(self._sessions)
