import { Logo } from './Logo'
import { footerColumns } from '../data/navigation'

export function Footer() {
  return (
    <footer id="tentang-kami" className="w-full bg-[var(--trustped-navy)] text-white">
      <div className="mx-auto max-w-[1500px] px-5 py-16 lg:px-8 lg:py-20">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,1.4fr)_repeat(3,minmax(0,1fr))]">
          <div className="max-w-xl">
            <Logo tone="dark" size="lg" />
            <p className="mt-8 text-xl font-bold">TrustPed by Acikiwir</p>
            <p className="mt-4 text-base font-medium italic leading-7 text-white/90">
              TrustPed adalah alat pengecekan toko berbasis AI yang membantu kamu menilai
              kredibilitas toko sebelum membeli. Analisis harga, ulasan, dan jejak digital toko
              untuk membantu kamu terhindar dari penipuan saat berbelanja online.
            </p>
          </div>

          {footerColumns.map((column) => (
            <nav key={column.title} aria-label={column.title}>
              <h2 className="text-xl font-bold">{column.title}</h2>
              <ul className="mt-5 space-y-3">
                {column.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-lg text-white/85 transition-colors duration-150 ease-out hover:text-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-ink"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>

        <hr className="mt-14 border-white/60" />
        <p className="mt-5 text-sm font-semibold text-white/90">
          © 2026 TrustPed, Inc. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
