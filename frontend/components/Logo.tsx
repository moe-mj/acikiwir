type LogoProps = {
  tone?: 'light' | 'dark'
  size?: 'sm' | 'lg'
}

export function Logo({ tone = 'light', size = 'sm' }: LogoProps) {
  const mark = size === 'sm' ? 'h-10 w-10' : 'h-12 w-12'
  const text = size === 'sm' ? 'text-2xl' : 'text-3xl'
  const trust = tone === 'light' ? 'text-navy' : 'text-white'
  const shield = tone === 'light' ? '#071B31' : '#FFFFFF'

  return (
    <a href="#beranda" className="flex items-center gap-2" aria-label="TrustPed beranda">
      <svg
        className={mark}
        viewBox="0 0 48 48"
        fill="none"
        aria-hidden="true"
        focusable="false"
      >
        <path
          d="M24 4 8 10v13c0 10 6.8 18.6 16 21 9.2-2.4 16-11 16-21V10L24 4Z"
          stroke={shield}
          strokeWidth="3"
          strokeLinejoin="round"
        />
        <circle cx="22" cy="20" r="6" stroke="#42B549" strokeWidth="3" />
        <path d="m26.5 24.5 4.5 4.5" stroke="#42B549" strokeWidth="3" strokeLinecap="round" />
        <path
          d="M15 27h13l-1.6 6H17l-2-6Z"
          stroke={shield}
          strokeWidth="2.4"
          strokeLinejoin="round"
        />
      </svg>
      <span className={`${text} font-bold tracking-tight ${trust}`}>
        Trust<span className="text-brand">Ped</span>
      </span>
    </a>
  )
}
