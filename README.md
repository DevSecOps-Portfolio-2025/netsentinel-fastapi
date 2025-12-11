# NetSentinel SIEM 🛡️

Sistema de análisis de logs en tiempo real con detección de patrones de ataque usando arquitectura de microservicios, Kafka y MongoDB.

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│  Ingestor   │─────▶│    Kafka     │─────▶│  Processor    │
│  (FastAPI)  │      │ (logs-topic) │      │ (Consumer)    │
└─────────────┘      └──────────────┘      └───────┬───────┘
                                                     │
                                    ┌────────────────┴────────────────┐
                                    ▼                                 ▼
                            ┌──────────────┐                 ┌──────────────┐
                            │   MongoDB    │                 │    Redis     │
                            │ (Events/    │                 │  (Alertas)   │
                            │  Alerts)     │                 │   Cache      │
                            └──────────────┘                 └──────────────┘
```

## 📁 Estructura del Monorepo

```
netsentinel-fastapi/
├── docker-compose.yml          # Orquestación de servicios
├── .env.example               # Variables de entorno template
├── .dockerignore              # Archivos excluidos de Docker build
├── docker/
│   ├── Dockerfile.python      # Imagen base Python 3.11 multistage
│   └── mongo-init.js          # Script de inicialización MongoDB
├── services/
│   ├── ingestor/              # Microservicio FastAPI (US-002)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── ...
│   └── processor/             # Worker Python (US-003/US-004)
│       ├── main.py
│       ├── requirements.txt
│       └── ...
└── docs/                      # Documentación técnica
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker Desktop 24.0+ (Windows/Mac) o Docker Engine 24.0+ (Linux)
- Docker Compose v2.20+
- 8GB RAM mínimo disponible
- Puertos libres: `2181`, `9092`, `9093`, `9000`, `27017`, `6379`

### 1️⃣ Configuración Inicial

```powershell
# Clonar el repositorio
git clone https://github.com/DevSecOps-Portfolio-2025/netsentinel-fastapi.git
cd netsentinel-fastapi

# Configurar variables de entorno
Copy-Item .env.example .env
# Editar .env con tus credenciales (CAMBIAR PASSWORDS EN PRODUCCIÓN)
```

### 2️⃣ Levantar Infraestructura

```powershell
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Verificar estado de servicios
docker-compose ps
```

**Tiempos de inicio esperados:**
- Zookeeper: ~10s
- Kafka: ~30s (espera health check de Zookeeper)
- MongoDB: ~15s
- Redis: ~5s
- Kafdrop: ~20s (espera Kafka)

### 3️⃣ Validar Servicios

```powershell
# Health checks
curl http://localhost:9000          # Kafdrop UI
curl http://localhost:27017         # MongoDB (connection refused = OK)
curl http://localhost:6379          # Redis (connection refused = OK)

# Verificar logs de Kafka
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 4️⃣ Acceder a Interfaces Web

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Kafdrop** | http://localhost:9000 | UI para inspeccionar tópicos, mensajes y consumer groups de Kafka |

## 🔧 Comandos Útiles

### Docker Compose

```powershell
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (BORRA DATOS)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Ver logs de un servicio específico
docker-compose logs -f kafka
docker-compose logs -f mongodb

# Ejecutar comando en contenedor
docker-compose exec kafka bash
docker-compose exec mongodb mongosh
```

### Kafka

```powershell
# Listar tópicos
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Crear tópico manualmente (si auto-create deshabilitado)
docker-compose exec kafka kafka-topics --create --topic logs-topic --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092

# Producir mensaje de prueba
docker-compose exec kafka kafka-console-producer --topic logs-topic --bootstrap-server localhost:9092
# (escribir JSON y presionar Enter)

# Consumir mensajes
docker-compose exec kafka kafka-console-consumer --topic logs-topic --from-beginning --bootstrap-server localhost:9092

# Ver consumer groups
docker-compose exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092
```

### MongoDB

```powershell
# Conectar a MongoDB
docker-compose exec mongodb mongosh -u admin -p netsentinel2025 --authenticationDatabase admin

# Comandos dentro de mongosh
use netsentinel
db.processed_events.countDocuments()
db.alerts.find().limit(5)
db.processed_events.createIndex({ "timestamp": -1, "source_ip": 1 })
```

### Redis

```powershell
# Conectar a Redis CLI
docker-compose exec redis redis-cli -a netsentinel2025

# Comandos dentro de redis-cli
KEYS alert:*
GET alert:12345
SCAN 0 MATCH alert:* COUNT 100
FLUSHDB  # ⚠️ BORRA TODA LA BASE DE DATOS
```

## 🔐 Seguridad

### Producción

**⚠️ CRÍTICO:** Antes de desplegar en producción:

1. Cambiar todas las contraseñas en `.env`:
   - `MONGO_ROOT_PASSWORD`
   - `REDIS_PASSWORD`
   - `API_KEY`
   - `JWT_SECRET_KEY`

2. Habilitar autenticación en Kafka:
   ```yaml
   KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:SASL_PLAINTEXT,EXTERNAL:SASL_PLAINTEXT
   KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAIN
   ```

3. Configurar SSL/TLS para comunicaciones externas

4. Limitar puertos expuestos (eliminar port mappings innecesarios)

5. Usar Docker Secrets en lugar de variables de entorno

## 📊 Monitoreo

### Health Checks Configurados

Todos los servicios tienen health checks automáticos:

```powershell
# Ver estado de health checks
docker-compose ps

# Inspeccionar health check de un servicio
docker inspect netsentinel-kafka --format='{{json .State.Health}}' | ConvertFrom-Json
```

### Métricas de Kafka (via Kafdrop)

Acceder a http://localhost:9000 para ver:
- Throughput de mensajes
- Consumer lag
- Tamaño de particiones
- Offsets por consumer group

## 🐛 Troubleshooting

### Kafka no inicia

```powershell
# Ver logs detallados
docker-compose logs kafka

# Verificar conectividad con Zookeeper
docker-compose exec kafka nc -zv zookeeper 2181

# Reiniciar Kafka
docker-compose restart kafka
```

### MongoDB no acepta conexiones

```powershell
# Verificar logs
docker-compose logs mongodb

# Validar credenciales
docker-compose exec mongodb mongosh -u admin -p netsentinel2025
```

### Puerto ya en uso

```powershell
# Encontrar proceso usando puerto (ejemplo: 9092)
Get-NetTCPConnection -LocalPort 9092 | Select OwningProcess
Stop-Process -Id <PID>
```

### Volúmenes corruptos

```powershell
# ⚠️ ELIMINA TODOS LOS DATOS
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

## 🔄 Próximos Pasos

1. Implementar **US-002**: Microservicio Ingestor (FastAPI)
2. Implementar **US-003**: Microservicio Processor (Consumer)
3. Implementar **US-004**: Sistema de alertas
4. Implementar **US-005**: API de consultas

## 📚 Referencias

- [Confluent Kafka Docker Images](https://docs.confluent.io/platform/current/installation/docker/image-reference.html)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [Kafdrop GitHub](https://github.com/obsidiandynamics/kafdrop)

## 📝 Licencia

MIT License - DevSecOps Portfolio 2025

---

**Desarrollado por:** DevSecOps-Portfolio-2025  
**Última actualización:** Diciembre 2025
