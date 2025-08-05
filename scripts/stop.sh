#!/bin/bash

echo "🛑 실시간 암호화폐 트래커 종료 중..."

# 모든 서비스 종료
docker-compose down

echo "✅ 모든 서비스가 종료되었습니다."

# Kafka 볼륨 자동 삭제 (클러스터 ID 충돌 방지)
echo "🔧 Kafka 볼륨 삭제 중... (클러스터 ID 충돌 방지)"
docker volume rm real-time-asset-tracker_kafka-data 2>/dev/null || echo "   (Kafka 볼륨이 이미 없거나 삭제할 수 없음)"

# 다른 볼륨들은 선택적 삭제
echo ""
read -p "🗑️ 나머지 데이터 볼륨도 삭제하시겠습니까? (InfluxDB, Grafana 데이터 포함) (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ 모든 볼륨 삭제 중..."
    docker volume rm real-time-asset-tracker_influxdb-data 2>/dev/null || true
    docker volume rm real-time-asset-tracker_influxdb-config 2>/dev/null || true
    docker volume rm real-time-asset-tracker_grafana-data 2>/dev/null || true
    echo "✅ 모든 데이터 볼륨이 삭제되었습니다."
else
    echo "📊 InfluxDB와 Grafana 데이터는 보존됩니다."
fi

echo ""
echo "🎯 다음 시작 시:"
echo "  - Kafka는 깨끗한 상태로 시작됩니다 (클러스터 ID 충돌 없음)"
echo "  - 토픽 자동 생성: ./scripts/start.sh"