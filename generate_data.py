import sqlite3
import random
from faker import Faker

fake = Faker("en_IN")

# --- CONNECT TO DB ---
conn = sqlite3.connect("pharmacy.db")
cur = conn.cursor()

# --- CONFIG (bigger dataset) ---
NUM_SUPPLIERS = 30
NUM_MEDICINES = 100
NUM_CUSTOMERS = 100
NUM_DOCTORS = 30
NUM_PRESCRIPTIONS = 200
NUM_SALES = 300

# --- SUPPLIERS ---
suppliers = []
for _ in range(NUM_SUPPLIERS):
    name = fake.unique.company()
    phone = "+91" + str(random.randint(6000000000, 9999999999))
    email = name.replace(" ", "").lower() + "@pharma.in"
    cur.execute("INSERT INTO suppliers (supplier_name, phone, email) VALUES (?,?,?)",
                (name, phone, email))
    suppliers.append(cur.lastrowid)

# --- MEDICINES ---
categories = ["Antibiotic", "Analgesic", "Antipyretic", "Antacid", "Antihistamine",
              "Antifungal", "Cardiac", "Diabetic", "Respiratory", "Dermatology"]
brands = ["Cipla", "Sun Pharma", "Lupin", "Dr. Reddy's", "Zydus Cadila", "Glenmark", "Torrent Pharma"]

medicines = []
for _ in range(NUM_MEDICINES):
    name = fake.unique.lexify(text="Med????").capitalize()
    brand = random.choice(brands)
    category = random.choice(categories)
    unit_price = round(random.uniform(5, 2000), 2)  # bigger range
    expiry = fake.date_between(start_date="+6m", end_date="+5y").isoformat()
    cur.execute("INSERT INTO medicines (medicine_name, brand, category, unit_price, expiry_date) VALUES (?,?,?,?,?)",
                (name, brand, category, unit_price, expiry))
    medicines.append(cur.lastrowid)

# --- STOCK (supplier ↔ medicine) ---
for supplier_id in suppliers:
    for med_id in random.sample(medicines, k=random.randint(15, 30)):  # bigger stock
        quantity = random.randint(100, 2000)
        cur.execute("INSERT OR IGNORE INTO stock (supplier_id, medicine_id, quantity) VALUES (?,?,?)",
                    (supplier_id, med_id, quantity))

# --- CUSTOMERS ---
customers = []
for _ in range(NUM_CUSTOMERS):
    name = fake.name()
    phone = "+91" + str(random.randint(7000000000, 9999999999))
    email = name.replace(" ", "").lower() + str(random.randint(10,99)) + "@gmail.com"
    cur.execute("INSERT INTO customers (name, phone, email) VALUES (?,?,?)",
                (name, phone, email))
    customers.append(cur.lastrowid)

# --- DOCTORS ---
specializations = ["General Physician", "Pediatrician", "Cardiologist", "Dermatologist", 
                   "Orthopedic", "Endocrinologist", "Neurologist", "Oncologist"]
doctors = []
for _ in range(NUM_DOCTORS):
    name = "Dr. " + fake.name()
    specialization = random.choice(specializations)
    cur.execute("INSERT INTO doctors (doctor_name, specialization) VALUES (?,?)",
                (name, specialization))
    doctors.append(cur.lastrowid)

# --- PRESCRIPTIONS ---
prescriptions = []
for _ in range(NUM_PRESCRIPTIONS):
    doctor_id = random.choice(doctors)
    customer_id = random.choice(customers)
    date = fake.date_between(start_date="-2y", end_date="today").isoformat()
    cur.execute("INSERT INTO prescriptions (doctor_id, customer_id, date) VALUES (?,?,?)",
                (doctor_id, customer_id, date))
    pres_id = cur.lastrowid
    prescriptions.append(pres_id)

    # prescription details
    for med_id in random.sample(medicines, k=random.randint(1, 4)):
        dosage = f"{random.randint(1,2)} tablet(s) {random.choice(['OD','BD','TDS'])}"
        duration = random.randint(5, 30)
        cur.execute("INSERT INTO prescription_details (prescription_id, medicine_id, dosage, duration_days) VALUES (?,?,?,?)",
                    (pres_id, med_id, dosage, duration))

# --- SALES ---
sales = []
for _ in range(NUM_SALES):
    customer_id = random.choice(customers)
    date = fake.date_between(start_date="-2y", end_date="today").isoformat()
    cur.execute("INSERT INTO sales (customer_id, sale_date) VALUES (?,?)",
                (customer_id, date))
    sale_id = cur.lastrowid
    sales.append(sale_id)

    # sale details
    total = 0
    for med_id in random.sample(medicines, k=random.randint(1, 6)):
        quantity = random.randint(1, 10)
        price = cur.execute("SELECT unit_price FROM medicines WHERE medicine_id=?", (med_id,)).fetchone()[0]
        total += price * quantity
        cur.execute("INSERT INTO sale_details (sale_id, medicine_id, quantity, price) VALUES (?,?,?,?)",
                    (sale_id, med_id, quantity, price))

    # payment
    payment_mode = random.choice(["Cash","UPI","Card","NetBanking"])
    cur.execute("INSERT INTO payments (sale_id, amount, payment_mode, payment_date) VALUES (?,?,?,?)",
                (sale_id, round(total,2), payment_mode, date))

conn.commit()
conn.close()

print("data generated successfully!")
