import { useState } from "react";
import { Header } from "../components/Header";
import { HeroSearch } from "../components/HeroSearch";
import { ArticleSection } from "../components/ArticleSection";
import { Footer } from "../components/Footer";
import {
  AnalysisResult,
  type AnalysisData,
} from "../components/AnalysisResult";

const API_BASE_URL = "http://localhost:8000";

interface AnomalyData {
  score: number;
  explanation: string;
  top_features: string[];
}

interface BackendResponse {
  id: number;
  store_name: string;
  risk_score: number;
  status: "SAFE" | "WARNING" | "HIGH";

  thresholds: {
    warning: number;
    high: number;
  };

  price_anomaly: AnomalyData;
  review_anomaly: AnomalyData;
  information_anomaly: AnomalyData;

  overall_explanation: string;
}

function getStatusLabel(status: BackendResponse["status"]): string {
  switch (status) {
    case "SAFE":
      return "Risiko Rendah";
    case "WARNING":
      return "Risiko Sedang";
    case "HIGH":
      return "Risiko Tinggi";
  }
}

function getMetricLevel(score: number): string {
  if (score <= 30) return "Risiko Rendah";
  if (score <= 60) return "Risiko Sedang";
  if (score <= 90) return "Risiko Tinggi";
  return "Risiko Sangat Tinggi";
}

function transformBackendToAnalysisData(
  backendData: BackendResponse,
): AnalysisData {
  return {
    id: backendData.id,
    storeName: backendData.store_name,
    storeUrl: `ID Toko: #${backendData.id}`,

    riskScore: backendData.risk_score,
    riskStatus: backendData.status,
    riskLevel: getStatusLabel(backendData.status),

    thresholds: {
      warning: backendData.thresholds.warning,
      high: backendData.thresholds.high,
    },

    overallExplanation: backendData.overall_explanation,

    analyzedAt: "Baru saja",

    metrics: {
      priceRisk: {
        score: backendData.price_anomaly.score,
        level: getMetricLevel(backendData.price_anomaly.score),
        description: backendData.price_anomaly.explanation,
        topFeatures: backendData.price_anomaly.top_features,
      },

      reviewRisk: {
        score: backendData.review_anomaly.score,
        level: getMetricLevel(backendData.review_anomaly.score),
        description: backendData.review_anomaly.explanation,
        topFeatures: backendData.review_anomaly.top_features,
      },

      storeInfoRisk: {
        score: backendData.information_anomaly.score,
        level: getMetricLevel(backendData.information_anomaly.score),
        description: backendData.information_anomaly.explanation,
        topFeatures: backendData.information_anomaly.top_features,
      },
    },
  };
}

export function App() {
  const [analysisData, setAnalysisData] =
    useState<AnalysisData | null>(null);

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSearch = async (storeInput: string) => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const trimmedInput = storeInput.trim();
      
      // Ekstraksi angka dari input (mengambil deretan angka terakhir dari URL atau teks)
      const match = trimmedInput.match(/\d+$/) || trimmedInput.match(/(\d+)/);
      const storeId = match ? Number(match[0]) : NaN;

      if (!Number.isInteger(storeId) || storeId <= 0) {
        throw new Error("ID toko tidak valid. Masukkan angka ID atau URL yang mengandung ID toko.");
      }

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: storeId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || `Server mengembalikan error ${response.status}.`,
        );
      }

      const backendData: BackendResponse = await response.json();
      const formattedData = transformBackendToAnalysisData(backendData);
      setAnalysisData(formattedData);

    } catch (err) {
      console.error("Gagal melakukan analisis:", err);
      setErrorMsg(
        err instanceof Error
          ? err.message
          : "Gagal terhubung ke server backend.",
      );
    } finally {
      setLoading(false);
    }
  };

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
            <HeroSearch
              onSearch={handleSearch}
              loading={loading}
            />

            <ArticleSection />
          </>
        ) : (
          <AnalysisResult data={analysisData} />
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;