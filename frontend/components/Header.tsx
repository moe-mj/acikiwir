import { useState } from 'react'
import { MenuIcon, XIcon, SunIcon, MoonIcon } from 'lucide-react'
import { Logo } from './Logo'
import { navLinks } from '../data/navigation'
import { useDarkMode } from '../src/hooks/useDarkMode'

export function Header() {
  const [open, setOpen] = useState(false)
  const { isDark, toggleDarkMode } = useDarkMode()

  return (
    <header className="border-b border-[#EBEDF1] bg-white transition-colors duration-200 dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto flex h-[72px] max-w-[1500px] items-center justify-between px-5 lg:px-8">
        <div className="flex items-center gap-10">
          <Logo />
          <nav aria-label="Navigasi utama" className="hidden md:block">
            <ul className="flex items-center gap-9">
              {navLinks.map((link, index) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    aria-current={index === 0 ? 'page' : undefined}
                    className={`text-lg font-medium text-slate-800 transition-colors duration-150 ease-out hover:text-brand dark:text-slate-100 dark:hover:text-emerald-400 ${
                      index === 0 ? 'underline underline-offset-8' : ''
                    }`}
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* --- TOMBOL SAKELAR GAMBAR 2 --- */}
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={toggleDarkMode}
            aria-label="Toggle Light and Dark Mode"
            className={`relative flex h-10 w-20 items-center rounded-full p-1 transition-colors duration-300 focus:outline-none ${
              isDark ? 'bg-slate-950 border border-slate-800' : 'bg-slate-200 border border-slate-300'
            }`}
          >
            {/* Ikon Latar Belakang Sakelar */}
            <div className="flex w-full items-center justify-between px-1.5 text-slate-400">
              <SunIcon className={`h-4 w-4 ${!isDark ? 'opacity-0' : 'text-amber-400'}`} />
              <MoonIcon className={`h-4 w-4 ${isDark ? 'opacity-0' : 'text-slate-500'}`} />
            </div>

            {/* Bulatan Tombol Geser (Thumb) */}
            <div
              className={`absolute flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-md transition-transform duration-300 ease-in-out dark:bg-slate-800 ${
                isDark ? 'translate-x-[40px]' : 'translate-x-0'
              }`}
            >
              {isDark ? (
                <MoonIcon className="h-4 w-4 text-slate-200" />
              ) : (
                <SunIcon className="h-4 w-4 text-amber-500" />
              )}
            </div>
          </button>

          {/* Tombol Navigasi Seluler */}
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            aria-controls="mobile-nav"
            className="rounded-md p-2 text-slate-800 transition-colors hover:bg-[#EBEDF1] dark:text-slate-200 dark:hover:bg-slate-800 md:hidden"
          >
            <span className="sr-only">{open ? 'Tutup menu' : 'Buka menu'}</span>
            {open ? <XIcon className="h-6 w-6" /> : <MenuIcon className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {open && (
        <nav id="mobile-nav" aria-label="Navigasi seluler" className="border-t border-[#EBEDF1] bg-white dark:border-slate-800 dark:bg-slate-900 md:hidden">
          <ul className="mx-auto max-w-[1500px] px-5 py-2">
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block py-3 text-base font-medium text-slate-800 dark:text-slate-200"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  )
}