"""Smoke test cho môi trường Python và dependencies"""
import sys, platform
import numpy as np
import pandas as pd
import sklearn
import simpy


def test_environment():
    """Test tất cả dependencies có sẵn và hoạt động"""
    print("\n🔍 Environment Info:")
    print("PY:", sys.executable)
    print("OS:", platform.platform())
    print("numpy:", np.__version__)
    print("pandas:", pd.__version__)
    print("sklearn:", sklearn.__version__)
    print("simpy:", simpy.__version__)

    # Thử phép tính với numpy
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = a @ b
    print("dot(a,b):", result)
    
    assert result == 32, "Numpy dot product should be 32"
    print("✅ Environment OK")
