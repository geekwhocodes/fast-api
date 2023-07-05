import os

from dynaconf import Dynaconf

root_dir = os.path.dirname(os.path.abspath(__file__))


def get_root_dir():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return root_dir


settings = Dynaconf(
    envvar_prefix="opalizer",
    preload=[os.path.join(root_dir, "default.toml")],
    settings_files=[
        "settings.dev.toml",
        "settings.test.toml",
        "settings.prod.toml",
        # ".secrets.toml",
    ],
    environments=["dev", "prod", "test"],
    load_dotenv=True,
    env_switcher="opalizerenv",
)
# db url
settings.db.url = f"postgresql+asyncpg://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.name}"

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order
