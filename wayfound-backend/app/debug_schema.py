# app/debug_schema.py - Run this to see what's in the schema
from app.schemas.graphql_schema import schema

print("=== SCHEMA DEBUG ===")
print("Query fields:")
for field_name, field in schema.query_type.fields.items():
    print(f"  - {field_name}: {field}")

print("\nMutation fields:")
if schema.mutation_type:
    for field_name, field in schema.mutation_type.fields.items():
        print(f"  - {field_name}: {field}")
else:
    print("  No mutations found!")

print("\nFull schema:")
print(schema)