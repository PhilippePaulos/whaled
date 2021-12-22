echo 'Create trades template'
curl -X PUT -H "Content-Type: application/json" http://localhost:9200/_template/trades_template -d '{
    "index_patterns": [
        "trades-*"
    ]
}'

echo 'Create token template'
curl -X PUT -H "Content-Type: application/json" http://localhost:9200/_template/token_template -d '{
    "index_patterns": [
        "token-*"
    ]
}'
