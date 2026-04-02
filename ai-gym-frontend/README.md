# AI Gym Trainer Frontend

React client for live workout tracking and gamification UI.

## Prerequisites
- Node.js 18+
- Running backend API

## Environment Configuration

Create a .env file in this folder:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

For production, set this to your deployed backend URL, for example:

```env
REACT_APP_API_BASE_URL=https://your-api-domain.com
```

The app derives WebSocket URLs automatically from this value.

## Scripts

Install dependencies:

```bash
npm install
```

Run development server:

```bash
npm start
```

Create production build:

```bash
npm run build
```

## Deployment Checklist
1. Set REACT_APP_API_BASE_URL to your backend URL.
2. Run npm run build.
3. Deploy the build folder to your static host.
4. Confirm browser camera permission prompts and live websocket connectivity in production.
