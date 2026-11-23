-- E-Compra MySQL Roles and Grants
-- Run as root: mysql -u root -pAdmin2627 ecompra < sql/06_roles_grants.sql
--
-- NOTE (M4.15 fix): Django connects through 127.0.0.1 which MySQL resolves
-- as 'localhost'. The '%' host wildcard does NOT reliably match 'localhost'
-- connections, so the application user is created for '%', 'localhost', and
-- '127.0.0.1' with identical privileges. Do not use role-based grants here:
-- a prior attempt with CREATE ROLE / GRANT role / SET DEFAULT ROLE failed
-- with ERROR 4027 (grant loop); direct GRANT to each user is used instead.

-- Create application user: full CRUD on domain tables, no DDL
CREATE USER IF NOT EXISTS 'ecompra_app'@'%' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_app'@'localhost' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_app'@'127.0.0.1' IDENTIFIED BY 'Admin2627';
GRANT SELECT, INSERT, UPDATE, DELETE ON ecompra.* TO 'ecompra_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON ecompra.* TO 'ecompra_app'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON ecompra.* TO 'ecompra_app'@'127.0.0.1';

-- Create read-only user: SELECT only
CREATE USER IF NOT EXISTS 'ecompra_readonly'@'%' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_readonly'@'localhost' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_readonly'@'127.0.0.1' IDENTIFIED BY 'Admin2627';
GRANT SELECT ON ecompra.* TO 'ecompra_readonly'@'%';
GRANT SELECT ON ecompra.* TO 'ecompra_readonly'@'localhost';
GRANT SELECT ON ecompra.* TO 'ecompra_readonly'@'127.0.0.1';

-- Create admin user: full privileges including DDL
CREATE USER IF NOT EXISTS 'ecompra_admin'@'%' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_admin'@'localhost' IDENTIFIED BY 'Admin2627';
CREATE USER IF NOT EXISTS 'ecompra_admin'@'127.0.0.1' IDENTIFIED BY 'Admin2627';
GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_admin'@'%';
GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_admin'@'localhost';
GRANT ALL PRIVILEGES ON ecompra.* TO 'ecompra_admin'@'127.0.0.1';

FLUSH PRIVILEGES;
