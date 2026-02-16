# nextjs-k8s-deploy Reference Guide

## Overview

The `nextjs-k8s-deploy` skill generates a complete Next.js 14 application with:
- App Router (latest Next.js pattern)
- Monaco code editor integration
- TailwindCSS responsive styling
- TypeScript configuration
- API integration with backend agents
- Docker containerization
- Kubernetes deployment manifests
- Jest and React Testing Library test suite

## Project Structure

```
learnflow-frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Home page
│   ├── globals.css              # Global Tailwind styles
│   ├── (auth)/                  # Auth group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (app)/                   # App group (requires auth)
│   │   ├── dashboard/page.tsx
│   │   └── editor/page.tsx
│   └── api/                     # API routes (optional)
│       └── auth/route.ts
├── components/                  # Reusable components
│   ├── Editor.tsx              # Monaco code editor
│   ├── Dashboard.tsx           # Dashboard layout
│   ├── ChatBox.tsx             # AI chat interface
│   ├── ModuleList.tsx          # Learning modules
│   ├── ProgressBar.tsx         # Progress visualization
│   └── Navbar.tsx              # Navigation
├── lib/
│   ├── api.ts                 # API client for backend
│   ├── auth.ts                # Auth utilities
│   └── hooks.ts               # Custom React hooks
├── public/
│   └── favicon.ico
├── styles/
│   └── (custom CSS files)
├── __tests__/                 # Jest tests
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── Dockerfile
├── .dockerignore
├── deployment.yaml
├── service.yaml
└── README.md
```

## Page Templates

### Home Page (app/page.tsx)

Landing page with:
- Hero section introducing LearnFlow
- CTA button to login/register
- Feature highlights
- Simple, clean design

### Dashboard Page (app/dashboard/page.tsx)

Main student interface with:
- 8 Python modules displayed
- Progress tracking
- Current topic indicator
- Quick links to modules
- Welcome message

### Editor Page (app/editor/page.tsx)

Code editor interface with:
- Full-screen Monaco editor
- Code submission button
- Real-time syntax highlighting
- Example code snippets
- Feedback panel

### Login Page (app/(auth)/login/page.tsx)

Authentication interface with:
- Email/password form
- Error messages
- Link to registration
- Remember me option
- Loading state

## Component Details

### Editor Component

```typescript
<Editor
  language="python"
  theme="vs-dark"
  height="100%"
  code={code}
  onChange={setCode}
  onSubmit={handleSubmit}
/>
```

Features:
- Python syntax highlighting
- Dark/light theme support
- Keyboard shortcuts (Cmd+S to submit)
- Line numbers and folding
- Integrated terminal output

### ChatBox Component

```typescript
<ChatBox
  messages={messages}
  onSendMessage={sendMessage}
  isLoading={isLoading}
/>
```

Features:
- Real-time message display
- Typing indicator
- Error handling
- Message history
- Auto-scroll to latest

### ModuleList Component

```typescript
<ModuleList
  modules={modules}
  currentModule={currentModule}
  onSelectModule={selectModule}
/>
```

Features:
- Displays 8 modules
- Current module highlighting
- Progress indicators
- Click to select
- Responsive grid

## API Integration

### API Client (lib/api.ts)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  }
});

// API methods
export const submitQuery = (studentId: number, query: string) =>
  api.post('/api/query', { student_id: studentId, query });

export const submitCodeReview = (studentId: number, code: string) =>
  api.post('/api/review', { student_id: studentId, code });

export const getExplanation = (studentId: number, concept: string) =>
  api.post('/api/explain', { student_id: studentId, concept });
```

### Making API Calls

```typescript
import { submitQuery } from '@/lib/api';

const handleQuery = async (query: string) => {
  try {
    const response = await submitQuery(studentId, query);
    setResponse(response.data);
  } catch (error) {
    setError('Failed to get response');
  }
};
```

## Styling with TailwindCSS

### Global Styles (app/globals.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
  }
}
```

### Component Styling

```typescript
export const Dashboard = () => (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div className="max-w-7xl mx-auto px-4">
      <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
    </div>
  </div>
);
```

### Responsive Design

```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid: 1 col mobile, 2 tablet, 3 desktop */}
</div>
```

## Authentication

### Local Storage Management

```typescript
// lib/auth.ts
export const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

export const getToken = () => {
  return localStorage.getItem('token');
};

export const clearToken = () => {
  localStorage.removeItem('token');
};
```

### Protected Routes

```typescript
// components/ProtectedRoute.tsx
export const ProtectedRoute = ({ children }) => {
  const [isAuthed, setIsAuthed] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/login');
    } else {
      setIsAuthed(true);
    }
  }, []);

  return isAuthed ? children : null;
};
```

## Development

### Setup

```bash
npm install
npm run dev
```

Open http://localhost:3000

### Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_SERVICE_NAME=LearnFlow
```

### Code Generation

```bash
# Generate pages
npx create-next-app --template typescript

# Add component
npx shadcn-ui@latest add button
```

### Hot Reload

Changes to files automatically reload in browser.

### Build

```bash
npm run build
npm run start  # Production
```

## Testing

### Unit Tests

```bash
npm test
```

### Component Tests

```typescript
// __tests__/Editor.test.tsx
import { render, screen } from '@testing-library/react';
import { Editor } from '@/components/Editor';

test('Editor renders code input', () => {
  render(<Editor />);
  expect(screen.getByRole('textbox')).toBeInTheDocument();
});
```

### E2E Tests (Optional)

```bash
npm install -D cypress
npx cypress open
```

## Docker

### Build Image

```bash
docker build -t learnflow-frontend:latest .
docker run -p 3000:3000 learnflow-frontend:latest
```

### Multi-Stage Build

Dockerfile uses multi-stage build for optimization:
1. Build stage: Install dependencies and build Next.js app
2. Runtime stage: Run production optimized app

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-frontend
  namespace: learnflow
spec:
  replicas: 2
  selector:
    matchLabels:
      app: learnflow-frontend
  template:
    metadata:
      labels:
        app: learnflow-frontend
    spec:
      containers:
      - name: nextjs
        image: learnflow-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_BASE
          value: "http://triage-agent:8001"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: learnflow-frontend
  namespace: learnflow
spec:
  selector:
    app: learnflow-frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer  # or NodePort for Minikube
```

### Deploy

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods -n learnflow
kubectl port-forward service/learnflow-frontend 3000:3000 -n learnflow
```

## Performance Optimization

### Image Optimization

```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="LearnFlow"
  width={200}
  height={200}
  priority  // Load immediately
/>
```

### Code Splitting

```typescript
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@/components/Editor'), {
  loading: () => <p>Loading editor...</p>,
  ssr: false  // Don't render on server
});
```

### Caching

```typescript
// Cache API responses
const cached = new Map();

export const submitQuery = async (studentId: number, query: string) => {
  const key = `${studentId}:${query}`;
  if (cached.has(key)) {
    return cached.get(key);
  }
  const response = await api.post('/api/query', { student_id: studentId, query });
  cached.set(key, response.data);
  return response.data;
};
```

## Error Handling

### Error Boundary

```typescript
export class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    this.setState({ hasError: true });
  }

  render() {
    if (this.state?.hasError) {
      return <div>Something went wrong. Please refresh.</div>;
    }
    return this.props.children;
  }
}
```

### API Error Handling

```typescript
try {
  const response = await submitQuery(studentId, query);
  setResponse(response);
} catch (error) {
  if (error.response?.status === 404) {
    setError('Service not found');
  } else if (error.response?.status === 500) {
    setError('Server error');
  } else {
    setError('Network error');
  }
}
```

## Troubleshooting

### Port 3000 Already in Use

```bash
npm run dev -- -p 3001
```

### Module Not Found

```bash
rm -rf node_modules package-lock.json
npm install
```

### Next.js Build Errors

```bash
npm run build -- --debug
```

## Environment Setup

### Required Variables

- `NEXT_PUBLIC_API_BASE`: Backend API base URL
- `NEXT_PUBLIC_SERVICE_NAME`: Application name

### Optional Variables

- `NEXT_PUBLIC_ENABLE_ANALYTICS`: Enable tracking
- `NEXT_PUBLIC_LOG_LEVEL`: Logging level

## Migration and Scaling

### Add New Pages

```bash
# Create new page
mkdir -p app/feature
touch app/feature/page.tsx
```

### Add New Components

```bash
# Create component
touch components/MyComponent.tsx
```

### Connect Additional Backends

Update `lib/api.ts` to add new endpoints:

```typescript
export const submitDebugQuery = (studentId: number, error: string) =>
  api.post('/api/debug', { student_id: studentId, error });
```

## Advanced Features

### Real-Time Updates (Tier 2)

Add WebSocket support for real-time agent responses:

```typescript
import io from 'socket.io-client';

const socket = io(process.env.NEXT_PUBLIC_API_BASE);
socket.on('response', (data) => setResponse(data));
```

### Monitoring

Add analytics and error tracking:

```typescript
import { Sentry } from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
});
```
