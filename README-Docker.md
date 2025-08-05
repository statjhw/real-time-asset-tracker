# Docker Compose를 이용한 실시간 암호화폐 트래커

이 프로젝트는 Docker Compose를 사용하여 여러 서비스를 연결한 실시간 암호화폐 데이터 파이프라인입니다.

## 🏗️ 아키텍처

```
암호화폐 거래소 APIs
           ↓
    [Producers] → [Kafka] → [Processor] → [Kafka]
                                              ↓
                              [Telegraf] → [InfluxDB] → [Grafana]
```

## 📦 서비스 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| **kafka** | 9092 | 메시지 브로커 |
| **zookeeper** | 2181 | Kafka 의존성 |
| **influxdb** | 8086 | 시계열 데이터베이스 |
| **grafana** | 3000 | 시각화 대시보드 |
| **producers** | - | 암호화폐 데이터 수집 |
| **processor** | - | PyFlink 스트림 처리 |
| **telegraf** | - | 메트릭 수집 및 전송 |

## 🚀 빠른 시작

### 1. 필수 요구사항
- Docker
- Docker Compose

### 2. 실행

```bash
# 스크립트 실행 권한 부여
chmod +x scripts/start.sh scripts/stop.sh

# 모든 서비스 시작
./scripts/start.sh

# 또는 직접 실행
docker-compose up -d
```

### 3. 서비스 확인

- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086 (admin/adminpassword)

## 📋 주요 명령어

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f                    # 전체 로그
docker-compose logs -f crypto-producers   # Producers 로그
docker-compose logs -f crypto-processor   # Processor 로그
docker-compose logs -f telegraf          # Telegraf 로그

# 서비스 재시작
docker-compose restart [서비스명]

# 이미지 재빌드
docker-compose up --build

# 서비스 중지
./scripts/stop.sh
# 또는
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

## 🔧 설정 파일

- `docker-compose.yml`: 메인 Docker Compose 설정
- `configs/config-docker.yaml`: Producers 설정 (Docker용)
- `configs/telegraf/telegraf-docker.conf`: Telegraf 설정 (Docker용)
- `configs/grafana/`: Grafana 대시보드 및 데이터소스 설정

## 📊 데이터 플로우

1. **Producers**: 거래소 API에서 데이터 수집 → Kafka 토픽들로 전송
2. **Processor**: Kafka에서 데이터 읽기 → 변동률/괴리율 계산 → `crypto-ticker-volatility` 토픽으로 전송
3. **Telegraf**: `crypto-ticker-volatility` 토픽에서 읽기 → InfluxDB에 저장
4. **Grafana**: InfluxDB에서 데이터 시각화

## 🐛 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 각 서비스별 로그 확인
docker-compose logs [서비스명]

# 포트 충돌 확인
lsof -i :3000  # Grafana
lsof -i :8086  # InfluxDB
lsof -i :9092  # Kafka
```

### 데이터가 보이지 않는 경우
```bash
# Kafka 토픽 확인
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Kafka 메시지 확인
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic crypto-ticker-volatility --from-beginning

# InfluxDB 데이터 확인
docker-compose exec influxdb influx query 'from(bucket:"crypto-metrics") |> range(start:-1h)'
```

## 📁 볼륨 정보

- `kafka-data`: Kafka 데이터
- `influxdb-data`: InfluxDB 데이터
- `influxdb-config`: InfluxDB 설정
- `grafana-data`: Grafana 설정 및 대시보드

## 🔐 기본 계정 정보

- **Grafana**: admin / admin
- **InfluxDB**: admin / adminpassword
- **InfluxDB Token**: my-super-secret-crypto-tracker-token-12345

## 🔑 InfluxDB 토큰 확인하기

실제 운영 환경에서는 보안을 위해 토큰을 확인하고 변경해야 합니다:

```bash
# 토큰 확인 방법 보기
./scripts/get-influxdb-token.sh

# 컨테이너에서 직접 토큰 목록 확인
docker-compose exec influxdb influx auth list

# InfluxDB UI에서 확인
# http://localhost:8086 → admin/adminpassword 로그인 → API Tokens
```

⚠️ **보안 주의사항**: 실제 운영환경에서는 기본 토큰을 반드시 변경하세요!