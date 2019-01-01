"""Pretty-print and format SQL queries for debugging."""

from __future__ import annotations

import re
import sys
from typing import TextIO

__all__ = ["format_sql", "print_sql"]

_KEYWORDS = (
    "SELECT", "FROM", "WHERE", "AND", "OR",
    "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN",
    "FULL OUTER JOIN", "CROSS JOIN",
    "ON", "ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET",
    "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM",
    "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
    "UNION", "UNION ALL", "EXCEPT", "INTERSECT",
    "CASE", "WHEN", "THEN", "ELSE", "END",
    "AS", "IN", "NOT", "IS", "NULL", "BETWEEN", "LIKE", "EXISTS",
    "DISTINCT", "INTO", "RETURNING",
)

# Keywords that trigger a newline before them
_NEWLINE_BEFORE = {
    "SELECT", "FROM", "WHERE", "AND", "OR",
    "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN",
    "FULL OUTER JOIN", "CROSS JOIN",
    "ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET",
    "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM",
    "UNION", "UNION ALL", "EXCEPT", "INTERSECT",
    "ON", "RETURNING",
}

# Keywords that get indented (clauses subordinate to the main keyword)
_INDENT_KEYWORDS = {"AND", "OR", "ON"}

# ANSI color codes for syntax highlighting
_COLORS = {
    "keyword": "\033[1;34m",   # bold blue
    "string": "\033[32m",      # green
    "number": "\033[33m",      # yellow
    "reset": "\033[0m",
}


def format_sql(sql: str, *, indent: int = 2, uppercase: bool = True) -> str:
    """Format a SQL query with newlines and indentation.

    Args:
        sql: The SQL query string to format.
        indent: Number of spaces for indentation.
        uppercase: Whether to uppercase SQL keywords.
    """
    # Normalize whitespace
    normalized = " ".join(sql.split())

    tokens = _tokenize(normalized)
    lines: list[str] = []
    current_line: list[str] = []
    indent_str = " " * indent
    depth = 0

    i = 0
    while i < len(tokens):
        token = tokens[i]
        upper = token.upper().strip()

        # Check for multi-word keywords
        multi = _match_multi_keyword(tokens, i)
        if multi:
            upper = multi.upper()
            token = multi
            i += len(multi.split()) - 1

        if upper in _NEWLINE_BEFORE:
            if current_line:
                lines.append(indent_str * depth + " ".join(current_line))
                current_line = []
            if upper in _INDENT_KEYWORDS:
                current_line.append(indent_str + (_apply_case(token, uppercase)))
            else:
                current_line.append(_apply_case(token, uppercase))
        elif upper == "(":
            current_line.append(token)
            depth += 1
        elif upper == ")":
            depth = max(0, depth - 1)
            current_line.append(token)
        else:
            kw = _apply_case(token, uppercase) if upper in {k.upper() for k in _KEYWORDS} else token
            current_line.append(kw)

        i += 1

    if current_line:
        lines.append(indent_str * depth + " ".join(current_line))

    return "\n".join(lines)


def print_sql(sql: str, *, indent: int = 2, uppercase: bool = True, color: bool = True, file: TextIO | None = None) -> None:
    """Print a formatted SQL query with optional syntax highlighting.

    Args:
        sql: The SQL query string.
        indent: Number of spaces for indentation.
        uppercase: Whether to uppercase SQL keywords.
        color: Whether to apply ANSI color codes.
        file: Output stream. Defaults to sys.stdout.
    """
    formatted = format_sql(sql, indent=indent, uppercase=uppercase)
    if color:
        formatted = _colorize(formatted)
    print(formatted, file=file or sys.stdout)


def _tokenize(sql: str) -> list[str]:
    """Split SQL into tokens, preserving strings and parentheses."""
    tokens: list[str] = []
    current = ""
    i = 0
    while i < len(sql):
        char = sql[i]
        if char in ("'", '"'):
            if current.strip():
                tokens.append(current.strip())
                current = ""
            quote = char
            string = char
            i += 1
            while i < len(sql) and sql[i] != quote:
                string += sql[i]
                i += 1
            if i < len(sql):
                string += sql[i]
            tokens.append(string)
            i += 1
            continue
        if char in ("(", ")"):
            if current.strip():
                tokens.append(current.strip())
                current = ""
            tokens.append(char)
            i += 1
            continue
        if char == ",":
            if current.strip():
                tokens.append(current.strip())
                current = ""
            tokens.append(",")
            i += 1
            continue
        if char == " ":
            if current.strip():
                tokens.append(current.strip())
                current = ""
            i += 1
            continue
        current += char
        i += 1
    if current.strip():
        tokens.append(current.strip())
    return tokens


def _match_multi_keyword(tokens: list[str], start: int) -> str | None:
    """Check if tokens starting at `start` form a multi-word keyword."""
    multi_keywords = [
        "FULL OUTER JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
        "OUTER JOIN", "CROSS JOIN", "ORDER BY", "GROUP BY",
        "INSERT INTO", "DELETE FROM", "UNION ALL",
        "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
    ]
    for kw in multi_keywords:
        parts = kw.split()
        if start + len(parts) <= len(tokens):
            candidate = " ".join(tokens[start:start + len(parts)])
            if candidate.upper() == kw:
                return candidate
    return None


def _apply_case(token: str, uppercase: bool) -> str:
    return token.upper() if uppercase else token


def _colorize(sql: str) -> str:
    """Apply ANSI colors to formatted SQL."""
    all_kw = {k.upper() for k in _KEYWORDS}
    words = sql.split(" ")
    result: list[str] = []
    for word in words:
        stripped = word.strip()
        if stripped.upper() in all_kw:
            result.append(f"{_COLORS['keyword']}{word}{_COLORS['reset']}")
        elif stripped.startswith("'") or stripped.startswith('"'):
            result.append(f"{_COLORS['string']}{word}{_COLORS['reset']}")
        elif re.match(r"^\d+\.?\d*$", stripped):
            result.append(f"{_COLORS['number']}{word}{_COLORS['reset']}")
        else:
            result.append(word)
    return " ".join(result)
