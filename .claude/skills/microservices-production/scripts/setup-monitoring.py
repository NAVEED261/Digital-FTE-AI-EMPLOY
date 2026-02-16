#!/usr/bin/env python3
"""
Setup monitoring stack for microservices (Prometheus, Grafana, Jaeger, Loki).

Usage:
    python setup-monitoring.py --namespace monitoring --install-prometheus --install-grafana
"""

import argparse
import yaml
from pathlib import Path

def create_prometheus_configmap(services: list) -> dict:
    """Create Prometheus ConfigMap"""
    scrape_configs = []
    for service in services:
        scrape_configs.append({
            'job_name': service,
            'static_configs': [{'targets': [f'{service}:8000']}],
            'metrics_path': '/metrics'
        })

    config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s'
        },
        'scrape_configs': scrape_configs
    }

    return {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
            'name': 'prometheus-config',
            'namespace': 'monitoring'
        },
        'data': {
            'prometheus.yml': yaml.dump(config)
        }
    }

def create_prometheus_deployment() -> dict:
    """Create Prometheus Deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'prometheus',
            'namespace': 'monitoring'
        },
        'spec': {
            'replicas': 1,
            'selector': {'matchLabels': {'app': 'prometheus'}},
            'template': {
                'metadata': {'labels': {'app': 'prometheus'}},
                'spec': {
                    'containers': [{
                        'name': 'prometheus',
                        'image': 'prom/prometheus:latest',
                        'ports': [{'containerPort': 9090}],
                        'volumeMounts': [{
                            'name': 'config',
                            'mountPath': '/etc/prometheus'
                        }],
                        'args': [
                            '--config.file=/etc/prometheus/prometheus.yml',
                            '--storage.tsdb.path=/prometheus'
                        ],
                        'resources': {
                            'requests': {'cpu': '100m', 'memory': '128Mi'},
                            'limits': {'cpu': '500m', 'memory': '1Gi'}
                        }
                    }],
                    'volumes': [{
                        'name': 'config',
                        'configMap': {'name': 'prometheus-config'}
                    }]
                }
            }
        }
    }

def create_prometheus_service() -> dict:
    """Create Prometheus Service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'prometheus',
            'namespace': 'monitoring'
        },
        'spec': {
            'type': 'ClusterIP',
            'selector': {'app': 'prometheus'},
            'ports': [{
                'port': 9090,
                'targetPort': 9090
            }]
        }
    }

def create_grafana_deployment() -> dict:
    """Create Grafana Deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'grafana',
            'namespace': 'monitoring'
        },
        'spec': {
            'replicas': 1,
            'selector': {'matchLabels': {'app': 'grafana'}},
            'template': {
                'metadata': {'labels': {'app': 'grafana'}},
                'spec': {
                    'containers': [{
                        'name': 'grafana',
                        'image': 'grafana/grafana:latest',
                        'ports': [{'containerPort': 3000}],
                        'env': [
                            {'name': 'GF_SECURITY_ADMIN_PASSWORD', 'value': 'admin'},
                            {'name': 'GF_INSTALL_PLUGINS', 'value': 'grafana-piechart-panel'}
                        ],
                        'resources': {
                            'requests': {'cpu': '100m', 'memory': '128Mi'},
                            'limits': {'cpu': '200m', 'memory': '256Mi'}
                        }
                    }]
                }
            }
        }
    }

def create_grafana_service() -> dict:
    """Create Grafana Service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'grafana',
            'namespace': 'monitoring'
        },
        'spec': {
            'type': 'NodePort',
            'selector': {'app': 'grafana'},
            'ports': [{
                'port': 3000,
                'targetPort': 3000,
                'nodePort': 30300
            }]
        }
    }

def create_jaeger_deployment() -> dict:
    """Create Jaeger Deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'jaeger',
            'namespace': 'monitoring'
        },
        'spec': {
            'replicas': 1,
            'selector': {'matchLabels': {'app': 'jaeger'}},
            'template': {
                'metadata': {'labels': {'app': 'jaeger'}},
                'spec': {
                    'containers': [{
                        'name': 'jaeger',
                        'image': 'jaegertracing/all-in-one:latest',
                        'ports': [
                            {'name': 'jaeger-agent-zipkin-thrift', 'containerPort': 6831, 'protocol': 'UDP'},
                            {'name': 'jaeger-ui', 'containerPort': 16686}
                        ],
                        'resources': {
                            'requests': {'cpu': '100m', 'memory': '256Mi'},
                            'limits': {'cpu': '500m', 'memory': '1Gi'}
                        }
                    }]
                }
            }
        }
    }

def create_jaeger_service() -> dict:
    """Create Jaeger Service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'jaeger',
            'namespace': 'monitoring'
        },
        'spec': {
            'type': 'NodePort',
            'selector': {'app': 'jaeger'},
            'ports': [
                {'name': 'jaeger-agent', 'port': 6831, 'targetPort': 6831, 'protocol': 'UDP'},
                {'name': 'jaeger-ui', 'port': 16686, 'targetPort': 16686, 'nodePort': 30686}
            ]
        }
    }

def create_loki_deployment() -> dict:
    """Create Loki Deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'loki',
            'namespace': 'monitoring'
        },
        'spec': {
            'replicas': 1,
            'selector': {'matchLabels': {'app': 'loki'}},
            'template': {
                'metadata': {'labels': {'app': 'loki'}},
                'spec': {
                    'containers': [{
                        'name': 'loki',
                        'image': 'grafana/loki:latest',
                        'ports': [{'containerPort': 3100}],
                        'resources': {
                            'requests': {'cpu': '100m', 'memory': '128Mi'},
                            'limits': {'cpu': '200m', 'memory': '256Mi'}
                        }
                    }]
                }
            }
        }
    }

def create_loki_service() -> dict:
    """Create Loki Service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'loki',
            'namespace': 'monitoring'
        },
        'spec': {
            'type': 'ClusterIP',
            'selector': {'app': 'loki'},
            'ports': [{
                'port': 3100,
                'targetPort': 3100
            }]
        }
    }

def create_namespace() -> dict:
    """Create monitoring namespace"""
    return {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': 'monitoring'
        }
    }

def save_manifest(manifest: dict, filename: str, output_dir: Path):
    """Save manifest to file"""
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / filename, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False)
    print(f'Created: {filename}')

def main():
    parser = argparse.ArgumentParser(description='Setup monitoring stack')
    parser.add_argument('--output', default='./monitoring', help='Output directory')
    parser.add_argument('--services', nargs='+', default=['order-service', 'product-service'],
                        help='Services to monitor')

    args = parser.parse_args()
    output_dir = Path(args.output)

    # Create manifests
    manifests = [
        ('00-namespace.yaml', create_namespace()),
        ('01-prometheus-configmap.yaml', create_prometheus_configmap(args.services)),
        ('02-prometheus-deployment.yaml', create_prometheus_deployment()),
        ('03-prometheus-service.yaml', create_prometheus_service()),
        ('04-grafana-deployment.yaml', create_grafana_deployment()),
        ('05-grafana-service.yaml', create_grafana_service()),
        ('06-jaeger-deployment.yaml', create_jaeger_deployment()),
        ('07-jaeger-service.yaml', create_jaeger_service()),
        ('08-loki-deployment.yaml', create_loki_deployment()),
        ('09-loki-service.yaml', create_loki_service()),
    ]

    for filename, manifest in manifests:
        save_manifest(manifest, filename, output_dir)

    print(f'\nMonitoring stack manifests saved to: {output_dir}')
    print(f'Deploy with: kubectl apply -f {output_dir}/')
    print('\nAccess points:')
    print('  - Prometheus: http://localhost:30900 (or port-forward service/prometheus -n monitoring 9090:9090)')
    print('  - Grafana: http://localhost:30300 (or use NodePort)')
    print('  - Jaeger: http://localhost:30686 (or use NodePort)')

if __name__ == '__main__':
    main()
