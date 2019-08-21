-- Initialization of DappStoreBackend Postgres
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT                       -- SELECT list can stay empty for this
      FROM   pg_catalog.pg_roles
      WHERE  rolname = 'dev') THEN
      CREATE USER dev;
   END IF;
END
$do$;

-- MASTER DATABASE FOR ALL DAPPS
-- TODO: add logic to check if database exists
-- CREATE DATABASE "dappstore";

GRANT ALL PRIVILEGES ON DATABASE "dappstore" TO postgres;
GRANT ALL PRIVILEGES ON DATABASE "dappstore" TO dev;
