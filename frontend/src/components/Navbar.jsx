import { Link, useLocation } from 'react-router-dom'
import { Upload, MessageSquare, Leaf } from 'lucide-react'

export default function Navbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/upload', label: 'Upload Docs', icon: <Upload size={17} /> },
    { to: '/chat',   label: 'Scheme Assistant', icon: <MessageSquare size={17} /> },
  ]

  return (
    <header className="bg-white border-b border-green-100 shadow-sm sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/chat" className="flex items-center gap-2 text-green-700 font-semibold text-lg">
          <Leaf size={22} className="text-green-500" />
          <span>AgriConnect AI</span>
        </Link>

        {/* Nav links */}
        <nav className="flex gap-1">
          {links.map(({ to, label, icon }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-all
                ${pathname === to
                  ? 'bg-green-600 text-white shadow-sm'
                  : 'text-green-700 hover:bg-green-50'
                }`}
            >
              {icon} {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
