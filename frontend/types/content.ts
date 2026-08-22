export type Article = {
  id: string
  title: string
  excerpt: string
  imageUrl: string
  imageAlt: string
  readTime: string
  href: string
}

export type FooterColumn = {
  title: string
  links: { label: string; href: string }[]
}
