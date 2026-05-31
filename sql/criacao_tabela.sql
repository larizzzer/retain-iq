CREATE TABLE customers 
(
    row_number       INTEGER,
    customer_id      BIGINT PRIMARY KEY,
    surname          VARCHAR(100),
    credit_score     INTEGER,
    geography        VARCHAR(50),
    gender           VARCHAR(10),
    age              INTEGER,
    tenure           INTEGER,
    balance          NUMERIC(15,2),
    num_of_products  INTEGER,
    has_cr_card      BOOLEAN,
    is_active_member BOOLEAN,
    estimated_salary NUMERIC(15,2),
    exited           BOOLEAN
);