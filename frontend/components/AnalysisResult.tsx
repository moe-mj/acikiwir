import { ShieldAlert } from 'lucide-react'

export interface AnalysisData {
  storeName: string
  storeUrl: string
  logoUrl?: string
  riskScore: number
  riskLevel: string
  analyzedAt: string
  reviewManipulation: {
    reviewCountText: string
    description: string
    syntheticPercentage: number
  }
  metrics: {
    priceRisk: { score: number; level: string; description: string }
    reviewRisk: { score: number; level: string; description: string }
    storeInfoRisk: { score: number; level: string; description: string }
  }
}

interface AnalysisResultProps {
  data: AnalysisData
}

export function AnalysisResult({ data }: AnalysisResultProps) {
  return (
    <section className="mx-auto max-w-[1400px] px-5 py-10 lg:px-8">
      <h1 className="mb-8 text-3xl font-extrabold text-slate-900">Hasil Analisis Toko</h1>

      {/* Grid Atas */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Kartu Profil Toko & Skor Utama */}
        <div className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
          <div className="flex flex-col items-center gap-6 md:flex-row">
            <div className="flex h-36 w-36 shrink-0 items-center justify-center rounded-xl border border-emerald-500 p-2">
              <img
                src={data.logoUrl || 'https://placehold.co/150x150?text=Logo+Toko'}
                alt={data.storeName}
                className="max-h-full max-w-full object-contain"
              />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-slate-900">{data.storeName}</h2>
              <p className="text-sm text-slate-400">{data.storeUrl}</p>

              <div className="mt-4 rounded-xl bg-slate-50 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-500">Skor Risiko</span>
                  <span className="text-lg font-bold text-red-600">{data.riskLevel}</span>
                </div>
                <div className="mt-1 text-4xl font-black text-red-600">
                  {data.riskScore} <span className="text-base font-normal text-slate-400">/100</span>
                </div>

                {/* Progress Bar Risiko */}
                <div className="mt-4 h-3 w-full rounded-full bg-slate-200">
                  <div
                    className="h-3 rounded-full bg-red-500 transition-all duration-500"
                    style={{ width: `${data.riskScore}%` }}
                  />
                </div>
                <div className="mt-2 flex justify-between text-[11px] font-semibold text-slate-400">
                  <span className="text-emerald-600">Low (0-30)</span>
                  <span>Medium (31-60)</span>
                  <span className="text-red-500">High (61-90)</span>
                  <span>Very High (91-100)</span>
                </div>
              </div>
            </div>
          </div>
          <p className="mt-4 text-xs text-slate-400">Analisis selesai: {data.analyzedAt}</p>
        </div>

        {/* Kartu Review Manipulation */}
        <div className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <div className="flex items-center gap-2 font-bold text-emerald-600">
              <ShieldAlert className="h-5 w-5" />
              <span>Review Manipulation</span>
            </div>
            <h3 className="mt-4 text-3xl font-extrabold text-slate-900">
              {data.reviewManipulation.reviewCountText}
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              {data.reviewManipulation.description}
            </p>
          </div>

          <div className="mt-6">
            <div className="mb-1 flex justify-between text-xs font-semibold text-slate-500">
              <span>Authentic vs Synthetic</span>
              <span>
                {100 - data.reviewManipulation.syntheticPercentage}% / {data.reviewManipulation.syntheticPercentage}%
              </span>
            </div>
            <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-emerald-500">
              <div
                className="bg-red-500 transition-all duration-500"
                style={{ width: `${data.reviewManipulation.syntheticPercentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Grid Bawah - 3 Metrik Utama */}
      <div className="mt-6 grid gap-6 md:grid-cols-3">
        {/* Harga Produk */}
        <div className="rounded-2xl border-2 border-sky-500 bg-white p-6 text-center shadow-sm">
          <h3 className="text-xl font-bold text-slate-800">Harga Produk</h3>
          <div className="mt-4 text-5xl font-black text-red-500">
            {data.metrics.priceRisk.score} <span className="text-xl font-normal text-slate-400">/100</span>
          </div>
          <p className="mt-3 font-bold text-red-600">{data.metrics.priceRisk.level}</p>
          <p className="mt-1 text-xs text-slate-500">{data.metrics.priceRisk.description}</p>
        </div>

        {/* Ulasan & Reputasi */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <h3 className="text-xl font-bold text-slate-800">Ulasan & Reputasi</h3>
          <div className="mt-4 text-5xl font-black text-amber-500">
            {data.metrics.reviewRisk.score} <span className="text-xl font-normal text-slate-400">/100</span>
          </div>
          <p className="mt-3 font-bold text-amber-600">{data.metrics.reviewRisk.level}</p>
          <p className="mt-1 text-xs text-slate-500">{data.metrics.reviewRisk.description}</p>
        </div>

        {/* Informasi Toko */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <h3 className="text-xl font-bold text-slate-800">Informasi Toko</h3>
          <div className="mt-4 text-5xl font-black text-emerald-500">
            {data.metrics.storeInfoRisk.score} <span className="text-xl font-normal text-slate-400">/100</span>
          </div>
          <p className="mt-3 font-bold text-emerald-600">{data.metrics.storeInfoRisk.level}</p>
          <p className="mt-1 text-xs text-slate-500">{data.metrics.storeInfoRisk.description}</p>
        </div>
      </div>
    </section>
  )
}