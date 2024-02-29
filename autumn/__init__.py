import os
import warnings

# Ignore future warnings they're annoying.
warnings.simplefilter(action="ignore", category=FutureWarning)

# Ensure NumPy only uses 1 thread for matrix multiplication,
# because NumPy is stupid and tries to use heaps of threads,
#  which is quite wasteful and makes our models run way more slowly.
# https://stackoverflow.com/questions/30791550/limit-number-of-threads-in-numpy
os.environ["OMP_NUM_THREADS"] = "1"
