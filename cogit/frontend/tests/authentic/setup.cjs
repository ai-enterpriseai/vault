/**
 * VAULT_APP Authentic Testing - Environment Setup & Validation
 * Validates real environment before executing authentic tests
 */

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

class AuthenticTestEnvironment {
  constructor() {
    this.baseUrl = 'http://localhost:5173'
    this.testResults = {
      environment: {},
      performance: {},
      failures: []
    }
  }

  async validateEnvironment() {
    console.log('🔍 Validating Authentic Test Environment...\n')

    // 1. Check if development server is running
    await this.checkDevServer()
    
    // 2. Validate Node.js and npm versions
    await this.checkNodeEnvironment()
    
    // 3. Verify dependencies are installed
    await this.checkDependencies()
    
    // 4. Test actual HTTP connection
    await this.checkHttpConnection()
    
    // 5. Validate browser capabilities
    await this.checkBrowserSupport()

    console.log('✅ Environment validation complete!\n')
    return this.testResults
  }

  async checkDevServer() {
    console.log('📡 Checking Vite development server...')
    
    try {
      const curl = execSync(`curl -f -s ${this.baseUrl}`, { encoding: 'utf8' })
      const hasReactRoot = curl.includes('<div id="root">')
      const hasViteScript = curl.includes('/src/main.tsx')
      
      if (hasReactRoot && hasViteScript) {
        console.log('  ✅ Development server running and serving React app')
        this.testResults.environment.devServer = {
          status: 'running',
          url: this.baseUrl,
          serving: 'react-app'
        }
      } else {
        throw new Error('Server not serving expected React application')
      }
    } catch (error) {
      console.log('  ❌ Development server not accessible')
      console.log('  💡 Run: npm run dev')
      this.testResults.failures.push({
        component: 'dev-server',
        error: error.message,
        solution: 'Start development server with: npm run dev'
      })
      throw error
    }
  }

  async checkNodeEnvironment() {
    console.log('🟢 Checking Node.js environment...')
    
    try {
      const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim()
      const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim()
      
      console.log(`  ✅ Node.js: ${nodeVersion}`)
      console.log(`  ✅ npm: ${npmVersion}`)
      
      this.testResults.environment.runtime = {
        node: nodeVersion,
        npm: npmVersion
      }
    } catch (error) {
      console.log('  ❌ Node.js environment not available')
      this.testResults.failures.push({
        component: 'runtime',
        error: error.message
      })
      throw error
    }
  }

  async checkDependencies() {
    console.log('📦 Verifying installed dependencies...')
    
    try {
      const packagePath = path.join(__dirname, '../../package.json')
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'))
      
      // Check key dependencies
      const keyDeps = ['react', 'vite', 'tailwindcss', 'typescript', 'lucide-react']
      const missingDeps = []
      
      for (const dep of keyDeps) {
        try {
          const version = execSync(`npm list ${dep} --depth=0`, { 
            encoding: 'utf8',
            cwd: path.dirname(packagePath)
          })
          console.log(`  ✅ ${dep}: installed`)
        } catch (error) {
          console.log(`  ❌ ${dep}: missing`)
          missingDeps.push(dep)
        }
      }
      
      if (missingDeps.length > 0) {
        throw new Error(`Missing dependencies: ${missingDeps.join(', ')}`)
      }
      
      this.testResults.environment.dependencies = {
        status: 'complete',
        verified: keyDeps
      }
    } catch (error) {
      console.log('  ❌ Dependencies not properly installed')
      this.testResults.failures.push({
        component: 'dependencies',
        error: error.message,
        solution: 'Run: npm install'
      })
      throw error
    }
  }

  async checkHttpConnection() {
    console.log('🌐 Testing HTTP connection to application...')
    
    try {
      // Use a simpler HTTP check that works in Node.js
      const https = require('http')
      const url = require('url')
      
      const options = url.parse(this.baseUrl)
      
      return new Promise((resolve, reject) => {
        const startTime = Date.now()
        const req = https.get(options, (res) => {
          const endTime = Date.now()
          const responseTime = endTime - startTime
          
          if (res.statusCode === 200) {
            console.log(`  ✅ HTTP connection successful (${responseTime}ms)`)
            this.testResults.environment.http = {
              status: 'connected',
              responseTime: responseTime,
              statusCode: res.statusCode
            }
            resolve()
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`))
          }
        })
        
        req.on('error', (error) => {
          reject(error)
        })
        
        req.setTimeout(5000, () => {
          req.destroy()
          reject(new Error('HTTP request timeout'))
        })
      })
    } catch (error) {
      console.log('  ❌ HTTP connection failed')
      this.testResults.failures.push({
        component: 'http-connection',
        error: error.message
      })
      throw error
    }
  }

  async checkBrowserSupport() {
    console.log('🌍 Checking browser support requirements...')
    
    // This will be enhanced when we have actual Playwright tests
    const requiredFeatures = [
      'localStorage',
      'CSS custom properties',
      'ES2020 modules',
      'Fetch API'
    ]
    
    console.log('  ✅ Modern browser features required:')
    requiredFeatures.forEach(feature => {
      console.log(`    • ${feature}`)
    })
    
    this.testResults.environment.browser = {
      requirements: requiredFeatures,
      status: 'ready'
    }
  }

  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      environment: this.testResults.environment,
      failures: this.testResults.failures,
      status: this.testResults.failures.length === 0 ? 'READY' : 'FAILED'
    }
    
    // Save report
    const reportPath = path.join(__dirname, 'environment-report.json')
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))
    
    console.log('\n📊 Environment Report Generated:')
    console.log(`   Status: ${report.status}`)
    console.log(`   Report: ${reportPath}`)
    
    return report
  }
}

// Execute environment validation if run directly
if (require.main === module) {
  const env = new AuthenticTestEnvironment()
  
  env.validateEnvironment()
    .then(() => {
      const report = env.generateReport()
      if (report.status === 'READY') {
        console.log('\n🚀 Environment ready for authentic testing!')
        process.exit(0)
      } else {
        console.log('\n❌ Environment validation failed')
        process.exit(1)
      }
    })
    .catch((error) => {
      console.error('\n💥 Environment validation error:', error.message)
      env.generateReport()
      process.exit(1)
    })
}

module.exports = AuthenticTestEnvironment