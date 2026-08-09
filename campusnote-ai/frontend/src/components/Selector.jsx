import React from 'react'
import { ChevronDown } from 'lucide-react'

export default function Selector({ label, value, onChange, options, placeholder = 'Any' }) {
  return (
    <div className="relative">
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none text-xs font-medium bg-gray-100 dark:bg-navy-800 border border-gray-200 dark:border-navy-700 rounded-lg pl-3 pr-7 py-1.5 focus:outline-none focus:ring-2 focus:ring-accent-500 text-gray-700 dark:text-gray-200"
      >
        <option value="">{label}: {placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400" />
    </div>
  )
}
