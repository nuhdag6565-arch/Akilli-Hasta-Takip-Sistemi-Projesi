print("Sistem testi basliyor...\n")

try:
    import pandas as pd
    print(f"✅ Pandas calisiyor! Surum: {pd.__version__}")
    
    import numpy as np
    print(f"✅ Numpy calisiyor! Surum: {np.__version__}")
    
    import pymongo
    print(f"✅ PyMongo calisiyor! Surum: {pymongo.__version__}")
    
    import fastapi
    print(f"✅ FastAPI calisiyor! Surum: {fastapi.__version__}")
    
    import sklearn
    print(f"✅ Scikit-Learn calisiyor! Surum: {sklearn.__version__}")
    
    import tensorflow as tf
    print(f"✅ TensorFlow calisiyor! Surum: {tf.__version__}")

    print("\n🎉 HARIKA! Tum ana kutuphaneler basariyla yuklendi ve calisiyor.")

except ImportError as e:
    print(f"\n❌ HATA: Kutuphanelerden biri eksik veya hatali: {e}")