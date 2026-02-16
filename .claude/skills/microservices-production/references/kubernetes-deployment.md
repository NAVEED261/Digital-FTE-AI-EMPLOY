# Kubernetes Production Deployment

## Service Deployment Manifests

### Namespace Setup
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: microservices
  labels:
    name: microservices
```

### ConfigMap for Configuration
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-config
  namespace: microservices
data:
  LOG_LEVEL: "INFO"
  SERVICE_NAME: "order-service"
  ENVIRONMENT: "production"
```

### Secret for Credentials
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: service-secrets
  namespace: microservices
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:password@postgres.microservices.svc.cluster.local:5432/mydb"
  API_KEY: "your-secret-api-key"
  JWT_SECRET: "your-jwt-secret-key"
```

### Deployment with Health Checks
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: microservices
  labels:
    app: order-service
    version: v1
spec:
  replicas: 3  # High availability
  selector:
    matchLabels:
      app: order-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max extra pod during update
      maxUnavailable: 0  # Zero downtime
  template:
    metadata:
      labels:
        app: order-service
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: order-service
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      # Init container for migrations
      initContainers:
      - name: db-migrate
        image: order-service:latest
        imagePullPolicy: IfNotPresent
        command: ["python", "-m", "alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: service-secrets
              key: DATABASE_URL

      containers:
      - name: order-service
        image: order-service:latest
        imagePullPolicy: IfNotPresent

        # Port configuration
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP

        # Environment variables
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: SERVICE_NAME
          valueFrom:
            configMapKeyRef:
              name: service-config
              key: SERVICE_NAME
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: service-config
              key: LOG_LEVEL
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: service-secrets
              key: DATABASE_URL
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: service-secrets
              key: JWT_SECRET

        # Resource requests and limits
        resources:
          requests:
            cpu: 100m           # Minimum CPU needed
            memory: 128Mi       # Minimum memory needed
          limits:
            cpu: 500m           # Maximum CPU allowed
            memory: 512Mi       # Maximum memory allowed

        # Health checks
        livenessProbe:
          httpGet:
            path: /health/live
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health/ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

        # Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]  # Wait for load balancer to stop sending traffic

        # Security context
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
          readOnlyRootFilesystem: true

        # Volume mounts
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache

      # Volumes
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}

      # Pod disruption budget (for voluntary disruptions)
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - order-service
              topologyKey: kubernetes.io/hostname

      # Termination grace period for graceful shutdown
      terminationGracePeriodSeconds: 30
```

### Service Exposure
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: microservices
  labels:
    app: order-service
spec:
  type: ClusterIP  # Internal DNS within cluster
  selector:
    app: order-service
  ports:
  - name: http
    port: 8000
    targetPort: http
    protocol: TCP
  sessionAffinity: None  # Round-robin load balancing
```

### Ingress for External Access
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: microservices-ingress
  namespace: microservices
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-cert
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /orders
        pathType: Prefix
        backend:
          service:
            name: order-service
            port:
              number: 8000
      - path: /products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8000
```

### Horizontal Pod Autoscaler
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
  namespace: microservices
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### ServiceAccount and RBAC
```yaml
# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service
  namespace: microservices

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: order-service-role
  namespace: microservices
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: order-service-rolebinding
  namespace: microservices
subjects:
- kind: ServiceAccount
  name: order-service
  namespace: microservices
roleRef:
  kind: Role
  name: order-service-role
  apiGroup: rbac.authorization.k8s.io
```

### Pod Disruption Budget (Availability)
```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
  namespace: microservices
spec:
  minAvailable: 2  # Keep at least 2 pods running
  selector:
    matchLabels:
      app: order-service
```

## Deployment Strategy

### Rolling Update (Zero Downtime)
```bash
# kubectl applies RollingUpdate automatically
# Old pods are replaced gradually while new ones come up
# Configured in deployment.yaml via strategy.type and rollingUpdate
```

### Blue-Green Deployment (Fast Rollback)
```yaml
# Maintain two complete deployments
# Switch traffic between them using Service selector
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
    version: v2  # Toggle between v1 and v2
```

### Canary Deployment (Risk Mitigation)
```yaml
# Use Istio VirtualService for traffic shifting
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: order-service
        subset: v1
      weight: 90  # 90% to v1
    - destination:
        host: order-service
        subset: v2
      weight: 10  # 10% to v2 (new version)
```

## Deployment Commands

```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f pdb.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n microservices
kubectl describe deployment order-service -n microservices
kubectl logs -f deployment/order-service -n microservices

# Scale manually
kubectl scale deployment/order-service --replicas=5 -n microservices

# Rolling restart
kubectl rollout restart deployment/order-service -n microservices

# Check rollout status
kubectl rollout status deployment/order-service -n microservices

# Rollback if needed
kubectl rollout undo deployment/order-service -n microservices
kubectl rollout history deployment/order-service -n microservices
```

## Networking Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: order-service-netpol
  namespace: microservices
spec:
  podSelector:
    matchLabels:
      app: order-service
  policyTypes:
  - Ingress
  - Egress

  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: microservices
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000

  egress:
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
