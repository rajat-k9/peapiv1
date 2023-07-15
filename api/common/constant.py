CATEGORY_CHOICES =(
    ("wire", "Wire Cable"),
    ("board", "Distribution Board"),
    ("china_light", "China Light"),
)
ORDER_TYPES=(
    ("purchase","Purchase"),
    ("sale","Sale"),
    ("sale_return","Sale Return"),
    ("purchase_return","Purchase Return")
)
PAYMENT_TYPE_CHOICES =(
    ("income", "Payment In(income)"),
    ("expense", "Payment Out(expense)"),
    ("stock_in", "Stock In(debit)"),
)
PAYMENT_MODE_CHOICES =(
    ("cash", "Cash"),
    ("cheque", "Cheque"),
    ("bank transfer", "Bank Transfer(NEFT/RTGS)"),
)
WAREHOUSE_CHOICES=(
    ("shop","Shop"),
    ("home","Home"),
    ("po_godown", "Post Office Godown"),
    ("colony","Teacher Colony Godown"),
    ("hameerpur","Hameerpur Road")
)