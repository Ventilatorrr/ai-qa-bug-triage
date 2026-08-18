# Temporary script for database verification. Delete after setup.
import sqlite3

conn = sqlite3.connect("bugtriage.db")

tables = conn.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """
).fetchall()

print(tables, "\n")
##################################################

columns = conn.execute(
    """
    PRAGMA table_info(users)
    """
).fetchall()

for column in columns:
    print(column)

print("\nIndexes:")


##################################################

indexes = conn.execute(
    """
    PRAGMA index_list(users)
    """
).fetchall()

for index in indexes:
    print(index)

print("\nIndex columns:")

##################################################

index_columns = conn.execute(
    """
    PRAGMA index_info('sqlite_autoindex_users_1')
    """
).fetchall()

for column in index_columns:
    print(column)

##################################################

print("\nUsers:")

users = conn.execute(
    """
    SELECT id, email, password_hash
    FROM users
    """
).fetchall()

for user in users:
    print(user)

conn.close()

##################################################
