#!/usr/bin/env python3
"""
Bootstrap Kubernetes manifests for microservices deployment.

Usage:
    python bootstrap-k8s.py --service order-service --image myrepo/order-service:v1.0.0 --namespace microservices
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any

def create_namespace_manifest(namespace: str) -> Dict[str, Any]:
    """Create namespace manifest"""
    return {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': namespace,
            'labels': {'name': namespace}
        }
    }

def create_configmap_manifest(service_name: str, namespace: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Create ConfigMap for service configuration"""
    return {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
            'name': f'{service_name}-config',
            'namespace': namespace
        },
        'data': env_vars
    }

def create_deployment_manifest(
    service_name: str,
    image: str,
    namespace: str,
    replicas: int = 3,
    cpu_request: str = '100m',
    cpu_limit: str = '500m',
    memory_request: str = '128Mi',
    memory_limit: str = '512Mi'
) -> Dict[str, Any]:
    """Create Deployment manifest with production settings"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': service_name,
            'namespace': namespace,
            'labels': {'app': service_name}
        },
        'spec': {
            'replicas': replicas,
            'selector': {'matchLabels': {'app': service_name}},
            'strategy': {
                'type': 'RollingUpdate',
                'rollingUpdate': {'maxSurge': 1, 'maxUnavailable': 0}
            },
            'template': {
                'metadata': {
                    'labels': {'app': service_name, 'version': 'v1'},
                    'annotations': {
                        'prometheus.io/scrape': 'true',
                        'prometheus.io/port': '8000',
                        'prometheus.io/path': '/metrics'
                    }
                },
                'spec': {
                    'serviceAccountName': service_name,
                    'securityContext': {
                        'runAsNonRoot': True,
                        'runAsUser': 1000,
                        'fsGroup': 1000
                    },
                    'containers': [{
                        'name': service_name,
                        'image': image,
                        'imagePullPolicy': 'IfNotPresent',
                        'ports': [{'name': 'http', 'containerPort': 8000, 'protocol': 'TCP'}],
                        'env': [
                            {'name': 'SERVICE_NAME', 'value': service_name},
                            {'name': 'LOG_LEVEL', 'value': 'INFO'}
                        ],
                        'resources': {
                            'requests': {
                                'cpu': cpu_request,
                                'memory': memory_request
                            },
                            'limits': {
                                'cpu': cpu_limit,
                                'memory': memory_limit
                            }
                        },
                        'livenessProbe': {
                            'httpGet': {'path': '/health/live', 'port': 'http'},
                            'initialDelaySeconds': 10,
                            'periodSeconds': 10
                        },
                        'readinessProbe': {
                            'httpGet': {'path': '/health/ready', 'port': 'http'},
                            'initialDelaySeconds': 5,
                            'periodSeconds': 5
                        },
                        'lifecycle': {
                            'preStop': {
                                'exec': {'command': ['/bin/sh', '-c', 'sleep 15']}
                            }
                        },
                        'securityContext': {
                            'allowPrivilegeEscalation': False,
                            'readOnlyRootFilesystem': True,
                            'capabilities': {'drop': ['ALL']}
                        }
                    }],
                    'terminationGracePeriodSeconds': 30
                }
            }
        }
    }

def create_service_manifest(service_name: str, namespace: str, port: int = 8000) -> Dict[str, Any]:
    """Create Service manifest"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': service_name,
            'namespace': namespace
        },
        'spec': {
            'type': 'ClusterIP',
            'selector': {'app': service_name},
            'ports': [{
                'name': 'http',
                'port': port,
                'targetPort': 'http',
                'protocol': 'TCP'
            }]
        }
    }

def create_hpa_manifest(service_name: str, namespace: str, min_replicas: int = 3, max_replicas: int = 10) -> Dict[str, Any]:
    """Create HorizontalPodAutoscaler manifest"""
    return {
        'apiVersion': 'autoscaling/v2',
        'kind': 'HorizontalPodAutoscaler',
        'metadata': {
            'name': f'{service_name}-hpa',
            'namespace': namespace
        },
        'spec': {
            'scaleTargetRef': {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'name': service_name
            },
            'minReplicas': min_replicas,
            'maxReplicas': max_replicas,
            'metrics': [
                {
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 70
                        }
                    }
                }
            ]
        }
    }

def create_pdb_manifest(service_name: str, namespace: str, min_available: int = 2) -> Dict[str, Any]:
    """Create PodDisruptionBudget manifest"""
    return {
        'apiVersion': 'policy/v1',
        'kind': 'PodDisruptionBudget',
        'metadata': {
            'name': f'{service_name}-pdb',
            'namespace': namespace
        },
        'spec': {
            'minAvailable': min_available,
            'selector': {
                'matchLabels': {'app': service_name}
            }
        }
    }

def create_serviceaccount_manifest(service_name: str, namespace: str) -> Dict[str, Any]:
    """Create ServiceAccount manifest"""
    return {
        'apiVersion': 'v1',
        'kind': 'ServiceAccount',
        'metadata': {
            'name': service_name,
            'namespace': namespace
        }
    }

def save_manifests(manifests: list, output_dir: Path):
    """Save manifests to YAML files"""
    output_dir.mkdir(exist_ok=True)

    for i, manifest in enumerate(manifests):
        kind = manifest.get('kind', 'Unknown')
        name = manifest.get('metadata', {}).get('name', f'manifest-{i}')
        filename = f'{i:02d}-{kind.lower()}-{name}.yaml'

        with open(output_dir / filename, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)

        print(f'Created: {filename}')

def main():
    parser = argparse.ArgumentParser(description='Bootstrap Kubernetes manifests')
    parser.add_argument('--service', required=True, help='Service name')
    parser.add_argument('--image', required=True, help='Container image')
    parser.add_argument('--namespace', default='microservices', help='Kubernetes namespace')
    parser.add_argument('--replicas', type=int, default=3, help='Number of replicas')
    parser.add_argument('--output', default='./k8s', help='Output directory for manifests')
    parser.add_argument('--cpu-request', default='100m', help='CPU request')
    parser.add_argument('--cpu-limit', default='500m', help='CPU limit')
    parser.add_argument('--memory-request', default='128Mi', help='Memory request')
    parser.add_argument('--memory-limit', default='512Mi', help='Memory limit')

    args = parser.parse_args()

    # Create manifests
    manifests = [
        create_namespace_manifest(args.namespace),
        create_serviceaccount_manifest(args.service, args.namespace),
        create_configmap_manifest(args.service, args.namespace, {
            'SERVICE_NAME': args.service,
            'LOG_LEVEL': 'INFO',
            'ENVIRONMENT': 'production'
        }),
        create_deployment_manifest(
            args.service,
            args.image,
            args.namespace,
            args.replicas,
            args.cpu_request,
            args.cpu_limit,
            args.memory_request,
            args.memory_limit
        ),
        create_service_manifest(args.service, args.namespace),
        create_hpa_manifest(args.service, args.namespace),
        create_pdb_manifest(args.service, args.namespace)
    ]

    # Save manifests
    output_dir = Path(args.output)
    save_manifests(manifests, output_dir)

    print(f'\nManifests saved to: {output_dir}')
    print(f'Deploy with: kubectl apply -f {output_dir}/')

if __name__ == '__main__':
    main()
