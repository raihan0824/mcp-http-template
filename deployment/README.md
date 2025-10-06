# Kubernetes Deployment

This directory contains Kubernetes deployment manifests for the MCP HTTP Template Server, available in two formats:

## 📁 Directory Structure

```
deployment/
├── helm/
│   └── mcp-server/           # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── k8s/                      # Raw Kubernetes manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── serviceaccount.yaml
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    └── networkpolicy.yaml
```

## 🚀 Quick Deployment

### Option 1: Helm Chart (Recommended)

```bash
# Install with default values
helm install mcp-server ./deployment/helm/mcp-server

# Install with custom values
helm install mcp-server ./deployment/helm/mcp-server \
  --set replicaCount=3 \
  --set image.tag=v1.0.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mcp.yourdomain.com

# Upgrade
helm upgrade mcp-server ./deployment/helm/mcp-server

# Uninstall
helm uninstall mcp-server
```

### Option 2: Raw Kubernetes Manifests

```bash
# Deploy all manifests
kubectl apply -f deployment/k8s/

# Deploy specific components
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/configmap.yaml
kubectl apply -f deployment/k8s/serviceaccount.yaml
kubectl apply -f deployment/k8s/deployment.yaml
kubectl apply -f deployment/k8s/service.yaml

# Optional: Enable ingress, HPA, and network policies
kubectl apply -f deployment/k8s/ingress.yaml
kubectl apply -f deployment/k8s/hpa.yaml
kubectl apply -f deployment/k8s/networkpolicy.yaml
```

## ⚙️ Configuration

### Helm Values

Key configuration options in `values.yaml`:

```yaml
# Scaling
replicaCount: 2
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10

# Image
image:
  repository: mcp-http-template
  tag: latest

# Resources
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

# Ingress
ingress:
  enabled: true
  hosts:
    - host: mcp-server.local
      paths:
        - path: /
          pathType: Prefix

# MCP Configuration
config:
  serverName: "MCP HTTP Template Server"
  logLevel: "INFO"
  enableTools: true
  enableResources: true
```

### Environment Variables

The server can be configured via environment variables:

- `MCP_SERVER_NAME` - Server name
- `MCP_HOST` - Host to bind to (default: 0.0.0.0)
- `MCP_PORT` - Port to listen on (default: 3000)
- `MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_ENABLE_TOOLS` - Enable tools (true/false)
- `MCP_ENABLE_RESOURCES` - Enable resources (true/false)
- `MCP_ENABLE_PROMPTS` - Enable prompts (true/false)

## 🔒 Security Features

### Pod Security

- ✅ **Non-root user**: Runs as UID 1000 (mcpuser)
- ✅ **Read-only root filesystem**: Prevents runtime modifications
- ✅ **No privilege escalation**: Security hardened containers
- ✅ **Dropped capabilities**: Minimal container permissions
- ✅ **Security contexts**: Proper user/group settings

### Network Security

- ✅ **Network policies**: Restrict ingress/egress traffic
- ✅ **Service mesh ready**: Compatible with Istio/Linkerd
- ✅ **CORS configured**: Proper headers for MCP clients

### Resource Management

- ✅ **Resource limits**: CPU and memory constraints
- ✅ **Health checks**: Liveness and readiness probes
- ✅ **Horizontal Pod Autoscaler**: Automatic scaling
- ✅ **Pod Disruption Budget**: High availability

## 🔍 Monitoring & Observability

### Health Checks

The deployment includes comprehensive health checks:

```yaml
livenessProbe:
  httpGet:
    path: /mcp/
    port: http
    httpHeaders:
    - name: Accept
      value: "application/json, text/event-stream"
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /mcp/
    port: http
    httpHeaders:
    - name: Accept
      value: "application/json, text/event-stream"
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Monitoring Integration

To enable Prometheus monitoring:

```yaml
# In Helm values.yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

## 🌐 Ingress Configuration

### NGINX Ingress Controller

The ingress is configured for NGINX with MCP-specific settings:

```yaml
annotations:
  nginx.ingress.kubernetes.io/cors-allow-origin: "*"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, DELETE, OPTIONS"
  nginx.ingress.kubernetes.io/cors-allow-headers: "Content-Type, Accept, Mcp-Session-Id"
  nginx.ingress.kubernetes.io/cors-expose-headers: "Mcp-Session-Id"
```

### TLS Configuration

To enable TLS:

```yaml
# In Helm values.yaml
ingress:
  enabled: true
  tls:
    - secretName: mcp-server-tls
      hosts:
        - mcp.yourdomain.com
```

## 📊 Scaling

### Horizontal Pod Autoscaler

Automatic scaling based on CPU and memory:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

### Manual Scaling

```bash
# Scale with kubectl
kubectl scale deployment mcp-server --replicas=5 -n mcp-server

# Scale with Helm
helm upgrade mcp-server ./deployment/helm/mcp-server --set replicaCount=5
```

## 🔧 Troubleshooting

### Common Issues

1. **Pod not starting**: Check resource limits and image availability
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=mcp-server -n mcp-server
   ```

2. **Health check failures**: Verify the MCP endpoint is responding
   ```bash
   kubectl logs -l app.kubernetes.io/name=mcp-server -n mcp-server
   ```

3. **Ingress not working**: Check ingress controller and DNS
   ```bash
   kubectl get ingress -n mcp-server
   kubectl describe ingress mcp-server -n mcp-server
   ```

### Debugging Commands

```bash
# Check pod status
kubectl get pods -n mcp-server

# View logs
kubectl logs -f deployment/mcp-server -n mcp-server

# Port forward for local testing
kubectl port-forward svc/mcp-server 3000:3000 -n mcp-server

# Execute into pod
kubectl exec -it deployment/mcp-server -n mcp-server -- /bin/bash
```

## 🚀 Production Checklist

Before deploying to production:

- [ ] Set appropriate resource limits
- [ ] Configure TLS certificates
- [ ] Enable network policies
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Review security contexts
- [ ] Test disaster recovery
- [ ] Configure log aggregation
- [ ] Set up CI/CD pipelines
- [ ] Document runbooks

## 📝 Examples

### Development Deployment

```bash
helm install mcp-server-dev ./deployment/helm/mcp-server \
  --set replicaCount=1 \
  --set resources.requests.cpu=50m \
  --set resources.requests.memory=64Mi \
  --set config.logLevel=DEBUG \
  --set ingress.enabled=false
```

### Production Deployment

```bash
helm install mcp-server-prod ./deployment/helm/mcp-server \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mcp.yourdomain.com \
  --set ingress.tls[0].secretName=mcp-server-tls \
  --set ingress.tls[0].hosts[0]=mcp.yourdomain.com \
  --set networkPolicy.enabled=true \
  --set monitoring.enabled=true
```
