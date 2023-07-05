import re

from unidecode import unidecode


def slugify(s):
    """Slugify the string
    :param s: string value
    """
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def generate_tenant_schema_name(name: str) -> str:
    company = re.sub("[^A-Za-z0-9 _]", "", unidecode(name))
    return "".join([company[:28]]).lower().replace(" ", "_")
