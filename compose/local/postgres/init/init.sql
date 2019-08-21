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

-- Grant privileges to test DB
-- Test DB is automatically created via docker
GRANT ALL PRIVILEGES ON DATABASE "test" TO postgres;
GRANT ALL PRIVILEGES ON DATABASE "test" to dev;
