"""Tests for philiprehberger_sql_print."""

from __future__ import annotations

import io

import pytest

from philiprehberger_sql_print import format_sql, print_sql


def test_simple_select_formatting() -> None:
    sql = "SELECT id, name FROM users WHERE active = 1"
    result = format_sql(sql)
    lines = result.split("\n")
    assert lines[0].startswith("SELECT")
    assert any(line.startswith("FROM") for line in lines)
    assert any(line.startswith("WHERE") for line in lines)


def test_left_join_formatting() -> None:
    sql = "SELECT * FROM orders LEFT JOIN users ON orders.user_id = users.id"
    result = format_sql(sql)
    assert "LEFT JOIN" in result
    assert "\n" in result


def test_inner_join_formatting() -> None:
    sql = "SELECT a.id FROM a INNER JOIN b ON a.id = b.a_id"
    result = format_sql(sql)
    assert "INNER JOIN" in result


def test_and_or_indented_under_where() -> None:
    sql = "SELECT id FROM users WHERE active = 1 AND role = 'admin' OR status = 'vip'"
    result = format_sql(sql)
    lines = result.split("\n")
    and_lines = [line for line in lines if "AND" in line]
    or_lines = [line for line in lines if "OR" in line]
    for line in and_lines + or_lines:
        assert line.startswith("  ") or line.startswith(" ")


def test_insert_into_formatting() -> None:
    sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
    result = format_sql(sql)
    assert "INSERT INTO" in result
    assert "VALUES" in result


def test_update_set_formatting() -> None:
    sql = "UPDATE users SET name = 'Bob' WHERE id = 1"
    result = format_sql(sql)
    assert "UPDATE" in result
    assert "SET" in result
    assert "WHERE" in result


def test_delete_from_formatting() -> None:
    sql = "DELETE FROM users WHERE id = 1"
    result = format_sql(sql)
    assert "DELETE FROM" in result
    assert "WHERE" in result


def test_order_by_group_by_having_limit() -> None:
    sql = "SELECT role, count(*) FROM users GROUP BY role HAVING count(*) > 1 ORDER BY role LIMIT 10"
    result = format_sql(sql)
    assert "GROUP BY" in result
    assert "HAVING" in result
    assert "ORDER BY" in result
    assert "LIMIT" in result


def test_uppercase_true_by_default() -> None:
    sql = "select id from users where active = 1"
    result = format_sql(sql)
    assert "SELECT" in result
    assert "FROM" in result
    assert "WHERE" in result


def test_uppercase_false_preserves_case() -> None:
    sql = "select id from users where active = 1"
    result = format_sql(sql, uppercase=False)
    assert "select" in result
    assert "from" in result
    assert "where" in result


def test_indent_parameter() -> None:
    sql = "SELECT id FROM users WHERE active = 1 AND role = 'admin'"
    result_2 = format_sql(sql, indent=2)
    result_4 = format_sql(sql, indent=4)
    and_line_2 = [line for line in result_2.split("\n") if "AND" in line][0]
    and_line_4 = [line for line in result_4.split("\n") if "AND" in line][0]
    indent_2 = len(and_line_2) - len(and_line_2.lstrip())
    indent_4 = len(and_line_4) - len(and_line_4.lstrip())
    assert indent_4 > indent_2


def test_empty_string() -> None:
    assert format_sql("") == ""


def test_idempotent_formatting() -> None:
    sql = "SELECT id, name FROM users WHERE active = 1"
    first = format_sql(sql)
    second = format_sql(first)
    assert first == second


def test_string_literals_preserved() -> None:
    sql = "SELECT id FROM users WHERE name = 'select from where'"
    result = format_sql(sql)
    assert "'select from where'" in result


def test_print_sql_outputs_to_stream() -> None:
    buf = io.StringIO()
    print_sql("SELECT id FROM users", color=False, file=buf)
    output = buf.getvalue()
    assert "SELECT" in output
    assert "FROM" in output


def test_subquery_with_parentheses() -> None:
    sql = "SELECT id FROM users WHERE id IN (SELECT user_id FROM orders)"
    result = format_sql(sql)
    assert "(" in result
    assert ")" in result
    assert "SELECT" in result
