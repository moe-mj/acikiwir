import { ArticleCard } from './ArticleCard'
import { articles } from '../data/article'

export function ArticleSection() {
  return (
    <section 
      aria-label="Berita penipuan online terbaru" 
      className="w-full bg-white transition-colors duration-200 dark:bg-slate-950"
    >
      <div className="mx-auto grid max-w-[1500px] gap-10 px-5 py-16 lg:grid-cols-2 lg:gap-12 lg:px-8 lg:py-24">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </section>
  )
}