# philiprehberger-sql-print

Pretty-print and format SQL queries for debugging.

## Installation

```bash
pip install philiprehberger-sql-print
```

## Usage

### Format SQL

```python
from philiprehberger_sql_print import format_sql

query = "SELECT id, name FROM users WHERE active = 1 AND role = 'admin' ORDER BY name"
print(format_sql(query))
```

Output:

```sql
SELECT id, name
FROM users
WHERE active = 1
  AND role = 'admin'
ORDER BY name
```

### Print SQL with syntax highlighting

```python
from philiprehberger_sql_print import print_sql

print_sql("SELECT * FROM orders LEFT JOIN users ON orders.user_id = users.id WHERE total > 100")
```

Prints formatted SQL with ANSI color-coded keywords, strings, and numbers.

### Disable colors or uppercase

```python
from philiprehberger_sql_print import print_sql

# No ANSI colors (useful for logging)
print_sql("select id from users", color=False)

# Preserve original keyword casing
print_sql("select id from users", uppercase=False)
```

### Custom indentation

```python
from philiprehberger_sql_print import format_sql

print(format_sql("SELECT id FROM users WHERE active = 1", indent=4))
```

## API

| Function | Description |
|---|---|
| `format_sql(sql, *, indent=2, uppercase=True) -> str` | Format a SQL query with newlines and indentation. |
| `print_sql(sql, *, indent=2, uppercase=True, color=True, file=None) -> None` | Print a formatted SQL query with optional ANSI syntax highlighting. |

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sql` | `str` | — | The SQL query string to format. |
| `indent` | `int` | `2` | Number of spaces for indentation. |
| `uppercase` | `bool` | `True` | Whether to uppercase SQL keywords. |
| `color` | `bool` | `True` | Whether to apply ANSI color codes (print_sql only). |
| `file` | `TextIO \| None` | `None` | Output stream. Defaults to sys.stdout (print_sql only). |

## License

MIT
