#!/bin/bash

echo "🚀 실시간 암호화폐 트래커 시작 중..."

# Docker Compose로 모든 서비스 시작
docker-compose up -d

echo "⏳ 서비스 초기화 대기 중..."
sleep 30

echo "✅ 서비스 상태 확인:"
docker-compose ps

echo ""
echo "🌐 서비스 접속 정보:"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo "  - InfluxDB: http://localhost:8086 (admin/adminpassword)"
echo "  - Kafka: localhost:9092"
echo ""
echo "🔑 InfluxDB 토큰 정보:"
echo "  - 기본 토큰: my-super-secret-crypto-tracker-token-12345"
echo "  - 토큰 확인: ./scripts/get-influxdb-token.sh"
echo ""
echo "📊 로그 확인:"
echo "  - 전체 로그: docker-compose logs -f"
echo "  - 특정 서비스: docker-compose logs -f [서비스명]"
echo "    예: docker-compose logs -f crypto-producers"
echo ""
echo "🔧 유용한 명령어:"
echo "  - 서비스 중지: docker-compose down"
echo "  - 볼륨까지 삭제: docker-compose down -v"
echo "  - 이미지 재빌드: docker-compose up --build"