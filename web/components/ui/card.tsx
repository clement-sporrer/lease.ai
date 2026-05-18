import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface CardProps {
  children: ReactNode
  className?: string
}

interface CardHeaderProps {
  title: string
  action?: ReactNode
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn('bg-white rounded-xl border border-gray-100 shadow-sm', className)}>
      {children}
    </div>
  )
}

export function CardHeader({ title, action }: CardHeaderProps) {
  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
      <h2 className="text-sm font-semibold text-navy-900">{title}</h2>
      {action}
    </div>
  )
}

export function CardBody({ children, className }: CardProps) {
  return <div className={cn('px-6 py-5', className)}>{children}</div>
}
