# ConsultantOS Dashboard

Modern React/Next.js dashboard for ConsultantOS business intelligence platform.

## Features

- **User Authentication**: Login and registration with email verification
- **Report History**: View, filter, and manage all generated reports
- **Usage Statistics**: Track metrics and performance analytics
- **API Key Management**: Create, rotate, and revoke API keys
- **Report Management**: View, download, share, and export reports
- **Report Sharing**: Create shareable links with permissions
- **Comments & Collaboration**: Comment threads on reports
- **Template Library**: Browse and use framework templates
- **Version History**: View and compare report versions
- **Community**: Browse case studies and best practices

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
npm start
```

## Tech Stack

- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **TanStack Query**: Data fetching
- **Axios**: HTTP client
- **Lucide React**: Icons

