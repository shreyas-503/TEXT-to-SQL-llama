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
