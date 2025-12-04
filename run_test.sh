#!/bin/bash
# filepath: /Users/ichan-yeong/IdeaProjects/rabbit-mq/run_test.sh

# File Scanner Test Runner
# This script creates test files, scans them, and reads the results from RabbitMQ

set -e  # Exit on error

echo "============================================"
echo "File Scanner - Full Test Run"
echo "============================================"
echo ""

# Step 0: Start RabbitMQ
echo "🐰 Step 0: Starting RabbitMQ..."
echo "--------------------------------------------"
docker compose up -d
echo "Waiting for RabbitMQ to be ready..."
sleep 5
echo ""

# Step 1: Generate test files
echo "📁 Step 1: Generating test files..."
echo "--------------------------------------------"
cd src/utils
python make_files.py
echo ""

# Step 2: Scan files and send to RabbitMQ
echo "🔍 Step 2: Scanning files and sending to RabbitMQ..."
echo "--------------------------------------------"
cd ../
python file_scanner.py --input-dirs test_files --log-level INFO
echo ""

# Step 3: Read messages from RabbitMQ
echo "📨 Step 3: Reading messages from RabbitMQ..."
echo "--------------------------------------------"
cd utils
python read_messages.py --count 10
echo ""

# Cleanup
echo "🧹 Cleaning up test files and stopping RabbitMQ..."
cd ../../
rm -rf test_files


echo "============================================"
echo "Test run completed successfully!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  - Check file_scanner.log for detailed logs"
echo "  - Visit http://localhost:15672 for RabbitMQ UI"
echo "  - Run 'python read_messages.py --count 20' to see more messages"
echo " run docker compose down to stop RabbitMQ"