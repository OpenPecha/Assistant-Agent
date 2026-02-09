class LLMError(Exception):
    """Base exception for LLM routing/provider issues."""


class UnsupportedModelError(LLMError, ValueError):
    """Raised when a model name is not in the registry."""


class ModelUnavailableError(LLMError, RuntimeError):
    """Raised when a model exists but cannot be used (missing credentials, etc.)."""


class ProviderInvocationError(LLMError, RuntimeError):
    """Raised when a provider call fails at runtime."""
