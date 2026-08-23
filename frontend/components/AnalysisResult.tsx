import {
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
} from 'lucide-react'

export interface RiskMetric {
  score: number
  level: string
  description: string
  topFeatures: string[]
}

export interface AnalysisData {
  id: number
  storeName: string
  storeUrl: string
  logoUrl?: string

  riskScore: number
  riskStatus: 'SAFE' | 'WARNING' | 'HIGH'
  riskLevel: string

  thresholds: {
    warning: number
    high: number
  }

  overallExplanation: string
  analyzedAt: string

  metrics: {
    priceRisk: RiskMetric
    reviewRisk: RiskMetric
    storeInfoRisk: RiskMetric
  }
}

interface AnalysisResultProps {
  data: AnalysisData
}

function getStatusColor(
  status: AnalysisData['riskStatus']
) {
  switch (status) {
    case 'SAFE':
      return {
        text: 'text-emerald-600',
        bg: 'bg-emerald-50',
        border: 'border-emerald-200',
        bar: 'bg-emerald-500',
      }

    case 'WARNING':
      return {
        text: 'text-amber-600',
        bg: 'bg-amber-50',
        border: 'border-amber-200',
        bar: 'bg-amber-500',
      }

    case 'HIGH':
      return {
        text: 'text-red-600',
        bg: 'bg-red-50',
        border: 'border-red-200',
        bar: 'bg-red-500',
      }
  }
}

function getMetricColor(score: number) {
  if (score <= 30) {
    return {
      text: 'text-emerald-600',
      bar: 'bg-emerald-500',
      border: 'border-emerald-200',
      bg: 'bg-emerald-50',
    }
  }

  if (score <= 60) {
    return {
      text: 'text-amber-600',
      bar: 'bg-amber-500',
      border: 'border-amber-200',
      bg: 'bg-amber-50',
    }
  }

  return {
    text: 'text-red-600',
    bar: 'bg-red-500',
    border: 'border-red-200',
    bg: 'bg-red-50',
  }
}

function RiskMetricCard({
  title,
  metric,
}: {
  title: string
  metric: RiskMetric
}) {
  const colors = getMetricColor(metric.score)

  return (
    <div
      className={`rounded-2xl border ${colors.border} bg-white p-6 shadow-sm`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-800">
          {title}
        </h3>

        <span
          className={`rounded-full px-3 py-1 text-xs font-bold ${colors.bg} ${colors.text}`}
        >
          {metric.level}
        </span>
      </div>

      <div
        className={`mt-4 text-5xl font-black ${colors.text}`}
      >
        {metric.score.toFixed(2)}

        <span className="text-xl font-normal text-slate-400">
          {' '}
          /100
        </span>
      </div>

      <div className="mt-4 h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full transition-all duration-500 ${colors.bar}`}
          style={{
            width: `${Math.min(
              100,
              Math.max(0, metric.score)
            )}%`,
          }}
        />
      </div>

      <p className="mt-4 text-sm leading-relaxed text-slate-600">
        {metric.description}
      </p>

      {metric.topFeatures.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-slate-400">
            Faktor Paling Berpengaruh
          </p>

          <div className="flex flex-wrap gap-2">
            {metric.topFeatures.map(
              (feature) => (
                <span
                  key={feature}
                  className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600"
                >
                  {feature}
                </span>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function AnalysisResult({
  data,
}: AnalysisResultProps) {
  const statusColors = getStatusColor(
    data.riskStatus
  )

  return (
    <section className="mx-auto max-w-[1400px] px-5 py-10 lg:px-8">
      <h1 className="mb-8 text-3xl font-extrabold text-slate-900">
        Hasil Analisis Toko
      </h1>

      {/* BAGIAN ATAS */}
      <div className="grid gap-6 lg:grid-cols-3">

        {/* PROFIL TOKO + RISK SCORE */}
        <div className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <div className="flex flex-col items-center gap-6 md:flex-row">

            {/* LOGO */}
            <div className="flex h-36 w-36 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 p-2">
              <img
                src={
                  data.logoUrl ||
                  'https://placehold.co/150x150?text=Logo+Toko'
                }
                alt={data.storeName}
                className="max-h-full max-w-full object-contain"
              />
            </div>

            {/* STORE INFO */}
            <div className="flex-1 text-center md:text-left">

              <h2 className="text-2xl font-bold text-slate-900">
                {data.storeName}
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                {data.storeUrl}
              </p>

              {/* RISK SCORE */}
              <div
                className={`mt-5 rounded-xl p-5 ${statusColors.bg}`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-500">
                    Skor Risiko
                  </span>

                  <span
                    className={`text-lg font-bold ${statusColors.text}`}
                  >
                    {data.riskLevel}
                  </span>
                </div>

                <div
                  className={`mt-2 text-5xl font-black ${statusColors.text}`}
                >
                  {data.riskScore.toFixed(2)}

                  <span className="text-base font-normal text-slate-400">
                    {' '}
                    /100
                  </span>
                </div>

                {/* PROGRESS BAR */}
                <div className="mt-5 h-3 w-full overflow-hidden rounded-full bg-slate-200">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${statusColors.bar}`}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(
                          0,
                          data.riskScore
                        )
                      )}%`,
                    }}
                  />
                </div>

                <div className="mt-2 flex justify-between text-[11px] font-semibold text-slate-400">
                  <span className="text-emerald-600">
                    Low
                  </span>

                  <span className="text-amber-500">
                    Warning
                  </span>

                  <span className="text-red-500">
                    High
                  </span>
                </div>
              </div>
            </div>
          </div>

          <p className="mt-5 text-xs text-slate-400">
            Analisis selesai: {data.analyzedAt}
          </p>
        </div>

        {/* STATUS TOKO */}
        <div
          className={`flex flex-col justify-between rounded-2xl border ${statusColors.border} ${statusColors.bg} p-6 shadow-sm`}
        >
          <div>
            <div className="flex items-center gap-2">

              {data.riskStatus === 'SAFE' && (
                <CheckCircle2 className="h-6 w-6 text-emerald-600" />
              )}

              {data.riskStatus === 'WARNING' && (
                <AlertTriangle className="h-6 w-6 text-amber-600" />
              )}

              {data.riskStatus === 'HIGH' && (
                <ShieldAlert className="h-6 w-6 text-red-600" />
              )}

              <span
                className={`font-bold ${statusColors.text}`}
              >
                Status Toko
              </span>
            </div>

            <h3
              className={`mt-5 text-4xl font-extrabold ${statusColors.text}`}
            >
              {data.riskStatus}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              {data.riskLevel}
            </p>
          </div>

          {/* SCORE */}
          <div className="mt-8 rounded-xl bg-white/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Risk Score
            </p>

            <p
              className={`mt-1 text-3xl font-black ${statusColors.text}`}
            >
              {data.riskScore.toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* RINGKASAN ANALISIS - SEKALI SAJA */}
      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start gap-3">
          <ShieldAlert className="mt-0.5 h-6 w-6 shrink-0 text-slate-500" />

          <div>
            <h3 className="text-lg font-bold text-slate-800">
              Ringkasan Analisis
            </h3>

            <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-600">
              {data.overallExplanation}
            </p>
          </div>
        </div>
      </div>

      {/* METRIK */}
      <div className="mt-6 grid gap-6 md:grid-cols-3">

        <RiskMetricCard
          title="Harga Produk"
          metric={data.metrics.priceRisk}
        />

        <RiskMetricCard
          title="Ulasan & Reputasi"
          metric={data.metrics.reviewRisk}
        />

        <RiskMetricCard
          title="Informasi Toko"
          metric={data.metrics.storeInfoRisk}
        />

      </div>
    </section>
  )
}