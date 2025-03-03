# Generated by ariadne-codegen on 2025-03-05 15:04

from typing import Any

import httpx


class GraphQLClientError(Exception):
    """Base exception."""


class GraphQLClientHttpError(GraphQLClientError):
    def __init__(self, status_code: int, response: httpx.Response) -> None:
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        return f"HTTP status code: {self.status_code}"


class GraphQlClientInvalidResponseError(GraphQLClientError):
    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    def __str__(self) -> str:
        return "Invalid response format."


class GraphQLClientGraphQLError(GraphQLClientError):
    def __init__(
        self,
        message: str,
        locations: list[dict[str, int]] | None = None,
        path: list[str] | None = None,
        extensions: dict[str, object] | None = None,
        orginal: dict[str, object] | None = None,
    ):
        self.message = message
        self.locations = locations
        self.path = path
        self.extensions = extensions
        self.orginal = orginal

    def __str__(self) -> str:
        return self.message

    @classmethod
    def from_dict(cls, error: dict[str, Any]) -> "GraphQLClientGraphQLError":
        return cls(
            message=error["message"],
            locations=error.get("locations"),
            path=error.get("path"),
            extensions=error.get("extensions"),
            orginal=error,
        )


class GraphQLClientGraphQLMultiError(GraphQLClientError):
    def __init__(self, errors: list[GraphQLClientGraphQLError], data: dict[str, Any]):
        self.errors = errors
        self.data = data

    def __str__(self) -> str:
        return "; ".join(str(e) for e in self.errors)

    @classmethod
    def from_errors_dicts(
        cls, errors_dicts: list[dict[str, Any]], data: dict[str, Any]
    ) -> "GraphQLClientGraphQLMultiError":
        return cls(
            errors=[GraphQLClientGraphQLError.from_dict(e) for e in errors_dicts],
            data=data,
        )


class GraphQLClientInvalidMessageFormat(GraphQLClientError):
    def __init__(self, message: str | bytes) -> None:
        self.message = message

    def __str__(self) -> str:
        return "Invalid message format."
