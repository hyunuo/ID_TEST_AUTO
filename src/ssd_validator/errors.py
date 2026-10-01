"""Actionable knowledge/build errors, separate from device validation results."""


class KnowledgeError(ValueError):
    def __init__(self, code: str, message: str, *, source: str | None = None):
        self.code = code
        self.source = source
        self.message = message
        super().__init__(f"{code}: {source + ': ' if source else ''}{message}")
