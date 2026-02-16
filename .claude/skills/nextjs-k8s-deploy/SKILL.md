---
name: nextjs-k8s-deploy
description: Deploy Next.js frontend to Kubernetes with Monaco editor
version: 1.0.0
cross-agent: claude-code,goose
token-cost: 130
---

# Deploy Next.js Frontend to Kubernetes

Creates and deploys Next.js student dashboard to Kubernetes with Monaco code editor integration, TailwindCSS styling, and API connections to backend agents.

## When to Use

Use this skill when you need to:
- Deploy LearnFlow Next.js frontend to Kubernetes
- Create Next.js app with Monaco code editor
- Setup TailwindCSS styling and responsive layout
- Configure API calls to backend services
- Deploy with Dockerfile and K8s manifests

## Usage

```bash
claude "Use nextjs-k8s-deploy skill to generate learnflow-frontend"
```

## Parameters

- **app-name**: Application name (learnflow-frontend, default)
- **port**: Port number (3000, default)
- **include-docker**: Include Dockerfile (default: true)
- **include-k8s**: Include Kubernetes manifests (default: true)
- **include-tests**: Include test suite (default: true)

## Output

Creates directory with complete Next.js application:

```
learnflow-frontend/
├── app/
│   ├── page.tsx              # Home page
│   ├── dashboard/
│   │   └── page.tsx          # Student dashboard
│   ├── login/
│   │   └── page.tsx          # Authentication
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── Editor.tsx            # Monaco code editor
│   ├── Dashboard.tsx         # Student dashboard
│   ├── ChatBox.tsx           # AI chat interface
│   └── ModuleList.tsx        # Learning modules
├── lib/
│   └── api.ts               # API client
├── public/                   # Static assets
├── package.json             # Dependencies
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # TailwindCSS config
├── tsconfig.json            # TypeScript config
├── Dockerfile               # Docker image
├── deployment.yaml          # Kubernetes deployment
├── service.yaml             # Kubernetes service
└── __tests__/               # Test files
```

## Features Included

### Pages
- **Home**: Landing page with login link
- **Dashboard**: Student learning dashboard with:
  - 8 Python modules (Basics, Control Structures, Functions, etc.)
  - Progress tracking
  - Current topic display
  - Mastery scores

- **Editor**: Monaco code editor with:
  - Python syntax highlighting
  - Code submission button
  - Real-time feedback display
  - Example code snippets

- **Login**: Simple authentication with:
  - Email/password form
  - User registration
  - Session management

### Components
- **CodeEditor**: Monaco editor with syntax highlighting and submission
- **ChatBox**: Real-time chat with AI tutors
- **ModuleList**: Display of 8 Python learning modules
- **ProgressBar**: Student progress visualization
- **ResponseDisplay**: AI response formatting and display

### API Integration
- **POST /api/query**: Send query to Triage Agent
- **POST /api/explain**: Get concept explanation
- **POST /api/review**: Submit code for review

## Examples

Generate basic frontend:
```bash
claude "Use nextjs-k8s-deploy skill"
```

Generate with custom port:
```bash
claude "Use nextjs-k8s-deploy skill with port=3001"
```

Generate without tests:
```bash
claude "Use nextjs-k8s-deploy skill with include-tests=false"
```

## Configuration

### API Endpoints

Edit `lib/api.ts` to configure backend URLs:

```typescript
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
export const TRIAGE_ENDPOINT = `${API_BASE}/api/query`;
export const CONCEPTS_ENDPOINT = `${API_BASE}/api/explain`;
export const CODE_REVIEW_ENDPOINT = `${API_BASE}/api/review`;
```

### Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_BASE=http://localhost:8001
NEXT_PUBLIC_SERVICE_NAME=LearnFlow
```

## Deployment

### Local Development

```bash
npm install
npm run dev
# Open http://localhost:3000
```

### Docker Build

```bash
docker build -t learnflow-frontend:latest .
docker run -p 3000:3000 learnflow-frontend:latest
```

### Kubernetes Deployment

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
minikube service learnflow-frontend -n learnflow
```

## Validation

Generated app should:
- [ ] Run with `npm run dev`
- [ ] Display home page at http://localhost:3000
- [ ] Have responsive layout (mobile/tablet/desktop)
- [ ] Load dashboard with 8 modules
- [ ] Show Monaco editor on editor page
- [ ] Submit code to backend
- [ ] Display API responses
- [ ] Build with `npm run build`
- [ ] Deploy to Kubernetes

---

**See [REFERENCE.md](./REFERENCE.md) for customization and component details.**
