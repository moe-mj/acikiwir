import type { FooterColumn } from '../types/content'

export const navLinks = [
  { label: 'Beranda', href: '#beranda' },
  { label: 'Riwayat', href: '#riwayat' },
  { label: 'Tentang Kami', href: '#tentang-kami' },
]

export const footerColumns: FooterColumn[] = [
  {
    title: 'Cek Kredibilitas',
    links: [
      { label: 'Cek Toko', href: '#cek-toko' },
      { label: 'Riwayat', href: '#riwayat' },
    ],
  },
  {
    title: 'Keamanan & Transparansi',
    links: [
      { label: 'FAQ', href: '#faq' },
      { label: 'Kebijakan Privasi', href: '#privasi' },
      { label: 'Syarat & Ketentuan', href: '#syarat' },
    ],
  },
  {
    title: 'TrustPed',
    links: [
      { label: 'Tentang Kami', href: '#tentang-kami' },
      { label: 'Feedback', href: '#feedback' },
      { label: 'Hubungi Kami', href: '#kontak' },
    ],
  },
]
