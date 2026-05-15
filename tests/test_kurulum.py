print("Sistem kurulum testi basliyor...\n")

try:
    import pandas as pd
    print(f"OK  pandas          {pd.__version__}")

    import numpy as np
    print(f"OK  numpy           {np.__version__}")

    import pymongo
    print(f"OK  pymongo         {pymongo.__version__}")

    import flask
    print(f"OK  flask           {flask.__version__}")


    import sklearn
    print(f"OK  scikit-learn    {sklearn.__version__}")

    import imblearn
    print(f"OK  imbalanced-learn {imblearn.__version__}")

    print("\nTum bagimliliklar hazir.")

except ImportError as e:
    print(f"\nHATA: Eksik veya hatali kutuphane: {e}")
    print("  'pip install -r requirements.txt' komutunu calistirin.")
