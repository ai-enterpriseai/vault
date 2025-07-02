import ThemeToggle from '../components/common/ThemeToggle'

export default function Dashboard() {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header with Theme Toggle */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold text-foreground">
            VAULT_APP v2.0
          </h1>
          <ThemeToggle />
        </div>

        {/* Success Banner */}
        <div className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg">
          <h3 className="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
            🚀 Phase A3: Tailwind CSS Foundation Complete!
          </h3>
          <p className="text-sm text-muted-foreground">
            React + TypeScript + Tailwind CSS foundation is ready. Theme switching, component styles, and design system are fully configured.
          </p>
        </div>
        
        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="card-header">
              <div className="card-title text-xl">AI Assistant</div>
              <div className="card-description">
                Chat with VAULT.AI for document analysis and questions
              </div>
            </div>
            <div className="card-content">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-success rounded-full"></div>
                Ready for implementation
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="card-header">
              <div className="card-title text-xl">Document Processing</div>
              <div className="card-description">
                Upload and index documents for intelligent search
              </div>
            </div>
            <div className="card-content">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-warning rounded-full"></div>
                Planned for Phase C
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="card-header">
              <div className="card-title text-xl">Workflow Automation</div>
              <div className="card-description">
                Run specialized sequences for business tasks
              </div>
            </div>
            <div className="card-content">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-info rounded-full"></div>
                6 templates ready
              </div>
            </div>
          </div>
        </div>

        {/* Component Showcase */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">Design System Showcase</h2>
          
          {/* Buttons */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Buttons</h3>
            <div className="flex flex-wrap gap-3">
              <button className="btn btn-primary btn-md">Primary</button>
              <button className="btn btn-secondary btn-md">Secondary</button>
              <button className="btn btn-outline btn-md">Outline</button>
              <button className="btn btn-ghost btn-md">Ghost</button>
              <button className="btn btn-destructive btn-md">Destructive</button>
            </div>
            <div className="flex flex-wrap gap-3">
              <button className="btn btn-primary btn-sm">Small</button>
              <button className="btn btn-primary btn-md">Medium</button>
              <button className="btn btn-primary btn-lg">Large</button>
            </div>
          </div>

          {/* Badges */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Badges</h3>
            <div className="flex flex-wrap gap-3">
              <span className="badge badge-default">Default</span>
              <span className="badge badge-secondary">Secondary</span>
              <span className="badge badge-success">Success</span>
              <span className="badge badge-warning">Warning</span>
              <span className="badge badge-destructive">Error</span>
              <span className="badge badge-outline">Outline</span>
            </div>
          </div>

          {/* Alerts */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Alerts</h3>
            <div className="space-y-3">
              <div className="alert alert-default">
                <div className="alert-title">Information</div>
                <div className="alert-description">
                  This is a default alert with some information.
                </div>
              </div>
              <div className="alert alert-success">
                <div className="alert-title">Success</div>
                <div className="alert-description">
                  Your action was completed successfully.
                </div>
              </div>
              <div className="alert alert-destructive">
                <div className="alert-title">Error</div>
                <div className="alert-description">
                  Something went wrong. Please try again.
                </div>
              </div>
            </div>
          </div>

          {/* Form Elements */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Form Elements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
              <input
                type="text"
                className="input"
                placeholder="Enter your message..."
              />
              <input
                type="email"
                className="input"
                placeholder="email@example.com"
              />
            </div>
          </div>

          {/* Loading Spinner */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Loading States</h3>
            <div className="flex gap-4 items-center">
              <div className="spinner w-4 h-4"></div>
              <div className="spinner w-6 h-6"></div>
              <div className="spinner w-8 h-8"></div>
              <span className="text-sm text-muted-foreground">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}