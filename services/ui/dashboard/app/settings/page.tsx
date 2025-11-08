/**
 * Settings Page
 * Centralized configuration management for AI Security Lab
 */

'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Settings as SettingsIcon, 
  Save, 
  RotateCcw, 
  Search,
  Database,
  HardDrive,
  Zap,
  Cpu,
  ToggleRight,
  Activity,
  Shield,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { settingsAPI } from '@/lib/api-client'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import type { SystemSetting, SettingsCategory } from '@/types'

const CATEGORY_ICONS: Record<string, any> = {
  database: Database,
  cache: HardDrive,
  services: Zap,
  performance: Cpu,
  features: ToggleRight,
  monitoring: Activity,
  security: Shield,
}

export default function SettingsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('database')
  const [searchQuery, setSearchQuery] = useState('')
  const [modifiedSettings, setModifiedSettings] = useState<Record<string, any>>({})
  const queryClient = useQueryClient()

  // Fetch all settings
  const { data: settings, isLoading, error } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsAPI.getAll,
    staleTime: 30000,
  })

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['settings-categories'],
    queryFn: settingsAPI.getCategories,
    staleTime: 60000,
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: any }) =>
      settingsAPI.update(key, value, 'current_user'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      setModifiedSettings({})
    },
  })

  // Reset mutation
  const resetMutation = useMutation({
    mutationFn: (key: string) => settingsAPI.reset(key, 'current_user'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })

  const handleValueChange = (key: string, value: any) => {
    setModifiedSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async (key: string) => {
    if (modifiedSettings[key] !== undefined) {
      await updateMutation.mutateAsync({ key, value: modifiedSettings[key] })
    }
  }

  const handleReset = async (key: string) => {
    await resetMutation.mutateAsync(key)
  }

  const handleSaveAll = async () => {
    for (const [key, value] of Object.entries(modifiedSettings)) {
      await updateMutation.mutateAsync({ key, value })
    }
  }

  // Filter settings
  const filteredSettings = settings?.filter((s: SystemSetting) => {
    const matchesCategory = selectedCategory === 'all' || s.category === selectedCategory
    const matchesSearch = !searchQuery || 
      s.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.description?.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  }) || []

  const hasModifications = Object.keys(modifiedSettings).length > 0

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <SettingsIcon className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                System Settings
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Configure system behavior and parameters
              </p>
            </div>
          </div>

          {/* Actions */}
          {hasModifications && (
            <div className="flex space-x-2">
              <button
                onClick={handleSaveAll}
                disabled={updateMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save All Changes</span>
              </button>
              <button
                onClick={() => setModifiedSettings({})}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Discard
              </button>
            </div>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search settings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Category Tabs */}
        <div className="flex space-x-2 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              selectedCategory === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            All Settings
          </button>
          {categories?.map((cat: SettingsCategory) => {
            const Icon = CATEGORY_ICONS[cat.id] || SettingsIcon
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 whitespace-nowrap ${
                  selectedCategory === cat.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{cat.name}</span>
                <span className="px-2 py-0.5 bg-white/20 rounded-full text-xs">{cat.count}</span>
              </button>
            )
          })}
        </div>

        {/* Settings List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : error ? (
            <div className="p-8 text-center text-red-600 dark:text-red-400">
              <AlertCircle className="w-12 h-12 mx-auto mb-4" />
              <p>Failed to load settings</p>
            </div>
          ) : filteredSettings.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              <p>No settings found</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredSettings.map((setting: SystemSetting) => {
                const currentValue = modifiedSettings[setting.key] !== undefined 
                  ? modifiedSettings[setting.key] 
                  : setting.value
                const isModified = modifiedSettings[setting.key] !== undefined

                return (
                  <div key={setting.key} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                            {setting.key}
                          </h3>
                          {setting.is_modified && !isModified && (
                            <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs rounded">
                              Modified
                            </span>
                          )}
                          {isModified && (
                            <span className="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 text-xs rounded">
                              Unsaved
                            </span>
                          )}
                          {setting.is_readonly && (
                            <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded">
                              Read-only
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {setting.description}
                        </p>

                        {/* Input based on type */}
                        {setting.value_type === 'boolean' ? (
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={currentValue === true}
                              onChange={(e) => handleValueChange(setting.key, e.target.checked)}
                              disabled={setting.is_readonly}
                              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700 dark:text-gray-300">
                              {currentValue ? 'Enabled' : 'Disabled'}
                            </span>
                          </label>
                        ) : setting.value_type === 'number' ? (
                          <input
                            type="number"
                            value={currentValue || ''}
                            onChange={(e) => handleValueChange(setting.key, Number(e.target.value))}
                            disabled={setting.is_readonly}
                            min={setting.validation?.min}
                            max={setting.validation?.max}
                            className="w-full max-w-xs px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                          />
                        ) : setting.validation?.options ? (
                          <select
                            value={currentValue || ''}
                            onChange={(e) => handleValueChange(setting.key, e.target.value)}
                            disabled={setting.is_readonly}
                            className="w-full max-w-xs px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                          >
                            {setting.validation.options.map(opt => (
                              <option key={opt} value={opt}>{opt}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type={setting.is_secret ? 'password' : 'text'}
                            value={currentValue || ''}
                            onChange={(e) => handleValueChange(setting.key, e.target.value)}
                            disabled={setting.is_readonly}
                            placeholder={setting.is_secret ? '***HIDDEN***' : `Default: ${setting.default_value}`}
                            className="w-full max-w-md px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                          />
                        )}

                        {/* Metadata */}
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                          <span>Type: {setting.value_type}</span>
                          <span>Category: {setting.category}</span>
                          {setting.modified_by && (
                            <span>Modified by: {setting.modified_by}</span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      {!setting.is_readonly && (
                        <div className="flex space-x-2 ml-4">
                          {isModified && (
                            <button
                              onClick={() => handleSave(setting.key)}
                              disabled={updateMutation.isPending}
                              className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm flex items-center space-x-1"
                            >
                              <CheckCircle className="w-4 h-4" />
                              <span>Save</span>
                            </button>
                          )}
                          {setting.is_modified && !isModified && (
                            <button
                              onClick={() => handleReset(setting.key)}
                              disabled={resetMutation.isPending}
                              className="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 text-sm flex items-center space-x-1"
                            >
                              <RotateCcw className="w-4 h-4" />
                              <span>Reset</span>
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Status Messages */}
        {updateMutation.isSuccess && (
          <div className="fixed bottom-4 right-4 px-4 py-3 bg-green-600 text-white rounded-lg shadow-lg flex items-center space-x-2">
            <CheckCircle className="w-5 h-5" />
            <span>Settings saved successfully</span>
          </div>
        )}

        {updateMutation.isError && (
          <div className="fixed bottom-4 right-4 px-4 py-3 bg-red-600 text-white rounded-lg shadow-lg flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span>Failed to save settings</span>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
