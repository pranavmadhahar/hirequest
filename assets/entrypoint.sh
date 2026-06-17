#!/bin/bash
set -e

echo "Step 1: Preprocessing raw data..."
python src/assets/build/preprocess.py

echo "Step 2: Building chunks..."
python src/assets/build/chunks_builder.py

echo "Step 3: Building FAISS index..."
python src/assets/build/index_builder.py

echo "✅ Assets pipeline complete."
