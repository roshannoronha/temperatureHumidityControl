CREATE TABLE IF NOT EXISTS batches (
	id bigserial PRIMARY KEY UNIQUE,
	name text NOT NULL UNIQUE,
	location text,
	created timestamp with time zone NOT NULL
);

CREATE INDEX IF NOT EXISTS created_index ON batches (created);

CREATE TABLE IF NOT EXISTS sensor_data (
	id bigserial PRIMARY KEY UNIQUE,
	ts timestamp with time zone,
	temp NUMERIC(12, 6),
	humidity NUMERIC(9, 6),
	batch bigserial REFERENCES batches(id)
);

CREATE INDEX IF NOT EXISTS sensor_id_index ON sensor_data (batch);
CREATE INDEX IF NOT EXISTS ts_index ON sensor_data (ts);

CREATE TABLE IF NOT EXISTS users (
	login text PRIMARY KEY UNIQUE,
	password bytea,
	is_admin boolean
);
