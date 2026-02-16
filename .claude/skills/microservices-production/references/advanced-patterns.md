# Advanced Microservices Patterns

## 1. Service Mesh (Istio)

### Istio Installation
```bash
# Install Istio
istioctl install --set profile=demo -y

# Enable sidecar injection for namespace
kubectl label namespace microservices istio-injection=enabled

# Verify installation
istioctl verify-install
```

### Virtual Service for Traffic Management
```yaml
# vs-order-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
  namespace: microservices
spec:
  hosts:
  - order-service.microservices.svc.cluster.local
  http:
  - match:
    - uri:
        prefix: /orders/premium
    route:
    - destination:
        host: order-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: order-service
        subset: v1
      weight: 90
    - destination:
        host: order-service
        subset: v2
      weight: 10
  timeout: 10s
  retries:
    attempts: 3
    perTryTimeout: 2s

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-service
  namespace: microservices
spec:
  host: order-service.microservices.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### mTLS Configuration (Zero-Trust)
```yaml
# peer-auth.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: microservices
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic

---
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: microservices
spec:
  jwtRules:
  - issuer: "https://your-auth-provider.com"
    jwksUri: "https://your-auth-provider.com/.well-known/jwks.json"
    audiences: "api"

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-order-service
  namespace: microservices
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/microservices/sa/api-gateway"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/orders*"]
```

### Service Entry for External Services
```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-api
  namespace: microservices
spec:
  hosts:
  - api.example.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
```

---

## 2. Event-Driven Architecture

### Apache Kafka Setup
```yaml
# kafka-docker-compose.yml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
```

### Event Producer (Order Service)
```python
# producer.py
from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  # Wait for all replicas
    retries=3,
    request_timeout_ms=5000
)

async def publish_order_created_event(order_id: int, user_id: int, total: float):
    event = {
        "event_type": "order.created",
        "aggregate_id": order_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "user_id": user_id,
            "total": total
        }
    }

    future = producer.send('orders', value=event, key=str(order_id))
    record_metadata = future.get(timeout=10)

    logger.info(f"Event published to partition {record_metadata.partition}")
```

### Event Consumer (Notification Service)
```python
# consumer.py
from kafka import KafkaConsumer
import json
import asyncio

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['localhost:9092'],
    group_id='notification-service',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

async def consume_events():
    for message in consumer:
        event = message.value

        if event['event_type'] == 'order.created':
            # Send notification
            await send_order_confirmation_email(
                event['data']['user_id'],
                event['aggregate_id']
            )

        logger.info(f"Processed event: {event['event_type']}")
```

### Saga Pattern for Distributed Transactions
```python
# saga_orchestrator.py - Order Creation Saga
from enum import Enum

class SagaStep(Enum):
    RESERVE_INVENTORY = 1
    PROCESS_PAYMENT = 2
    CREATE_SHIPMENT = 3
    CONFIRM_ORDER = 4

class OrderCreationSaga:
    def __init__(self, order_id: int):
        self.order_id = order_id
        self.current_step = None

    async def execute(self):
        try:
            # Step 1: Reserve inventory
            self.current_step = SagaStep.RESERVE_INVENTORY
            await inventory_service.reserve(self.order_id)

            # Step 2: Process payment
            self.current_step = SagaStep.PROCESS_PAYMENT
            await payment_service.charge(self.order_id)

            # Step 3: Create shipment
            self.current_step = SagaStep.CREATE_SHIPMENT
            await shipment_service.create(self.order_id)

            # Step 4: Confirm order
            self.current_step = SagaStep.CONFIRM_ORDER
            await order_service.confirm(self.order_id)

        except Exception as e:
            logger.error(f"Saga failed at {self.current_step}: {str(e)}")
            await self.compensate()
            raise

    async def compensate(self):
        """Rollback previous steps"""
        if self.current_step == SagaStep.PROCESS_PAYMENT:
            await payment_service.refund(self.order_id)
        elif self.current_step == SagaStep.CREATE_SHIPMENT:
            await payment_service.refund(self.order_id)
            await inventory_service.release(self.order_id)
        elif self.current_step == SagaStep.CONFIRM_ORDER:
            await shipment_service.cancel(self.order_id)
            await payment_service.refund(self.order_id)
            await inventory_service.release(self.order_id)
```

### Dead-Letter Queue for Failed Messages
```python
# Handle failed message processing
async def process_message_with_dlq(message):
    max_retries = 3
    retries = int(message.headers.get('retry-count', 0))

    try:
        await handle_event(message)
    except Exception as e:
        if retries < max_retries:
            # Requeue with incremented retry count
            message.headers['retry-count'] = retries + 1
            producer.send('orders-retry', value=message)
        else:
            # Send to dead-letter queue
            logger.error(f"Message failed after {max_retries} retries, sending to DLQ")
            producer.send('orders-dlq', value=message)
```

---

## 3. Security: Zero-Trust Architecture

### Secret Management with HashiCorp Vault
```python
# vault_client.py
import hvac

class VaultClient:
    def __init__(self, vault_url: str, token: str):
        self.client = hvac.Client(url=vault_url, token=token)

    def get_secret(self, path: str) -> dict:
        response = self.client.secrets.kv.read_secret_version(path=path)
        return response['data']['data']

    def get_database_credentials(self) -> dict:
        return self.get_secret('secret/data/database')

# Usage in FastAPI
vault = VaultClient(
    vault_url=os.getenv('VAULT_ADDR'),
    token=os.getenv('VAULT_TOKEN')
)

db_creds = vault.get_secret('secret/database')
DATABASE_URL = f"postgresql://{db_creds['user']}:{db_creds['password']}@localhost/mydb"
```

### Kubernetes Secret Rotation
```yaml
# external-secrets.yaml - Auto-sync with Vault
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: microservices
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "microservices"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-secret
  namespace: microservices
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
  - secretKey: database-url
    remoteRef:
      key: database
      property: url
```

### JWT Token Validation
```python
# auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from functools import lru_cache

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_jwks():
    """Cache JWKS to avoid repeated fetches"""
    response = httpx.get("https://auth-provider/.well-known/jwks.json")
    return response.json()

async def verify_jwt_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials

    try:
        # Get signing key from JWKS
        unverified = jwt.decode(token, options={"verify_signature": False})
        kid = unverified.get("kid")

        jwks = get_jwks()
        key = next((k for k in jwks['keys'] if k['kid'] == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Verify and decode
        decoded = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience="api"
        )
        return decoded
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(user: dict = Depends(verify_jwt_token)):
    return {"user": user}
```

### Network Policies for Micro-Segmentation
```yaml
# Default deny all traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: microservices
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow order-service to receive traffic from api-gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-gateway-to-order-service
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: order-service
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000

---
# Allow order-service to call product-service and database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-order-service-egress
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: order-service
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: product-service
    ports:
    - protocol: TCP
      port: 8000
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
```

---

## 4. Resilience Patterns

### Circuit Breaker Pattern
```python
# circuit_breaker.py
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = 1      # Normal operation
    OPEN = 2        # Failing, reject requests
    HALF_OPEN = 3   # Test if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@app.get("/protected-call")
async def make_protected_call():
    try:
        result = await breaker.call(
            downstream_service.get_data,
            param1="value"
        )
        return result
    except Exception as e:
        return {"error": "Service unavailable", "fallback_data": []}
```

### Bulkhead Pattern (Resource Isolation)
```python
# bulkhead.py
from concurrent.futures import ThreadPoolExecutor
from asyncio import Semaphore

# Separate thread pools for different operations
db_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="db-")
external_api_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="api-")

# Semaphore for async operations
db_semaphore = Semaphore(20)

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    async with db_semaphore:
        # Only 20 concurrent database operations
        order = await get_order_from_db(order_id)
    return order
```

---

## Production Deployment Checklist

- [ ] Implement circuit breakers for all external calls
- [ ] Configure bulkheads to isolate resource usage
- [ ] Enable distributed tracing end-to-end
- [ ] Implement graceful degradation (fallback strategies)
- [ ] Set up saga pattern for multi-step transactions
- [ ] Configure Istio for traffic management and mTLS
- [ ] Implement secret rotation every 30-90 days
- [ ] Enable network policies for micro-segmentation
- [ ] Set up comprehensive alerting on SLOs
- [ ] Document runbooks for common operational issues
