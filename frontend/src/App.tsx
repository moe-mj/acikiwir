import { useState } from 'react'
import { Header } from '../components/Header'
import { HeroSearch } from '../components/HeroSearch'
import { ArticleSection } from '../components/ArticleSection'
import { Footer } from '../components/Footer'
import { AnalysisResult, type AnalysisData } from '../components/AnalysisResult'

const API_BASE_URL = 'http://localhost:8000'

const mockResult: AnalysisData = {
  storeName: "Toko Maju Jaya",
  storeUrl: "https://www.e-commerce.com/majujayaofficial",
  riskScore: 78,
  riskLevel: "Tinggi",
  analyzedAt: "2 menit yang lalu",
  reviewManipulation: {
    reviewCountText: "500+ reviews in 1 hour",
    description: "Sudden influx of 5-star reviews originating from highly suspicious IP blocks. NLP analysis indicates repetitive phrasing and identical sentence structures.",
    syntheticPercentage: 95
  },
  metrics: {
    priceRisk: { score: 80, level: "Risiko Tinggi", description: "Anomali harga terdeteksi" },
    reviewRisk: { score: 60, level: "Risiko Sedang", description: "Pola ulasan mencurigakan" },
    storeInfoRisk: { score: 40, level: "Risiko Rendah", description: "Informasi dasar valid" }
  }
}

export function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async (storeUrl: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: storeUrl }),
      })

      if (!response.ok) {
        throw new Error('Gagal melakukan analisis toko.')
      }
      const data = await response.json()
      setAnalysisData(data)
    } catch (error) {
      console.warn("Backend belum terhubung / error, fallback ke data simulasi:", error)
      setAnalysisData(mockResult)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 font-sans transition-colors duration-200 dark:bg-slate-950">
      <Header />
      <main className="flex-1">
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