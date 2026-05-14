export default function LoadingSpinner({ size = 'md', label = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }
  return (
    <div className="flex items-center gap-2">
      <div className={`${sizes[size]} border-2 border-green-200 border-t-green-600 rounded-full animate-spin`} />
      {label && <span className="text-sm text-gray-500">{label}</span>}
    </div>
  )
}
