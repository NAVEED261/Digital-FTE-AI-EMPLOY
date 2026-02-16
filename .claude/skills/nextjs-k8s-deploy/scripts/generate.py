#!/usr/bin/env python3
"""
nextjs-k8s-deploy: Generate and deploy Next.js frontend to Kubernetes
MCP Code Execution Pattern - Script executes externally (0 tokens in context)
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict

def generate_package_json(app_name: str) -> str:
    """Generate package.json with Next.js dependencies."""
    return f'''{{
  "name": "{app_name}",
  "version": "1.0.0",
  "description": "LearnFlow - AI-Powered Python Tutoring Frontend",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^14.0.0",
    "@monaco-editor/react": "^4.5.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0"
  }},
  "devDependencies": {{
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.0",
    "eslint": "^8",
    "eslint-config-next": "^14.0.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0"
  }}
}}
'''

def generate_tailwind_config() -> str:
    """Generate tailwind.config.ts."""
    return '''import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{{js,ts,jsx,tsx,mdx}}',
    './components/**/*.{{js,ts,jsx,tsx,mdx}}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#6366f1',
      },
    },
  },
  plugins: [],
}
export default config
'''

def generate_globals_css() -> str:
    """Generate app/globals.css."""
    return '''@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded font-medium transition-colors;
  }

  .btn-primary {
    @apply btn bg-blue-500 text-white hover:bg-blue-600;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-800 hover:bg-gray-300;
  }

  .container {
    @apply max-w-7xl mx-auto px-4;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
'''

def generate_layout_tsx() -> str:
    """Generate app/layout.tsx."""
    return '''import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LearnFlow - AI Python Tutoring',
  description: 'Learn Python with AI-powered tutoring',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  )
}
'''

def generate_page_tsx() -> str:
    """Generate app/page.tsx."""
    return '''export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow">
        <div className="container py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">LearnFlow</h1>
          <a href="/login" className="btn btn-primary">
            Login
          </a>
        </div>
      </nav>

      <section className="container py-20 text-center">
        <h2 className="text-5xl font-bold text-gray-900 mb-6">
          Learn Python with AI Tutoring
        </h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get instant feedback from AI experts. Master Python concepts with
          personalized learning paths.
        </p>
        <a href="/login" className="btn btn-primary text-lg">
          Get Started
        </a>
      </section>

      <section className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'AI Tutors',
              description: 'Get instant feedback from AI experts',
            },
            {
              title: 'Code Editor',
              description: 'Write and test Python code directly',
            },
            {
              title: 'Progress Tracking',
              description: 'Monitor your learning journey',
            },
          ].map((feature) => (
            <div key={feature.title} className="card">
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
'''

def generate_editor_tsx() -> str:
    """Generate components/Editor.tsx."""
    return '''import dynamic from 'next/dynamic'
import { useState } from 'react'

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
  loading: () => <p className="text-gray-500">Loading editor...</p>,
})

interface EditorProps {
  onChange?: (value: string) => void
  onSubmit?: () => void
  defaultValue?: string
}

export const Editor = ({
  onChange,
  onSubmit,
  defaultValue = '# Write your Python code here\\n',
}: EditorProps) => {
  const [code, setCode] = useState(defaultValue)

  const handleChange = (value: string | undefined) => {
    if (value) {
      setCode(value)
      onChange?.(value)
    }
  }

  return (
    <div className="border rounded-lg overflow-hidden bg-gray-900">
      <div className="flex justify-between items-center bg-gray-800 px-4 py-2">
        <span className="text-white font-mono">Python Editor</span>
        <button
          onClick={onSubmit}
          className="btn btn-primary"
        >
          Submit
        </button>
      </div>
      <MonacoEditor
        height="500px"
        defaultLanguage="python"
        defaultValue={defaultValue}
        onChange={handleChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
        }}
      />
    </div>
  )
}
'''

def generate_dashboard_tsx() -> str:
    """Generate components/Dashboard.tsx."""
    return '''interface Module {
  id: number
  name: string
  description: string
}

const MODULES: Module[] = [
  { id: 1, name: 'Python Basics', description: 'Variables, types, operators' },
  { id: 2, name: 'Control Structures', description: 'If, loops, conditions' },
  { id: 3, name: 'Functions', description: 'Definition, parameters, returns' },
  { id: 4, name: 'Data Structures', description: 'Lists, dicts, sets' },
  { id: 5, name: 'OOP Fundamentals', description: 'Classes, objects, inheritance' },
  { id: 6, name: 'File I/O', description: 'Reading, writing files' },
  { id: 7, name: 'Exception Handling', description: 'Error handling' },
  { id: 8, name: 'Popular Libraries', description: 'NumPy, Pandas, Requests' },
]

export const Dashboard = () => {
  return (
    <div className="container py-8">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Welcome Back!
        </h1>
        <p className="text-gray-600">
          Continue your Python learning journey
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {MODULES.map((module) => (
          <div
            key={module.id}
            className="card cursor-pointer hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-gray-900">{module.name}</h3>
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">
                {module.id}
              </span>
            </div>
            <p className="text-gray-600 text-sm">{module.description}</p>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${(module.id * 12) % 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

def generate_dockerfile() -> str:
    """Generate Dockerfile."""
    return '''FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "server.js"]
'''

def generate_deployment_yaml(app_name: str) -> str:
    """Generate Kubernetes deployment manifest."""
    return f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: learnflow
  labels:
    app: {app_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: nextjs
        image: {app_name}:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NEXT_PUBLIC_API_BASE
          value: "http://triage-agent:8001"
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {app_name}
  namespace: learnflow
spec:
  selector:
    app: {app_name}
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
  type: LoadBalancer
'''

def generate_tsconfig() -> str:
    """Generate tsconfig.json."""
    return '''{
  "compilerOptions": {
    "target": "ES2017",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": false,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "allowJs": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
'''

def generate_next_config() -> str:
    """Generate next.config.js."""
    return '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
}

module.exports = nextConfig
'''

def create_nextjs_app(app_name: str = "learnflow-frontend") -> bool:
    """Create Next.js application structure."""
    cwd = Path.cwd()
    app_dir = cwd / app_name

    # Create directories
    dirs = [
        app_dir / "app" / "(auth)" / "login",
        app_dir / "app" / "(app)" / "dashboard",
        app_dir / "app" / "(app)" / "editor",
        app_dir / "components",
        app_dir / "lib",
        app_dir / "public",
        app_dir / "__tests__",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Generate files
    files = {
        "package.json": generate_package_json(app_name),
        "tsconfig.json": generate_tsconfig(),
        "next.config.js": generate_next_config(),
        "tailwind.config.ts": generate_tailwind_config(),
        "app/globals.css": generate_globals_css(),
        "app/layout.tsx": generate_layout_tsx(),
        "app/page.tsx": generate_page_tsx(),
        "components/Editor.tsx": generate_editor_tsx(),
        "components/Dashboard.tsx": generate_dashboard_tsx(),
        "Dockerfile": generate_dockerfile(),
        "deployment.yaml": generate_deployment_yaml(app_name),
        ".gitignore": ".next/\nnode_modules/\n.env.local\n*.log\n",
        ".dockerignore": "node_modules\n.next\n.git\n",
    }

    for file_path, content in files.items():
        full_path = app_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    print(f"✓ Generated {app_name} frontend")
    print(f"  Location: {app_dir}")
    print(f"  Files: {len(files)} created")
    print(f"\\nNext steps:")
    print(f"  cd {app_name}")
    print(f"  npm install")
    print(f"  npm run dev")

    return True

def main():
    """Main entry point."""
    app_name = sys.argv[1] if len(sys.argv) > 1 else "learnflow-frontend"

    success = create_nextjs_app(app_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
