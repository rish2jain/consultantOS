/**
 * Live Dashboard Page
 *
 * Real-time interactive dashboard view with WebSocket updates
 */

import { Metadata } from 'next';
import { InteractiveDashboard } from '@/app/components/InteractiveDashboard';

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `Dashboard ${id} | ConsultantOS`,
    description: 'Live interactive business intelligence dashboard',
  };
}

export default async function DashboardPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <div className="container mx-auto px-4 py-8">
      <InteractiveDashboard dashboardId={id} />
    </div>
  );
}
