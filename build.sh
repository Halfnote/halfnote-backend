#!/bin/bash
set -e

echo "Building React frontend..."
cd frontend

# Clean install without cache issues
rm -rf node_modules/.cache || true
npm install
npm run build
cd ..

echo "React build completed successfully!"
ls -la frontend/build/ 