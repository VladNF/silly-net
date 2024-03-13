from environs import Env

env = Env()
env.read_env()

db_user = env.str("POSTGRES_USER", "postgres")
db_password = env.str("POSTGRES_PASSWORD", "postgres")
db_name = env.str("POSTGRES_DB", "snet")
db_host = env.str("POSTGRES_HOST", "localhost")
db_port = env.int("POSTGRES_PORT", 5432)
db_ro_user = env.str("POSTGRES_RO_USER", db_user)
db_ro_password = env.str("POSTGRES_RO_PASSWORD", db_password)
db_ro_name = env.str("POSTGRES_RO_DB", db_name)
db_ro_host = env.str("POSTGRES_RO_HOST", db_host)
db_ro_port = env.int("POSTGRES_RO_PORT", db_port)
db_dsn_rw = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
db_dsn_ro = f"postgresql://{db_ro_user}:{db_ro_password}@{db_ro_host}:{db_ro_port}/{db_ro_name}"
jwt_algo = env.str("JWT_ALGO", "HS256")
jwt_expire_in_days = env.int("JWT_EXP_IN_DAYS", 5)
jwt_private_key = env.str("JWT_PRIVATE_KEY")
jwt_public_key = env.str("JWT_PUBLIC_KEY")
