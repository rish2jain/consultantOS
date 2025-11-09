/**
 * Live Dashboard Page
 *
 * Real-time interactive dashboard view with WebSocket updates
 */

import { Metadata } from 'next';
import { InteractiveDashboard } from '@/app/components/InteractiveDashboard';

interface PageProps {
  params: {
    id: string;
  };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  return {
    title: `Dashboard ${params.id} | ConsultantOS`,
    description: 'Live interactive business intelligence dashboard',
  };
}

export default function DashboardPage({ params }: PageProps) {
  return (
    <div className="container mx-auto px-4 py-8">
      <InteractiveDashboard dashboardId={params.id} />
    </div>
  );
}
