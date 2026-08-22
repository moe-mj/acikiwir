import { ArrowRightIcon, ClockIcon } from 'lucide-react'
import type { Article } from '../types/content'

type ArticleCardProps = {
  article: Article
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <a
      href={article.href}
      className="group flex h-full flex-col overflow-hidden rounded-xl border border-card-border bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all duration-200 ease-out hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="aspect-[16/9] w-full overflow-hidden bg-card-border dark:bg-slate-800">
        <img
          src={article.imageUrl}
          alt={article.imageAlt}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      </div>

      <div className="flex flex-1 flex-col p-5">
        <h3 className="text-2xl font-semibold leading-snug text-card-title dark:text-white lg:text-[28px]">
          {article.title}
        </h3>
        <p className="mt-3 text-base leading-7 text-card-body dark:text-slate-400 lg:text-lg">{article.excerpt}</p>

        <div className="mt-auto flex items-center justify-between border-t border-card-border dark:border-slate-800 pt-4">
          <span className="flex items-center gap-1.5 text-sm font-medium text-card-meta dark:text-slate-400">
            <ClockIcon className="h-4 w-4" aria-hidden="true" />
            {article.readTime}
          </span>
          <ArrowRightIcon
            className="h-4 w-4 text-brand-dark dark:text-emerald-400 transition-transform duration-200 ease-out group-hover:translate-x-1"
            aria-hidden="true"
          />
        </div>
      </div>
    </a>
  )
}