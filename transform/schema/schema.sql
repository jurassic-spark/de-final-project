Drop TABLE IF EXISTS dim_staff
Drop TABLE IF EXISTS dim_location
Drop TABLE IF EXISTS dim_currency
Drop TABLE IF EXISTS dim_design
Drop TABLE IF EXISTS dim_counterparty


CREATE TABLE "fact_sales_order" (
  "sales_record_id" SERIAL PRIMARY KEY,
  "sales_order_id" int NOT NULL,
  "created_date" date NOT NULL,
  "created_time" time NOT NULL,
  "last_updated_date" date NOT NULL,
  "last_updated_time" time NOT NULL,
  "sales_staff_id" int NOT NULL,
  "counterparty_id" int NOT NULL,
  "units_sold" int NOT NULL,
  "unit_price" "numeric(10, 2)" NOT NULL,
  "currency_id" int NOT NULL,
  "design_id" int NOT NULL,
  "agreed_payment_date" date NOT NULL,
  "agreed_delivery_date" date NOT NULL,
  "agreed_delivery_location_id" int NOT NULL
);

CREATE TABLE "dim_date" (
  "date_id" date PRIMARY KEY NOT NULL,
  "year" int NOT NULL,
  "month" int NOT NULL,
  "day" int NOT NULL,
  "day_of_week" int NOT NULL,
  "day_name" varchar NOT NULL,
  "month_name" varchar NOT NULL,
  "quarter" int NOT NULL
);

CREATE TABLE "dim_staff" (
  "staff_id" int PRIMARY KEY NOT NULL,
  "first_name" varchar NOT NULL,
  "last_name" varchar NOT NULL,
  "department_name" varchar NOT NULL,
  "location" varchar NOT NULL,
  "email_address" email_address NOT NULL
);

CREATE TABLE "dim_location" (
  "location_id" int PRIMARY KEY NOT NULL,
  "address_line_1" varchar NOT NULL,
  "address_line_2" varchar,
  "district" varchar,
  "city" varchar NOT NULL,
  "postal_code" varchar NOT NULL,
  "country" varchar NOT NULL,
  "phone" varchar NOT NULL
);

CREATE TABLE "dim_currency" (
  "currency_id" int PRIMARY KEY NOT NULL,
  "currency_code" varchar NOT NULL,
  "currency_name" varchar NOT NULL
);

CREATE TABLE "dim_design" (
  "design_id" int PRIMARY KEY NOT NULL,
  "design_name" varchar NOT NULL,
  "file_location" varchar NOT NULL,
  "file_name" varchar NOT NULL
);

CREATE TABLE "dim_counterparty" (
  "counterparty_id" int PRIMARY KEY NOT NULL,
  "counterparty_legal_name" varchar NOT NULL,
  "counterparty_legal_address_line_1" varchar NOT NULL,
  "counterparty_legal_address_line_2" varchar,
  "counterparty_legal_district" varchar,
  "counterparty_legal_city" varchar NOT NULL,
  "counterparty_legal_postal_code" varchar NOT NULL,
  "counterparty_legal_country" varchar NOT NULL,
  "counterparty_legal_phone_number" varchar NOT NULL
);

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("created_date") REFERENCES "dim_date" ("date_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("last_updated_date") REFERENCES "dim_date" ("date_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("sales_staff_id") REFERENCES "dim_staff" ("staff_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("counterparty_id") REFERENCES "dim_counterparty" ("counterparty_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("currency_id") REFERENCES "dim_currency" ("currency_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("design_id") REFERENCES "dim_design" ("design_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("agreed_payment_date") REFERENCES "dim_date" ("date_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("agreed_delivery_date") REFERENCES "dim_date" ("date_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_sales_order" ADD FOREIGN KEY ("agreed_delivery_location_id") REFERENCES "dim_location" ("location_id") DEFERRABLE INITIALLY IMMEDIATE;
