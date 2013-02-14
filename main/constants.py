#Status constants
STATUS_GOOD=0
STATUS_UNKNOWN=1
STATUS_BAD=2

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
    ("contains","contains"),
)

PAST_CHECK_CHOICES = (
    ("current","current"),
    ("accumulate","accumulate")
)
