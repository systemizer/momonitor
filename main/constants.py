#Status constants
STATUS_GOOD=0
STATUS_UNKNOWN=1
STATUS_BAD=2

UMPIRE_CHECK_TYPES = (
    ("static","static"),
    ("dynamic","dynamic")
)

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

ALERT_CHOICES = (
    ("pagerduty","pagerduty"),
    ("email","email"),
    ("none","none")
    )
