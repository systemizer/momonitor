#Status constants
STATUS_GOOD=0
STATUS_BAD=1
STATUS_UNKNOWN=2

SERIALIZATION_CHOICES = (
    ("json","json"),
    ("plaintext","plaintext"),
)

COMPARATOR_CHOICES = (
    ("==","=="),
    ("!=","!="),
    (">",">"),
    (">=",">="),
    ("<","<"),
    ("<=","<="),
)
