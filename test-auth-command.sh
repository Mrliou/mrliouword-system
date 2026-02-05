#!/bin/bash
# test-auth-command.sh
# Simulates the gt auth --token command behavior

TOKEN=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            TOKEN="$2"
            shift 2
            ;;
        *)
            echo "Usage: gt auth --token <token>"
            exit 1
            ;;
    esac
done

# Check if token is provided
if [ -z "$TOKEN" ]; then
    echo "Usage: gt auth --token <token>"
    exit 1
fi

# Simulate authentication
echo "Authentication successful with token: $TOKEN"
exit 0
