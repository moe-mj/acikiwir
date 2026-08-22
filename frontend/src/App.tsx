import { useState } from 'react'
import { Header } from '../components/Header'
import { HeroSearch } from '../components/HeroSearch'
import { ArticleSection } from '../components/ArticleSection'
import { Footer } from '../components/Footer'
import { AnalysisResult, type AnalysisData } from '../components/AnalysisResult'

const API_BASE_URL = 'http://localhost:8001'

interface BackendResponse {
  id: number
  store_name: string
  risk_score: number
  status: string
  price_anomaly: {
    score: number
    explanation: string
    top_features: string[]
  }
  review_anomaly: {
    score: number
    explanation: string
    top_features: string[]
  }
  information_anomaly: {
    score: number
    explanation: string
    top_features: string[]
  }
  overall_explanation: string
}

function getRiskLevelLabel(score: number): string {
  if (score <= 30) return 'Risiko Rendah'
  if (score <= 60) return 'Risiko Sedang'
  if (score <= 90) return 'Risiko Tinggi'
  return 'Risiko Sangat Tinggi'
}

function transformBackendToAnalysisData(
  backendData: BackendResponse,
  rawInput: string
): AnalysisData {
  return {
    storeName: backendData.store_name,
    storeUrl: isNaN(Number(rawInput)) ? rawInput : `ID Toko: #${rawInput}`,
    riskScore: Math.round(backendData.risk_score),
    riskLevel: backendData.status || getRiskLevelLabel(backendData.risk_score),
    analyzedAt: 'Baru saja',
    reviewManipulation: {
      reviewCountText: backendData.review_anomaly.top_features[0] || 'Deteksi Anomali Ulasan',
      description: backendData.review_anomaly.explanation || backendData.overall_explanation,
      syntheticPercentage: Math.min(100, Math.round(backendData.review_anomaly.score)),
    },
    metrics: {
      priceRisk: {
        score: Math.round(backendData.price_anomaly.score),
        level: getRiskLevelLabel(backendData.price_anomaly.score),
        description: backendData.price_anomaly.explanation,
      },
      reviewRisk: {
        score: Math.round(backendData.review_anomaly.score),
        level: getRiskLevelLabel(backendData.review_anomaly.score),
        description: backendData.review_anomaly.explanation,
      },
      storeInfoRisk: {
        score: Math.round(backendData.information_anomaly.score),
        level: getRiskLevelLabel(backendData.information_anomaly.score),
        description: backendData.information_anomaly.explanation,
      },
    },
  }
}

export function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const handleSearch = async (storeInput: string) => {
    setLoading(true)
    setErrorMsg(null)

    const storeId = parseInt(storeInput.replace(/\D/g, ''), 10) || 1

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: storeId }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Error server: ${response.status}`)
      }

      const backendData: BackendResponse = await response.json()
      
      const formattedData = transformBackendToAnalysisData(backendData, storeInput)
      setAnalysisData(formattedData)
    } catch (err: any) {
      console.error('Gagal terhubung ke backend:', err)
      setErrorMsg(err.message || 'Gagal terhubung ke server backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 font-sans transition-colors duration-200 dark:bg-slate-950">
      <Header />
      <main className="flex-1">
        {errorMsg && (
          <div className="mx-auto my-4 max-w-xl rounded-lg bg-red-100 p-4 text-center text-sm text-red-700">
            {errorMsg}
          </div>
        )}

        {!analysisData ? (
          <>
            <HeroSearch onSearch={handleSearch} loading={loading} />
            <ArticleSection />
          </>
        ) : (
          <AnalysisResult data={analysisData} />
        )}
      </main>
      <Footer />
    </div>
  )
}

export default App