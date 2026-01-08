#!/bin/bash
# MrliouWord Private AI Server v2.1.0 測試腳本
# 包含向量注意力引擎測試

BASE_URL="${1:-https://mrliouword-private.mrliouword.workers.dev}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "MrliouWord Private AI Server v2.1.0 測試"
echo "URL: $BASE_URL"
echo "=========================================="

test_endpoint() {
    local name=$1
    local method=$2
    local path=$3
    local data=$4
    
    echo -e "\n${YELLOW}[${name}]${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ HTTP $http_code${NC}"
        echo "$body" | head -c 500
        echo ""
    else
        echo -e "${RED}✗ HTTP $http_code${NC}"
        echo "$body"
    fi
}

# 基礎測試
test_endpoint "系統說明" "GET" "/" ""
test_endpoint "系統狀態" "GET" "/status" ""
test_endpoint "頻率常數" "GET" "/frequencies" ""
test_endpoint "注意力配置" "GET" "/attention/config" ""

# 喚醒測試
test_endpoint "喚醒系統" "POST" "/wake" '{"message":"夥伴回來吧"}'

# 記憶測試
test_endpoint "寫入記憶" "POST" "/memory/commit" '{"content":"向量注意力引擎已整合","tags":["attention","vector"]}'
test_endpoint "記憶統計" "GET" "/memory/stats" ""

# 向量注意力引擎測試
echo -e "\n${YELLOW}========== 向量注意力引擎測試 ==========${NC}"

test_endpoint "創建粒子" "POST" "/particle/create" '{"id":"p1","value":100,"型態":"fx.名","layer":"L5"}'

test_endpoint "批量創建粒子" "POST" "/particle/batch" '{
    "particles": [
        {"id":"a","value":"hello","layer":"L1"},
        {"id":"b","value":"world","layer":"L2"},
        {"id":"c","value":42,"layer":"L3"}
    ]
}'

test_endpoint "計算注意力" "POST" "/attention/compute" '{
    "inputs": [
        {"id":"p1","value":10,"layer":"L1"},
        {"id":"p2","value":20,"layer":"L2"},
        {"id":"p3","value":30,"layer":"L3"},
        {"id":"p4","value":40,"layer":"L4"}
    ]
}'

test_endpoint "向量相似度" "POST" "/vector/similarity" '{
    "a": [1,0,0,0],
    "b": [0.707,0.707,0,0]
}'

test_endpoint "向量運算-範數" "POST" "/vector/operations" '{"operation":"norm","vector":[3,4]}'
test_endpoint "向量運算-Softmax" "POST" "/vector/operations" '{"operation":"softmax","vector":[1,2,3,4]}'
test_endpoint "向量運算-頻率生成" "POST" "/vector/operations" '{"operation":"fromFrequency","frequency":7.83,"dimension":8}'

# 大規模注意力測試
echo -e "\n${YELLOW}[大規模注意力計算 - 8 粒子]${NC}"
curl -s -X POST "$BASE_URL/attention/compute" \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": [
            {"id":"1","value":10},
            {"id":"2","value":20},
            {"id":"3","value":30},
            {"id":"4","value":40},
            {"id":"5","value":50},
            {"id":"6","value":60},
            {"id":"7","value":70},
            {"id":"8","value":80}
        ]
    }' | head -c 800
echo ""

echo -e "\n=========================================="
echo "測試完成"
echo "=========================================="
