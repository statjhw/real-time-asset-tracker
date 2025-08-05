#!/bin/bash

echo "🛑 실시간 암호화폐 트래커 종료 중..."

# 모든 서비스 종료
docker-compose down

echo "✅ 모든 서비스가 종료되었습니다."

# 볼륨까지 삭제할지 확인
read -p "볼륨과 데이터도 삭제하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v
    echo "🗑️  볼륨과 데이터가 삭제되었습니다."
fi