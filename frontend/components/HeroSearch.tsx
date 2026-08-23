import { useState, type FormEvent } from 'react'
import { Loader2Icon, SearchIcon } from 'lucide-react'

interface HeroSearchProps {
  onSearch?: (url: string) => void
  loading?: boolean
}

const STORE_URL_PREFIX = 'https://www.e-commerce.com/'

export function HeroSearch({ onSearch, loading }: HeroSearchProps) {
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const storeId = value.trim()

    if (!storeId) {
      setError('Masukkan ID toko terlebih dahulu.')
      return
    }

    if (!/^\d+$/.test(storeId)) {
      setError('ID toko hanya boleh berisi angka. Contoh: 11111')
      return
    }

    setError(null)

    if (onSearch) {
      const storeUrl = `${STORE_URL_PREFIX}${storeId}`
      onSearch(storeUrl)
    }
  }

  return (
    <section
      id="beranda"
      className="w-full bg-[linear-gradient(180deg,#FFFFFF_0%,#EBEDF1_55%,#F5F6F8_100%)] transition-colors duration-200 dark:bg-[linear-gradient(180deg,#0f172a_0%,#020617_100%)]"
    >
      <div className="mx-auto flex max-w-[1180px] flex-col items-center px-5 pb-40 pt-24 text-center lg:px-8 lg:pb-52 lg:pt-32">
        <h1 className="max-w-4xl text-4xl font-bold leading-tight text-slate-900 transition-colors duration-200 dark:text-white sm:text-5xl lg:text-6xl">
          Belanja Aman Tanpa Ragu
        </h1>

        <p className="mt-7 max-w-3xl text-lg leading-8 text-slate-600 transition-colors duration-200 dark:text-slate-400 lg:text-xl">
          Cek kredibilitas toko sebelum membeli dengan analisis AI. Deteksi harga tidak wajar,
          ulasan mencurigakan, dan jejak digital toko secara cepat.
        </p>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="mt-12 w-full max-w-[1050px] text-left"
        >
          <label htmlFor="store-id" className="sr-only">
            Masukkan ID toko
          </label>

          <div
            className={`flex flex-col gap-3 rounded-md border-2 bg-white p-3 transition-colors duration-200 dark:bg-slate-900 sm:flex-row sm:items-center sm:gap-4 sm:p-4 ${error
                ? 'border-red-500'
                : 'border-slate-300 dark:border-slate-800'
              }`}
          >
            <SearchIcon
              className="hidden h-7 w-7 shrink-0 text-slate-400 dark:text-slate-500 sm:block"
              aria-hidden="true"
            />

            <div className="flex min-w-0 flex-1 items-center">
              <span className="shrink-0 text-lg font-medium text-slate-600 dark:text-slate-300 sm:text-xl">
                {STORE_URL_PREFIX}
              </span>

              <input
                id="store-id"
                type="text"
                inputMode="numeric"
                value={value}
                onChange={(event) => {
                  const input = event.target.value

                  if (/^\d*$/.test(input)) {
                    setValue(input)

                    if (error) {
                      setError(null)
                    }
                  }
                }}
                placeholder="11111"
                aria-invalid={Boolean(error)}
                aria-describedby={error ? 'store-id-error' : 'store-id-hint'}
                className="min-w-0 flex-1 bg-transparent text-lg font-semibold text-slate-900 placeholder:font-normal placeholder:text-slate-400 focus:outline-none dark:text-white dark:placeholder:text-slate-500 sm:text-xl"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-[3px] bg-emerald-600 px-7 py-3 text-lg font-semibold text-white transition-colors duration-150 ease-out hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 disabled:opacity-70"
            >
              {loading && (
                <Loader2Icon
                  className="h-5 w-5 animate-spin"
                  aria-hidden="true"
                />
              )}

              {loading ? 'Menganalisis' : 'Analisis Toko'}
            </button>
          </div>

          {error ? (
            <p
              id="store-id-error"
              role="alert"
              className="mt-3 text-base text-red-600"
            >
              {error}
            </p>
          ) : (
            <p
              id="store-id-hint"
              className="mt-3 text-base text-slate-500 dark:text-slate-400 lg:text-lg"
            >
              Contoh: https://www.e-commerce.com/11111
            </p>
          )}
        </form>
      </div>
    </section>
  )
}