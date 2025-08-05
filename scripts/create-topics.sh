#!/bin/bash

echo "🏗️ Kafka 토픽 생성 스크립트 시작"

# 필요한 토픽들
TOPICS=(
    "crypto-ticker-binance"
    "crypto-ticker-bithumb" 
    "crypto-ticker-bybit"
    "crypto-ticker-upbit"
    "crypto-ticker-coinone"
    "crypto-ticker-volatility"
)

echo "📡 Kafka 연결 확인 중..."
# Kafka가 준비될 때까지 대기
while ! docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; do
    echo "⏳ Kafka 대기 중..."
    sleep 5
done

echo "✅ Kafka 연결 확인됨"

# 각 토픽 생성
for topic in "${TOPICS[@]}"; do
    echo "🏗️ 토픽 생성 중: $topic"
    docker-compose exec kafka kafka-topics \
        --bootstrap-server localhost:9092 \
        --create \
        --topic $topic \
        --partitions 1 \
        --replication-factor 1 \
        --if-not-exists
    
    if [ $? -eq 0 ]; then
        echo "✅ 토픽 생성 완료: $topic"
    else
        echo "⚠️ 토픽 생성 실패 또는 이미 존재: $topic"
    fi
done

echo ""
echo "📋 생성된 토픽 목록:"
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

echo ""
echo "🎉 모든 토픽 생성 완료!" 