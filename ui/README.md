# VAJRA-CV Console

The `ui` directory contains the responsive React/Vite console for VAJRA-CV.

## Run locally

Start the backend from the repository root first, then run:

```powershell
Set-Location "C:\Users\YOUR_USER\vajra-cv\ui"
npm install
npm run dev
```

Open `http://127.0.0.1:5173/`.

## Demo login

```text
Email: admin@vajra.local
Password: local-password
API key: local-api-key
```

The flow is:

```text
Landing -> Login -> Command center
```

Use the dashboard moon/sun control for day/night mode. The hamburger control works across desktop, tablet, and phone layouts. Click the avatar to view the active user profile and sign out.

## Build

```powershell
npm run build
```

The main project guide and fixture paths are in the repository [README.md](../README.md).
