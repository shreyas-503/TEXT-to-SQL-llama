import subprocess
from sqlalchemy import create_engine, text
from tabulate import tabulate  

engine = create_engine("sqlite:///pharmacy.db")

SYSTEM_PROMPT = """
You are a Pharmacy Database Assistant.
You receive questions in natural language and return ONLY a valid SQL query for the SQLite database.
Use these exact tables and columns (snake_case):

this is the schema :
-- SUPPLIERS
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT NOT NULL UNIQUE,
    phone TEXT,
    email TEXT
);

-- MEDICINES
CREATE TABLE medicines (
    medicine_id INTEGER PRIMARY KEY,
    medicine_name TEXT NOT NULL,
    brand TEXT,
    category TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    expiry_date DATE NOT NULL
);

-- STOCK (many-to-many: supplier ↔ medicine)
CREATE TABLE stock (
    stock_id INTEGER PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
    medicine_id INTEGER NOT NULL REFERENCES medicines(medicine_id),
    quantity INTEGER NOT NULL,
    CONSTRAINT uq_stock UNIQUE (supplier_id, medicine_id)
);

-- CUSTOMERS
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT UNIQUE
);

-- DOCTORS
CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY,
    doctor_name TEXT NOT NULL,
    specialization TEXT
);

-- PRESCRIPTIONS
CREATE TABLE prescriptions (
    prescription_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(doctor_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    date DATE DEFAULT CURRENT_DATE
);

-- PRESCRIPTION DETAILS (many-to-many)
CREATE TABLE prescription_details (
    id INTEGER PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(prescription_id),
    medicine_id INTEGER NOT NULL REFERENCES medicines(medicine_id),
    dosage TEXT NOT NULL,
    duration_days INTEGER NOT NULL
);

-- SALES
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    sale_date DATE DEFAULT CURRENT_DATE
);

-- SALE DETAILS
CREATE TABLE sale_details (
    id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(sale_id),
    medicine_id INTEGER NOT NULL REFERENCES medicines(medicine_id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- PAYMENTS
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(sale_id),
    amount DECIMAL(10,2) NOT NULL,
    payment_mode TEXT CHECK(payment_mode IN ('Cash','UPI','Card','NetBanking')),
    payment_date DATE DEFAULT CURRENT_DATE
);



Strict rules:
- Use exact column and table names (snake_case).
- Only return SQL, no explanation.
- Use proper WHERE clauses with existing columns.
- Never use non-existent columns like sale_time, full_name, prescription_id in sale_details, etc.
"""

def run_sql(sql):
    with engine.connect() as conn:
        try:
            if sql.strip().lower().startswith(("select", "with")):
                rows = conn.execute(text(sql)).mappings().all()
                return [dict(r) for r in rows]
            else:
                with conn.begin():
                    conn.execute(text(sql))
                return [{"status": "Query executed successfully"}]
        except Exception as e:
            return [{"error": str(e)}]

import re

def clean_sql(output: str) -> str:
    sql = output.replace("\\n", "\n")
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.strip()

    match = re.search(r"\b(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|DROP)\b", sql, re.IGNORECASE)
    if match:
        sql = sql[match.start():].strip()

    if ";" in sql:
        sql = sql.split(";")[0] + ";"

    return sql


def call_llama(user_question):
    prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_question}\nSQL:"
    result = subprocess.run(
        ["ollama", "run", "llama3:8b"],  
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw_output = result.stdout.decode().strip()
    return clean_sql(raw_output)

if __name__ == "__main__":
    print("Pharmacy Agent . Ctrl+C to exit.")
    while True:
        try:
            q = input("\nYou: ")
            sql = call_llama(q)
            print("\nGenerated SQL:\n", sql)

            rows = run_sql(sql)
            if rows and "error" not in rows[0]:
                print("\nResult:\n", tabulate(rows, headers="keys", tablefmt="psql"))
            else:
                print("SQL Error:", rows[0]["error"])
        except KeyboardInterrupt:
            print("\nBye!")

            break
