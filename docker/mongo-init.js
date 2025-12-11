// ============================================
// NetSentinel SIEM - MongoDB Initialization
// ============================================

// Conectar a la base de datos 'netsentinel'
db = db.getSiblingDB('netsentinel');

print('🚀 Inicializando base de datos NetSentinel SIEM...');

// ============================================
// COLECCIÓN: processed_events
// Logs procesados con detección de patrones
// ============================================
db.createCollection('processed_events', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "source", "level", "message"],
            properties: {
                timestamp: {
                    bsonType: "date",
                    description: "Timestamp del evento (ISO 8601)"
                },
                source: {
                    bsonType: "string",
                    description: "Fuente del log (IP, hostname, servicio)"
                },
                source_ip: {
                    bsonType: "string",
                    description: "IP del origen (para correlación)"
                },
                level: {
                    enum: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    description: "Nivel de severidad del log"
                },
                message: {
                    bsonType: "string",
                    description: "Mensaje del evento"
                },
                metadata: {
                    bsonType: "object",
                    description: "Metadata adicional del log"
                },
                threat_level: {
                    enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    description: "Nivel de amenaza detectado"
                },
                pattern_matched: {
                    bsonType: "string",
                    description: "Patrón de ataque detectado"
                },
                occurrence_count: {
                    bsonType: "int",
                    description: "Número de ocurrencias en ventana temporal"
                }
            }
        }
    }
});

// Índices para optimización de queries
db.processed_events.createIndex({ "timestamp": -1 });
db.processed_events.createIndex({ "source_ip": 1 });
db.processed_events.createIndex({ "level": 1 });
db.processed_events.createIndex({ "threat_level": 1 });
db.processed_events.createIndex({ "timestamp": -1, "source_ip": 1 });

print('✅ Colección "processed_events" creada con índices');

// ============================================
// COLECCIÓN: alerts
// Alertas generadas por el sistema
// ============================================
db.createCollection('alerts', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["alert_id", "timestamp", "severity", "description"],
            properties: {
                alert_id: {
                    bsonType: "string",
                    description: "ID único de la alerta (UUID)"
                },
                timestamp: {
                    bsonType: "date",
                    description: "Timestamp de generación de la alerta"
                },
                severity: {
                    enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    description: "Severidad de la alerta"
                },
                description: {
                    bsonType: "string",
                    description: "Descripción legible de la alerta"
                },
                affected_resource: {
                    bsonType: "string",
                    description: "Recurso afectado (IP, usuario, servicio)"
                },
                recommended_action: {
                    bsonType: "string",
                    description: "Acción recomendada para mitigar"
                },
                pattern_type: {
                    bsonType: "string",
                    description: "Tipo de patrón detectado"
                },
                event_count: {
                    bsonType: "int",
                    description: "Número de eventos que dispararon la alerta"
                },
                resolved: {
                    bsonType: "bool",
                    description: "Estado de resolución de la alerta"
                },
                resolved_at: {
                    bsonType: "date",
                    description: "Timestamp de resolución"
                },
                related_events: {
                    bsonType: "array",
                    description: "Referencias a ObjectIds de processed_events"
                }
            }
        }
    }
});

// Índices para queries de alertas
db.alerts.createIndex({ "alert_id": 1 }, { unique: true });
db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "severity": 1 });
db.alerts.createIndex({ "affected_resource": 1 });
db.alerts.createIndex({ "resolved": 1, "timestamp": -1 });
db.alerts.createIndex({ "pattern_type": 1 });

print('✅ Colección "alerts" creada con índices');

// ============================================
// COLECCIÓN: metrics
// Métricas del sistema para monitoreo
// ============================================
db.createCollection('metrics');
db.metrics.createIndex({ "timestamp": -1 });
db.metrics.createIndex({ "metric_type": 1, "timestamp": -1 });

print('✅ Colección "metrics" creada');

// ============================================
// DATOS DE PRUEBA (Opcional - Comentar en producción)
// ============================================
print('📊 Insertando datos de prueba...');

db.processed_events.insertOne({
    timestamp: new Date(),
    source: "test-server",
    source_ip: "192.168.1.100",
    level: "INFO",
    message: "Sistema inicializado correctamente",
    metadata: { component: "init-script" },
    threat_level: "LOW",
    pattern_matched: null,
    occurrence_count: 1
});

db.alerts.insertOne({
    alert_id: "test-alert-001",
    timestamp: new Date(),
    severity: "LOW",
    description: "Alerta de prueba del sistema",
    affected_resource: "192.168.1.100",
    recommended_action: "Ninguna - alerta de prueba",
    pattern_type: "test",
    event_count: 1,
    resolved: false,
    related_events: []
});

print('✅ Datos de prueba insertados');
print('🎉 Inicialización de MongoDB completada exitosamente');
