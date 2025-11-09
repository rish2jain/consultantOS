'use client'

import dynamic from 'next/dynamic'
import type { Data, Layout } from 'plotly.js'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

type PlotlyChartProps = {
  title: string
  figure: {
    data: Data[]
    layout?: Partial<Layout>
  }
}

export function PlotlyChart({ title, figure }: PlotlyChartProps) {
  if (!figure) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <Plot data={figure.data} layout={figure.layout} config={{ displayModeBar: false }} style={{ width: '100%', height: '100%' }} />
    </div>
  )
}
