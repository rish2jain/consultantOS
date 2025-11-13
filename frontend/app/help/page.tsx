import Link from 'next/link';

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Help & Support</h1>
          
          <div className="prose max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Getting Started</h2>
              <p className="text-gray-600 mb-4">
                Welcome to ConsultantOS! This platform helps you generate professional-grade business framework analyses using AI-powered agents.
              </p>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>Create your first analysis by navigating to the "Create Analysis" page</li>
                <li>Select one or more business frameworks (Porter's 5 Forces, SWOT, PESTEL, Blue Ocean Strategy)</li>
                <li>Choose your analysis depth (Quick, Standard, or Deep)</li>
                <li>Submit and wait for your comprehensive analysis report</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Business Frameworks</h2>
              <div className="space-y-4 text-gray-600">
                <div>
                  <h3 className="font-semibold text-gray-800">Porter's Five Forces</h3>
                  <p>Analyze competitive intensity and attractiveness of an industry through five key forces: competitive rivalry, supplier power, buyer power, threat of substitution, and threat of new entry.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">SWOT Analysis</h3>
                  <p>Identify internal strengths and weaknesses, and external opportunities and threats for strategic planning.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">PESTEL Analysis</h3>
                  <p>Examine political, economic, social, technological, environmental, and legal factors affecting your business environment.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Blue Ocean Strategy</h3>
                  <p>Discover uncontested market spaces and make competition irrelevant by creating new demand.</p>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Analysis Types</h2>
              <div className="space-y-4 text-gray-600">
                <div>
                  <h3 className="font-semibold text-gray-800">Quick Analysis</h3>
                  <p>High-level overview with key insights. Processing time: ~30 seconds. Best for quick snapshots.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Standard Analysis</h3>
                  <p>Balanced depth with comprehensive coverage. Processing time: ~1-2 minutes. Recommended for most use cases.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Deep Analysis</h3>
                  <p>Thorough investigation with detailed insights. Processing time: ~3-5 minutes. Best for comprehensive strategic planning.</p>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Features</h2>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li><strong>Reports:</strong> View and manage all your analysis reports</li>
                <li><strong>Jobs:</strong> Monitor active and pending analyses</li>
                <li><strong>Templates:</strong> Use pre-built analysis templates for common scenarios</li>
                <li><strong>Sharing:</strong> Share reports with team members and stakeholders</li>
                <li><strong>Comments:</strong> Collaborate on reports with comments and discussions</li>
                <li><strong>Version History:</strong> Track changes and restore previous versions</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Need More Help?</h2>
              <p className="text-gray-600 mb-4">
                If you have questions or need assistance, please contact our support team or refer to the documentation.
              </p>
            </section>

            <div className="mt-8 pt-6 border-t border-gray-200">
              <Link 
                href="/" 
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

