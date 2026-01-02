# Claude Code Skills

Reusable skills for this project covering authentication (Better Auth) and Kubernetes development.

---

## Authentication Skills (Better Auth)

Production-tested patterns for Better Auth with Next.js frontend and FastAPI backend.

### Quick Reference

| Skill | Description | When to Use |
|-------|-------------|-------------|
| [auth.betterAuth](auth.betterAuth.md) | Server-side Better Auth setup | Initial setup, database config |
| [auth.frontend](auth.frontend.md) | Client-side auth client | Token management, API calls |
| [auth.hook](auth.hook.md) | React hooks (useAuth) | Login/logout, session state |
| [auth.backendjwt](auth.backendjwt.md) | FastAPI JWT verification | Protecting API routes |
| [auth.protectedRoutes](auth.protectedRoutes.md) | Route protection patterns | Middleware, ownership checks |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    Session     ┌──────────────────┐           │
│  │   Next.js    │ ◄────────────► │   Better Auth    │           │
│  │   Frontend   │    Cookie      │   (Next.js API)  │           │
│  └──────┬───────┘                └────────┬─────────┘           │
│         │                                  │                     │
│         │ JWT Token                        │ JWKS                │
│         │ (Bearer)                         │ Endpoint            │
│         ▼                                  ▼                     │
│  ┌──────────────┐                ┌──────────────────┐           │
│  │   FastAPI    │ ◄───Verify───► │  /api/auth/      │           │
│  │   Backend    │    via JWKS    │  .well-known/    │           │
│  └──────────────┘                │  jwks.json       │           │
│                                  └──────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Key Patterns

1. **Server Setup**: `jwt()` + `nextCookies()` plugins
2. **Client Setup**: `jwtClient()` plugin with bearer token handling
3. **Token Storage**: localStorage with expiration checking
4. **Backend Verification**: JWKS-based (EdDSA), not shared secret

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Cookie not set | Add origin to `trustedOrigins`, disable `useSecureCookies` for HTTP |
| 401 on backend | Check JWKS endpoint accessible, verify token format |
| Session undefined | Use `credentials: 'include'` in fetch |
| DB connection errors | Use singleton pattern for pg Pool |

---

## Kubernetes Skills

Local Kubernetes development with Docker, Minikube, and kubectl in WSL2.

### Quick Reference

| Skill | Description | When to Use |
|-------|-------------|-------------|
| [k8s.setup](k8s.setup.md) | Environment setup | Initial setup, missing tools |
| [k8s.start](k8s.start.md) | Start cluster | Daily startup, recovery |
| [k8s.deploy](k8s.deploy.md) | Deploy applications | After code changes |
| [k8s.status](k8s.status.md) | Check status | Debugging, health checks |
| [k8s.portforward](k8s.portforward.md) | Port forwarding | Local testing, API access |
| [k8s.logs](k8s.logs.md) | View logs | Debugging, monitoring |
| [k8s.cleanup](k8s.cleanup.md) | Clean up resources | Reset, free resources |

### Development Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    K8S DEVELOPMENT WORKFLOW                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. k8s.setup     ──►  First time / new machine setup       │
│         │                                                    │
│         ▼                                                    │
│  2. k8s.start     ──►  Start Docker + Minikube              │
│         │                                                    │
│         ▼                                                    │
│  3. k8s.deploy    ──►  Build & deploy your app              │
│         │                                                    │
│         ▼                                                    │
│  4. k8s.portforward ─► Access services locally              │
│         │                                                    │
│         ▼                                                    │
│  5. k8s.status    ──►  Check everything is running          │
│         │                                                    │
│    ┌────┴────┐                                              │
│    │ Issues? │                                               │
│    └────┬────┘                                              │
│         │                                                    │
│         ▼                                                    │
│  6. k8s.logs      ──►  Debug with logs                      │
│         │                                                    │
│         ▼                                                    │
│  7. k8s.cleanup   ──►  Clean up when done                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Quick Commands

```bash
# Start cluster
minikube start --driver=docker

# Deploy app
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
helm upgrade --install todo-app ./helm-charts/todo-app

# Access services
kubectl port-forward service/todo-app-backend 8000:8000 &
curl http://localhost:8000/health

# Cleanup
minikube stop
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `kubectl: command not found` | See [k8s.setup](k8s.setup.md) |
| `Docker not found in WSL` | Enable WSL integration in Docker Desktop |
| `connection refused` | Run `minikube start` |
| `ImagePullBackOff` | `minikube image load <image>` |
| `CrashLoopBackOff` | `kubectl logs <pod> --previous` |

---

## Environment Requirements

### For Authentication
- Node.js 18+
- PostgreSQL (Neon for production)
- Better Auth configured

### For Kubernetes
- Windows with Docker Desktop + WSL2
- kubectl, minikube installed
- Helm (optional)

---

## All Skills List

### Authentication
- `auth.betterAuth` - Server setup
- `auth.frontend` - Client setup
- `auth.hook` - React hooks
- `auth.backendjwt` - FastAPI JWT
- `auth.protectedRoutes` - Route protection
- `auth.form` - Form components
- `auth.errorHandling` - Error handling
- `auth.2fa.*` - Two-factor auth
- `auth.magicLink.*` - Magic link auth
- `auth.social.*` - Social OAuth

### Kubernetes
- `k8s.setup` - Environment setup
- `k8s.start` - Start cluster
- `k8s.deploy` - Deploy apps
- `k8s.status` - Check status
- `k8s.portforward` - Port forwarding
- `k8s.logs` - View logs
- `k8s.cleanup` - Cleanup

### Other
- `frontend-api-client` - API client patterns
