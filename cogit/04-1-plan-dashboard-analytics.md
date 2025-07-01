# 04-1: Dashboard and Analytics Implementation

## Objective
Create a comprehensive dashboard and analytics system that provides insights into application usage, performance metrics, and user activity. This includes real-time monitoring, usage statistics, and administrative controls.

## Prerequisites
- Frontend foundation completed (00-3)
- Core backend APIs implemented (01-1, 02-1, 03-1)
- Chat, Document, and Sequence functionalities working

## Implementation Steps

### 1. Analytics Data Collection
- Implement usage tracking for all major features
- Create event logging system for user interactions
- Add performance monitoring and metrics collection
- Implement error tracking and reporting
- Create data aggregation and storage system

### 2. Dashboard Backend Services
- Create analytics API endpoints
- Implement real-time metrics calculation
- Add data visualization preparation services
- Create reporting and export functionality
- Implement administrative monitoring tools

### 3. Dashboard Frontend Components
- Build metric visualization components
- Create real-time dashboard widgets
- Implement interactive charts and graphs
- Add filtering and time range selection
- Create responsive dashboard layout

### 4. Advanced Analytics Features
- Implement usage pattern analysis
- Create performance optimization suggestions
- Add cost monitoring and budgeting
- Implement user behavior analytics
- Create predictive insights and trends

### 5. Administrative Tools
- Create system health monitoring
- Implement user management interface
- Add configuration management tools
- Create backup and maintenance utilities
- Implement security monitoring dashboard

## Files to Create

### Backend Analytics
1. `backend/models/analytics.py` - Analytics data models
2. `backend/core/analytics_service.py` - Analytics data processing
3. `backend/core/metrics_collector.py` - Real-time metrics collection
4. `backend/core/usage_tracker.py` - User activity tracking
5. `backend/api/analytics.py` - Analytics API endpoints
6. `backend/api/dashboard.py` - Dashboard data endpoints

### Frontend Dashboard
7. `frontend/src/pages/Dashboard.tsx` - Main dashboard page
8. `frontend/src/components/dashboard/MetricsCard.tsx` - Metric display cards
9. `frontend/src/components/dashboard/ChartWidget.tsx` - Chart components
10. `frontend/src/components/dashboard/ActivityFeed.tsx` - Recent activity display
11. `frontend/src/components/dashboard/QuickActions.tsx` - Quick action buttons
12. `frontend/src/components/dashboard/SystemStatus.tsx` - System health indicators

### Analytics Components
13. `frontend/src/components/analytics/UsageChart.tsx` - Usage visualization
14. `frontend/src/components/analytics/PerformanceMetrics.tsx` - Performance dashboard
15. `frontend/src/components/analytics/ErrorTracking.tsx` - Error monitoring
16. `frontend/src/components/analytics/CostMonitoring.tsx` - Cost tracking
17. `frontend/src/hooks/useAnalytics.ts` - Analytics data hooks
18. `frontend/src/services/analyticsService.ts` - Analytics API client

### Data and State Management
19. `frontend/src/store/dashboardStore.ts` - Dashboard state management
20. `frontend/src/store/analyticsStore.ts` - Analytics data store
21. `frontend/src/types/analytics.ts` - Analytics type definitions
22. `frontend/src/utils/chartHelpers.ts` - Chart utility functions

## Key Features Implementation

### 1. Analytics Data Models
```python
# backend/models/analytics.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    CHAT_MESSAGE = "chat_message"
    DOCUMENT_UPLOAD = "document_upload"
    SEQUENCE_EXECUTION = "sequence_execution"
    USER_LOGIN = "user_login"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"

class AnalyticsEvent(BaseModel):
    id: str
    event_type: EventType
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UsageMetrics(BaseModel):
    total_users: int = 0
    active_users_today: int = 0
    active_users_week: int = 0
    total_conversations: int = 0
    total_documents: int = 0
    total_sequences: int = 0
    average_response_time: float = 0.0
    total_api_calls: int = 0
    error_rate: float = 0.0

class PerformanceMetrics(BaseModel):
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = Field(default_factory=dict)
    database_connections: int = 0
    cache_hit_rate: float = 0.0
    average_query_time: float = 0.0

class SystemHealth(BaseModel):
    status: str = "healthy"
    uptime: float = 0.0
    version: str = "1.0.0"
    last_backup: Optional[datetime] = None
    critical_errors: int = 0
    warnings: int = 0
    services_status: Dict[str, str] = Field(default_factory=dict)
```

### 2. Real-time Metrics Collection
```python
# backend/core/metrics_collector.py
import asyncio
import psutil
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class MetricsCollector:
    def __init__(self):
        self.metrics_cache = {}
        self.collection_interval = 30  # seconds
        self.is_collecting = False
    
    async def start_collection(self):
        """Start continuous metrics collection."""
        self.is_collecting = True
        while self.is_collecting:
            try:
                await self.collect_system_metrics()
                await self.collect_application_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)
    
    async def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        metrics = PerformanceMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=(disk.used / disk.total) * 100,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        )
        
        self.metrics_cache['system'] = metrics
        return metrics
    
    async def collect_application_metrics(self) -> UsageMetrics:
        """Collect application-specific metrics."""
        # Get metrics from database
        total_users = await self.get_total_users()
        active_today = await self.get_active_users_today()
        total_conversations = await self.get_total_conversations()
        avg_response_time = await self.get_average_response_time()
        
        metrics = UsageMetrics(
            total_users=total_users,
            active_users_today=active_today,
            total_conversations=total_conversations,
            average_response_time=avg_response_time
        )
        
        self.metrics_cache['usage'] = metrics
        return metrics
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current cached metrics."""
        return {
            "system": self.metrics_cache.get('system'),
            "usage": self.metrics_cache.get('usage'),
            "timestamp": datetime.utcnow()
        }
```

### 3. Analytics Service
```python
# backend/core/analytics_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, event_store, metrics_collector):
        self.event_store = event_store
        self.metrics_collector = metrics_collector
    
    async def track_event(self, event: AnalyticsEvent) -> None:
        """Track a user or system event."""
        await self.event_store.save_event(event)
        
        # Real-time processing for critical events
        if event.event_type == EventType.ERROR_OCCURRED:
            await self.process_error_event(event)
    
    async def get_usage_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day"
    ) -> Dict[str, Any]:
        """Get usage statistics for a date range."""
        
        events = await self.event_store.get_events_by_date_range(start_date, end_date)
        
        # Group events by time period
        time_series = self.group_events_by_time(events, granularity)
        
        # Calculate metrics
        stats = {
            "total_events": len(events),
            "unique_users": len(set(e.user_id for e in events if e.user_id)),
            "event_breakdown": self.count_events_by_type(events),
            "time_series": time_series,
            "peak_usage": self.find_peak_usage(time_series),
            "growth_rate": self.calculate_growth_rate(time_series)
        }
        
        return stats
    
    async def get_performance_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get performance analytics for a date range."""
        
        performance_events = await self.event_store.get_events_by_type(
            EventType.PERFORMANCE_METRIC, start_date, end_date
        )
        
        # Calculate performance metrics
        response_times = [e.metadata.get('response_time', 0) for e in performance_events]
        error_events = await self.event_store.get_events_by_type(
            EventType.ERROR_OCCURRED, start_date, end_date
        )
        
        return {
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "error_count": len(error_events),
            "error_rate": len(error_events) / len(performance_events) if performance_events else 0,
            "performance_trends": self.calculate_performance_trends(performance_events)
        }
    
    async def get_cost_analytics(self) -> Dict[str, Any]:
        """Calculate API usage costs and budgeting."""
        
        # Get API usage events
        api_events = await self.event_store.get_events_by_metadata_filter({
            "api_calls": {"$exists": True}
        })
        
        # Calculate costs based on API usage
        total_tokens = sum(e.metadata.get('tokens_used', 0) for e in api_events)
        estimated_cost = self.calculate_estimated_cost(total_tokens)
        
        return {
            "total_api_calls": len(api_events),
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost,
            "cost_breakdown": self.breakdown_costs_by_service(api_events),
            "monthly_projection": self.project_monthly_cost(api_events)
        }
```

### 4. Dashboard Frontend Components
```tsx
// frontend/src/pages/Dashboard.tsx
import React, { useEffect } from 'react';
import { MetricsCard } from '@/components/dashboard/MetricsCard';
import { ChartWidget } from '@/components/dashboard/ChartWidget';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { SystemStatus } from '@/components/dashboard/SystemStatus';
import { useDashboardStore } from '@/store/dashboardStore';
import { useAnalytics } from '@/hooks/useAnalytics';

export const Dashboard: React.FC = () => {
  const { metrics, loading, refreshMetrics } = useDashboardStore();
  const { trackEvent } = useAnalytics();

  useEffect(() => {
    // Track dashboard view
    trackEvent('dashboard_viewed');
    
    // Load initial metrics
    refreshMetrics();
    
    // Set up auto-refresh
    const interval = setInterval(refreshMetrics, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <SystemStatus />
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricsCard
          title="Active Users"
          value={metrics?.activeUsers || 0}
          change={"+12%"}
          trend="up"
          icon="Users"
        />
        <MetricsCard
          title="Total Conversations"
          value={metrics?.totalConversations || 0}
          change={"+8%"}
          trend="up"
          icon="MessageSquare"
        />
        <MetricsCard
          title="Documents Processed"
          value={metrics?.documentsProcessed || 0}
          change={"+15%"}
          trend="up"
          icon="FileText"
        />
        <MetricsCard
          title="Sequences Executed"
          value={metrics?.sequencesExecuted || 0}
          change={"-2%"}
          trend="down"
          icon="Play"
        />
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartWidget
          title="Usage Over Time"
          type="line"
          data={metrics?.usageTimeSeries}
          height={300}
        />
        <ChartWidget
          title="Feature Usage"
          type="doughnut"
          data={metrics?.featureUsage}
          height={300}
        />
      </div>

      {/* Activity Feed and Additional Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartWidget
            title="Performance Metrics"
            type="bar"
            data={metrics?.performanceMetrics}
            height={400}
          />
        </div>
        <div>
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
};
```

### 5. Interactive Metrics Components
```tsx
// frontend/src/components/dashboard/MetricsCard.tsx
import React from 'react';
import { Card } from '@/components/ui/Card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';

interface MetricsCardProps {
  title: string;
  value: number | string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
  loading?: boolean;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  loading = false
}) => {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  
  const trendColor = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  }[trend];

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        {icon && (
          <div className="p-2 bg-primary/10 rounded-lg">
            {/* Icon component would be rendered here */}
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        {loading ? (
          <div className="h-8 bg-muted animate-pulse rounded" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
        
        {change && (
          <div className={cn("flex items-center text-sm", trendColor)}>
            <TrendIcon className="w-4 h-4 mr-1" />
            {change} from last period
          </div>
        )}
      </div>
    </Card>
  );
};
```

### 6. Chart Widget Component
```tsx
// frontend/src/components/dashboard/ChartWidget.tsx
import React from 'react';
import { Card } from '@/components/ui/Card';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface ChartWidgetProps {
  title: string;
  type: 'line' | 'bar' | 'doughnut';
  data: any;
  height?: number;
  loading?: boolean;
}

export const ChartWidget: React.FC<ChartWidgetProps> = ({
  title,
  type,
  data,
  height = 400,
  loading = false
}) => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: type !== 'doughnut' ? {
      x: {
        display: true,
        grid: {
          display: false,
        },
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    } : undefined,
  };

  const renderChart = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      );
    }

    switch (type) {
      case 'line':
        return <Line data={data} options={chartOptions} />;
      case 'bar':
        return <Bar data={data} options={chartOptions} />;
      case 'doughnut':
        return <Doughnut data={data} options={chartOptions} />;
      default:
        return null;
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div style={{ height }}>
        {renderChart()}
      </div>
    </Card>
  );
};
```

## API Endpoints Implementation

### Analytics Endpoints
```python
# backend/api/analytics.py
from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/usage")
async def get_usage_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    granularity: str = Query("day", regex="^(hour|day|week|month)$")
):
    """Get usage statistics for the specified time range."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    return await analytics_service.get_usage_statistics(start_date, end_date, granularity)

@router.get("/performance")
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get performance metrics for the specified time range."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    return await analytics_service.get_performance_analytics(start_date, end_date)

@router.get("/real-time")
async def get_real_time_metrics():
    """Get current real-time system metrics."""
    return await metrics_collector.get_real_time_metrics()

@router.get("/costs")
async def get_cost_analytics():
    """Get API usage costs and budget information."""
    return await analytics_service.get_cost_analytics()

@router.post("/events")
async def track_event(event: AnalyticsEvent):
    """Track a custom analytics event."""
    await analytics_service.track_event(event)
    return {"message": "Event tracked successfully"}
```

## Success Criteria
- [ ] Dashboard displays real-time metrics correctly
- [ ] Charts and visualizations render properly
- [ ] Analytics data collection works accurately
- [ ] Performance monitoring shows system health
- [ ] Cost tracking provides accurate estimates
- [ ] Dashboard is responsive on mobile devices
- [ ] Real-time updates work via WebSocket
- [ ] Export functionality works for reports
- [ ] Error tracking and alerting function
- [ ] Administrative tools are accessible and functional

## Performance Considerations
- Implement data aggregation to reduce query load
- Use caching for frequently accessed metrics
- Optimize chart rendering for large datasets
- Implement lazy loading for dashboard components
- Use WebSocket for real-time updates to reduce polling

## Estimated Time
12-15 hours

## Next Steps
After completion, proceed to `05-1-plan-integration-testing.md`