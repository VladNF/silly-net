from environs import Env

env = Env()
env.read_env()

db_user = env.str("POSTGRES_USER", "postgres")
db_password = env.str("POSTGRES_PASSWORD", "postgres")
db_name = env.str("POSTGRES_DB", "snet")
db_host = env.str("POSTGRES_HOST", "localhost")
db_port = env.int("POSTGRES_PORT", 5432)
jwt_algo = env.str("JWT_ALGO", "HS256")
jwt_expire_in_days = env.int("JWT_EXP_IN_DAYS", 5)
jwt_private_key = env.str("JWT_PRIVATE_KEY")
jwt_public_key = env.str("JWT_PUBLIC_KEY")
