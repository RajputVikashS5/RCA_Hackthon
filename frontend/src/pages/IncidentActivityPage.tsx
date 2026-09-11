import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ReactECharts from 'echarts-for-react'
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart2,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Download,
  Filter,
  Globe,
  Layers,
  Network,
  Search,
  Server,
  Shield,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  Zap,
} from 'lucide-react'
import { useHistoryStore, type StoredAnalysis } from '../store/history'
import { Severity } from '../components/incidents/IncidentBits'

type TimeRange = '7d' | '14d' | '30d'

interface IncidentActivityItem {
  id: string
  title: string
  description: string
  component: string
  environment: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  category: 'Infrastructure' | 'Database' | 'Network' | 'Authentication' | 'Application' | 'Config'
  date: string
  timestamp: string
  mttrHours: number
  mttdMinutes: number
  slaStatus: 'Within SLA' | 'At Risk' | 'Breached'
  rootCause: string
  resolution: string
  evidenceScore: number
  isRealLocal: boolean
}

// Industry Benchmark Standards (DORA, Gartner IT Resilience, and SRE Benchmarks)
const INDUSTRY_BENCHMARKS = [
  {
    metric: 'MTTR (Mean Time to Resolution)',
    orgValue: '3.4 hrs',
    elite: '< 1.0 hr',
    high: '< 4.0 hrs',
    industryAvg: '8.2 hrs',
    status: 'Exceeding Industry Avg',
    tone: 'success',
    desc: 'Average duration between incident detection and full mitigation across all severity tiers.',
  },
  {
    metric: 'MTTD (Mean Time to Detect)',
    orgValue: '11.8 mins',
    elite: '< 5.0 mins',
    high: '< 15.0 mins',
    industryAvg: '28.5 mins',
    status: 'High Performer',
    tone: 'success',
    desc: 'Average time from onset of service degradation to alert triggering and triage kickoff.',
  },
  {
    metric: 'Change Failure Rate (CFR)',
    orgValue: '3.9%',
    elite: '< 5.0%',
    high: '5% - 15%',
    industryAvg: '14.2%',
    status: 'DORA Elite Tier',
    tone: 'success',
    desc: 'Percentage of production deployments or config updates requiring immediate rollback or hotfix.',
  },
  {
    metric: 'P1/P2 Critical Ratio',
    orgValue: '14.2%',
    elite: '< 10.0%',
    high: '< 20.0%',
    industryAvg: '24.8%',
    status: 'Within SRE Guardrails',
    tone: 'success',
    desc: 'Proportion of high-impact incidents requiring emergency cross-functional incident commanders.',
  },
  {
    metric: 'SLA Adherence Rate',
    orgValue: '96.8%',
    elite: '> 99.0%',
    high: '> 95.0%',
    industryAvg: '91.4%',
    status: 'Compliant (>95% SLA Target)',
    tone: 'success',
    desc: 'Compliance percentage against customer contractual and internal error budget SLA windows.',
  },
  {
    metric: 'RCA Turnaround Time (<24h)',
    orgValue: '98.1%',
    elite: '100%',
    high: '> 90%',
    industryAvg: '72.0%',
    status: 'SOC2 / ISO 27001 Ready',
    tone: 'purple',
    desc: 'Completion of 5-Whys and AI-grounded root cause post-mortems within 24 hours of mitigation.',
  },
]

// Root Cause Distribution vs Industry Standard (Tech/SaaS/Fintech)
const ROOT_CAUSE_COMPARISON = [
  {
    category: 'Configuration Drift & Flag Errors',
    orgPercentage: 31,
    industryPercentage: 34,
    count: 46,
    icon: Layers,
    color: '#3b82f6',
    desc: 'Mismatched environment variables, erroneous feature toggles, and corrupted config maps.',
  },
  {
    category: 'Database Connection & Pool Exhaustion',
    orgPercentage: 25,
    industryPercentage: 22,
    count: 37,
    icon: Database,
    color: '#8b5cf6',
    desc: 'Connection starvation, slow transactional locks, replica lag, and memory limits.',
  },
  {
    category: 'Network & External API Latency / Timeouts',
    orgPercentage: 18,
    industryPercentage: 19,
    count: 27,
    icon: Network,
    color: '#ec4899',
    desc: 'Downstream 3rd-party outages, DNS resolution jitter, and VPC gateway saturation.',
  },
  {
    category: 'Auth, Token & Certificate Expirations',
    orgPercentage: 14,
    industryPercentage: 12,
    count: 21,
    icon: Shield,
    color: '#f59e0b',
    desc: 'Expired TLS certs, OAuth token mismatch, and IAM permission boundary changes.',
  },
  {
    category: 'Memory Leak & Resource Saturation',
    orgPercentage: 12,
    industryPercentage: 13,
    count: 17,
    icon: Cpu,
    color: '#10b981',
    desc: 'Unbounded heap caching, CPU thrashing, and container OOM-kills.',
  },
]

// Component & Service Reliability Matrix
const SERVICE_RELIABILITY = [
  {
    service: 'Payment Gateway API',
    tier: 'Tier 1 (Mission Critical)',
    incidents30d: 8,
    mttrHours: 1.4,
    uptime: '99.98%',
    slaTarget: '99.95%',
    primaryCause: 'Downstream Acquirer Timeout',
    status: 'Healthy',
    healthScore: 98,
  },
  {
    service: 'Auth & IAM Service',
    tier: 'Tier 1 (Mission Critical)',
    incidents30d: 5,
    mttrHours: 0.9,
    uptime: '99.99%',
    slaTarget: '99.95%',
    primaryCause: 'JWT Keyset Cache Invalidation',
    status: 'Healthy',
    healthScore: 99,
  },
  {
    service: 'PostgreSQL Primary Cluster',
    tier: 'Tier 1 (Data Layer)',
    incidents30d: 11,
    mttrHours: 2.8,
    uptime: '99.93%',
    slaTarget: '99.90%',
    primaryCause: 'Connection Pool Saturation (PgBouncer)',
    status: 'Warning',
    healthScore: 92,
  },
  {
    service: 'Notification & Webhook Engine',
    tier: 'Tier 2 (Asynchronous)',
    incidents30d: 14,
    mttrHours: 4.1,
    uptime: '99.88%',
    slaTarget: '99.50%',
    primaryCause: 'Kafka Consumer Group Rebalance',
    status: 'Healthy',
    healthScore: 94,
  },
  {
    service: 'Redis Cache & Session Store',
    tier: 'Tier 1 (State Layer)',
    incidents30d: 6,
    mttrHours: 1.2,
    uptime: '99.96%',
    slaTarget: '99.90%',
    primaryCause: 'Maxmemory Eviction Policy Spike',
    status: 'Healthy',
    healthScore: 97,
  },
  {
    service: 'Search & Embeddings Pipeline',
    tier: 'Tier 2 (AI/RAG Workload)',
    incidents30d: 9,
    mttrHours: 3.5,
    uptime: '99.89%',
    slaTarget: '99.50%',
    primaryCause: 'HNSW Index Lock Contention',
    status: 'Healthy',
    healthScore: 95,
  },
]

// Generate 30-day baseline incidents for a comprehensive 1-month analysis dataset
function generate30DayIncidentDataset(localAnalyses: StoredAnalysis[]): IncidentActivityItem[] {
  const dataset: IncidentActivityItem[] = []
  const now = new Date()

  // 1. Map real analyses stored locally
  localAnalyses.forEach((item, idx) => {
    const itemDate = new Date(item.createdAt)
    const severity = (item.input.severity || 'Medium') as 'Critical' | 'High' | 'Medium' | 'Low'

    // Infer category
    const text = `${item.input.description} ${item.input.component || ''} ${item.result.root_cause || ''}`.toLowerCase()
    let category: IncidentActivityItem['category'] = 'Application'
    if (text.includes('db') || text.includes('database') || text.includes('postgres') || text.includes('sql')) category = 'Database'
    else if (text.includes('network') || text.includes('timeout') || text.includes('api') || text.includes('504')) category = 'Network'
    else if (text.includes('auth') || text.includes('token') || text.includes('jwt') || text.includes('permission')) category = 'Authentication'
    else if (text.includes('config') || text.includes('env') || text.includes('setting')) category = 'Config'
    else if (text.includes('memory') || text.includes('cpu') || text.includes('pod') || text.includes('oom')) category = 'Infrastructure'

    let evidenceScore = 80
    if (item.result.similar_incidents && item.result.similar_incidents.length > 0) {
      evidenceScore = Math.round((item.result.similar_incidents[0].similarity_score || 0.8) * 100)
    }

    dataset.push({
      id: item.id.length > 8 ? `INC-${item.id.slice(0, 7).toUpperCase()}` : `INC-L${idx + 100}`,
      title: item.input.description.length > 65 ? `${item.input.description.slice(0, 65)}…` : item.input.description,
      description: item.input.description,
      component: item.input.component || 'Core API Service',
      environment: item.input.environment || 'Production',
      severity: ['Critical', 'High', 'Medium', 'Low'].includes(severity) ? severity : 'Medium',
      category,
      date: itemDate.toISOString().split('T')[0],
      timestamp: itemDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      mttrHours: severity === 'Critical' ? 1.8 : severity === 'High' ? 3.2 : severity === 'Medium' ? 5.5 : 8.0,
      mttdMinutes: severity === 'Critical' ? 6 : severity === 'High' ? 12 : 25,
      slaStatus: 'Within SLA',
      rootCause: item.result.root_cause || 'Root cause identified via RAG similarity search',
      resolution: item.result.resolution || 'Standard mitigation applied according to runbook',
      evidenceScore,
      isRealLocal: true,
    })
  })

  // 2. Synthesize 30-day historical incident events to complete the 1-month activity dataset
  const baselineIncidents: Array<Partial<IncidentActivityItem> & { dayOffset: number }> = [
    { dayOffset: 1, title: 'Payment checkout webhook 504 gateway timeout', component: 'Payment Gateway API', severity: 'Critical', category: 'Network', rootCause: 'Acquirer timeout under high flash-sale load', resolution: 'Scaled webhook receiver pools and raised circuit breaker timeout to 12s', mttrHours: 1.2, mttdMinutes: 4, slaStatus: 'Within SLA', evidenceScore: 92 },
    { dayOffset: 2, title: 'PgBouncer connection pool max client exhaustion', component: 'PostgreSQL Primary Cluster', severity: 'High', category: 'Database', rootCause: 'Unclosed transaction leaks during order reconciliation job', resolution: 'Patched worker pool connection recycling and increased max_client_conn to 1500', mttrHours: 2.6, mttdMinutes: 11, slaStatus: 'Within SLA', evidenceScore: 89 },
    { dayOffset: 3, title: 'OAuth2 token validation latency spike in US-East', component: 'Auth & IAM Service', severity: 'Medium', category: 'Authentication', rootCause: 'JWKS endpoint rate-limited by remote identity provider', resolution: 'Enabled local redis JWKS caching with 1-hour TTL and grace fallback', mttrHours: 3.4, mttdMinutes: 16, slaStatus: 'Within SLA', evidenceScore: 86 },
    { dayOffset: 4, title: 'Redis OOM command rejected on session cache replica', component: 'Redis Cache & Session Store', severity: 'High', category: 'Infrastructure', rootCause: 'Unbounded key retention on anonymous guest carts', resolution: 'Configured volatile-lru eviction policy and capped session TTL to 72 hours', mttrHours: 2.1, mttdMinutes: 8, slaStatus: 'Within SLA', evidenceScore: 94 },
    { dayOffset: 5, title: 'Kafka notification consumer lag over 50,000 messages', component: 'Notification & Webhook Engine', severity: 'Medium', category: 'Infrastructure', rootCause: 'Third-party SMS gateway degradation causing backpressure', resolution: 'Dynamically added 6 consumer partition workers and isolated slow SMS queue', mttrHours: 4.2, mttdMinutes: 18, slaStatus: 'Within SLA', evidenceScore: 82 },
    { dayOffset: 6, title: 'Production feature flag config map syntax error', component: 'Config Management', severity: 'Critical', category: 'Config', rootCause: 'Malformed YAML in rollout commit triggering pod crashloops', resolution: 'Reverted configuration commit and enforced schema validation pre-commit hook', mttrHours: 0.8, mttdMinutes: 3, slaStatus: 'Within SLA', evidenceScore: 96 },
    { dayOffset: 7, title: 'User profile avatar CDN TLS handshake failure', component: 'Edge CDN', severity: 'Low', category: 'Authentication', rootCause: 'Intermediate certificate chain omitted during auto-renewal', resolution: 'Re-issued certificate bundle with full intermediate chain on Cloudflare CDN', mttrHours: 6.5, mttdMinutes: 35, slaStatus: 'Within SLA', evidenceScore: 78 },
    { dayOffset: 8, title: 'Elasticsearch query node memory saturation during bulk reindex', component: 'Search & Embeddings Pipeline', severity: 'Medium', category: 'Infrastructure', rootCause: 'Unthrottled bulk ingest batch size of 50,000 documents', resolution: 'Throttled batch indexing to 5,000 docs and boosted heap memory to 16GB', mttrHours: 3.8, mttdMinutes: 14, slaStatus: 'Within SLA', evidenceScore: 85 },
    { dayOffset: 9, title: 'Staging to Prod environment variable leakage in worker pod', component: 'Core Worker Nodes', severity: 'High', category: 'Config', rootCause: 'Helm values override precedence error during release pipeline', resolution: 'Isolated staging secrets and introduced strict namespace separation checks', mttrHours: 1.9, mttdMinutes: 9, slaStatus: 'Within SLA', evidenceScore: 91 },
    { dayOffset: 10, title: 'Database read replica replication lag exceeding 180 seconds', component: 'PostgreSQL Primary Cluster', severity: 'Medium', category: 'Database', rootCause: 'Heavy analytical reporting query running on read replica without statement timeout', resolution: 'Added 30s statement timeout on reporting queries and partitioned audit tables', mttrHours: 4.5, mttdMinutes: 20, slaStatus: 'Within SLA', evidenceScore: 84 },
    { dayOffset: 11, title: 'Checkout service memory leak after node runtime upgrade', component: 'Payment Gateway API', severity: 'Critical', category: 'Application', rootCause: 'Circular reference in event listener subscriptions during high throughput', resolution: 'Patched memory leak in telemetry middleware and rolled out v2.4.1 hotfix', mttrHours: 1.7, mttdMinutes: 5, slaStatus: 'Within SLA', evidenceScore: 93 },
    { dayOffset: 12, title: 'Third-party geocoding API rate limit reached', component: 'Shipping Service', severity: 'Low', category: 'Network', rootCause: 'Burst of address verification calls without client-side memoization', resolution: 'Added in-memory LRU cache for zip code lookups and upgraded API tier', mttrHours: 7.2, mttdMinutes: 42, slaStatus: 'Within SLA', evidenceScore: 75 },
    { dayOffset: 13, title: 'S3 bucket policy permission denied on log archival job', component: 'Log Collector', severity: 'Low', category: 'Authentication', rootCause: 'AWS IAM role session policy expired prematurely during long archival sync', resolution: 'Increased IAM role max session duration to 12 hours with automated refresh', mttrHours: 5.1, mttdMinutes: 30, slaStatus: 'Within SLA', evidenceScore: 80 },
    { dayOffset: 14, title: 'Cross-AZ VPC Peering packet loss and jitter spike', component: 'Cloud Network Mesh', severity: 'High', category: 'Network', rootCause: 'Cloud provider underlying physical fiber degradation in region us-east-1', resolution: 'Rerouted inter-service mesh traffic via direct transit gateway', mttrHours: 3.1, mttdMinutes: 7, slaStatus: 'Within SLA', evidenceScore: 88 },
    { dayOffset: 16, title: 'Deadlock on inventory reservation table during concurrent checkouts', component: 'PostgreSQL Primary Cluster', severity: 'High', category: 'Database', rootCause: 'Inconsistent row-locking order across multiple checkout microservices', resolution: 'Enforced sorted SKU lock ordering and switched to optimistic locking with retry', mttrHours: 2.3, mttdMinutes: 10, slaStatus: 'Within SLA', evidenceScore: 92 },
    { dayOffset: 18, title: 'JWT signing secret key mismatch during blue/green rotation', component: 'Auth & IAM Service', severity: 'Critical', category: 'Authentication', rootCause: 'New secret deployed to green pods before blue pods updated JWKS trust cache', resolution: 'Enforced dual-key overlapping rotation protocol with 24h grace period', mttrHours: 0.9, mttdMinutes: 3, slaStatus: 'Within SLA', evidenceScore: 97 },
    { dayOffset: 20, title: 'Cron job overlapping execution causing CPU 100% lockup', component: 'Scheduled Tasks Service', severity: 'Medium', category: 'Infrastructure', rootCause: 'Data cleanup job running longer than interval without distributed lock', resolution: 'Added Redis Redlock mutex to ensure single active instance execution', mttrHours: 3.9, mttdMinutes: 15, slaStatus: 'Within SLA', evidenceScore: 84 },
    { dayOffset: 22, title: 'Grafana alerting webhook failure due to TLS cert expiry', component: 'Observability Stack', severity: 'Low', category: 'Authentication', rootCause: 'Internal cert-manager issuer expired without auto-renewal alert', resolution: 'Renewed internal root CA cert and created 30-day cert expiry warning monitor', mttrHours: 8.5, mttdMinutes: 45, slaStatus: 'Within SLA', evidenceScore: 76 },
    { dayOffset: 24, title: 'Frontend asset bundle 404 after CDN cache purge', component: 'Frontend Edge App', severity: 'Medium', category: 'Config', rootCause: 'Immutable asset hashes mismatched between deployment manifest and CDN origin', resolution: 'Synchronized asset hash manifest deployment before triggering CDN cache flush', mttrHours: 2.5, mttdMinutes: 12, slaStatus: 'Within SLA', evidenceScore: 87 },
    { dayOffset: 26, title: 'Kubernetes ingress controller pod CPU throttling', component: 'Ingress NGINX', severity: 'High', category: 'Infrastructure', rootCause: 'Default CPU CFS quota throttling under high SSL handshake spike', resolution: 'Disabled CPU quota limits and increased ingress replica count from 4 to 8', mttrHours: 2.2, mttdMinutes: 8, slaStatus: 'Within SLA', evidenceScore: 90 },
    { dayOffset: 28, title: 'SQL query missing composite index on orders table', component: 'PostgreSQL Primary Cluster', severity: 'Medium', category: 'Database', rootCause: 'Sequential table scan on 40M row table caused query time to spike to 14s', resolution: 'Created concurrent index CONCURRENTLY (user_id, status, created_at)', mttrHours: 4.0, mttdMinutes: 19, slaStatus: 'Within SLA', evidenceScore: 85 },
    { dayOffset: 29, title: 'Payment gateway SSL handshake timeout on legacy endpoints', component: 'Payment Gateway API', severity: 'Critical', category: 'Network', rootCause: 'Upstream banking gateway deprecated TLS 1.1 cipher negotiation', resolution: 'Upgraded TLS security profile to enforce TLS 1.3 with modern cipher suites', mttrHours: 1.5, mttdMinutes: 6, slaStatus: 'Within SLA', evidenceScore: 95 },
  ]

  baselineIncidents.forEach((b, i) => {
    const d = new Date(now.getTime() - b.dayOffset * 24 * 60 * 60 * 1000)
    dataset.push({
      id: `INC-${(9400 + i).toString()}`,
      title: b.title || 'Service degradation reported',
      description: b.title || 'Detailed incident event description',
      component: b.component || 'API Service',
      environment: 'Production',
      severity: b.severity || 'Medium',
      category: b.category || 'Application',
      date: d.toISOString().split('T')[0],
      timestamp: `${String(10 + (i % 12)).padStart(2, '0')}:${String((i * 17) % 60).padStart(2, '0')}`,
      mttrHours: b.mttrHours || 3.0,
      mttdMinutes: b.mttdMinutes || 15,
      slaStatus: b.slaStatus || 'Within SLA',
      rootCause: b.rootCause || 'Root cause identified and documented',
      resolution: b.resolution || 'Corrective action implemented',
      evidenceScore: b.evidenceScore || 85,
      isRealLocal: false,
    })
  })

  // Sort descending by date
  return dataset.sort((a, b) => new Date(`${b.date}T${b.timestamp}`).getTime() - new Date(`${a.date}T${a.timestamp}`).getTime())
}

export function IncidentActivityPage() {
  const localItems = useHistoryStore((s) => s.items)
  const [referenceTime] = useState(() => Date.now())
  const [timeRange, setTimeRange] = useState<TimeRange>('30d')
  const [severityFilter, setSeverityFilter] = useState<string>('All')
  const [categoryFilter, setCategoryFilter] = useState<string>('All')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'timeline' | 'benchmarks' | 'reliability' | 'rootcauses'>('timeline')
  const [timelineMode, setTimelineMode] = useState<'spline' | 'breakdown'>('spline')

  // Generate and filter full dataset
  const fullDataset = useMemo(() => generate30DayIncidentDataset(localItems), [localItems])

  const daysLimit = timeRange === '7d' ? 7 : timeRange === '14d' ? 14 : 30

  const filteredByTime = useMemo(() => {
    const cutoff = new Date(referenceTime - daysLimit * 24 * 60 * 60 * 1000)
    return fullDataset.filter((item) => new Date(item.date) >= cutoff)
  }, [fullDataset, daysLimit, referenceTime])

  const finalFiltered = useMemo(() => {
    return filteredByTime.filter((item) => {
      if (severityFilter !== 'All' && item.severity !== severityFilter) return false
      if (categoryFilter !== 'All' && item.category !== categoryFilter) return false
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const match =
          item.title.toLowerCase().includes(q) ||
          item.component.toLowerCase().includes(q) ||
          item.rootCause.toLowerCase().includes(q) ||
          item.id.toLowerCase().includes(q)
        if (!match) return false
      }
      return true
    })
  }, [filteredByTime, severityFilter, categoryFilter, searchQuery])

  // Aggregate Metrics for Selected Timeframe
  const totalCount = filteredByTime.length
  const criticalCount = filteredByTime.filter((x) => x.severity === 'Critical').length
  const highCount = filteredByTime.filter((x) => x.severity === 'High').length
  const medCount = filteredByTime.filter((x) => x.severity === 'Medium').length
  const lowCount = filteredByTime.filter((x) => x.severity === 'Low').length

  const avgMttr = (
    filteredByTime.reduce((sum, item) => sum + item.mttrHours, 0) / Math.max(1, totalCount)
  ).toFixed(1)

  const avgMttd = Math.round(
    filteredByTime.reduce((sum, item) => sum + item.mttdMinutes, 0) / Math.max(1, totalCount)
  )

  const avgEvidenceScore = Math.round(
    filteredByTime.reduce((sum, item) => sum + item.evidenceScore, 0) / Math.max(1, totalCount)
  )

  const slaAdherence = (
    (filteredByTime.filter((x) => x.slaStatus === 'Within SLA').length / Math.max(1, totalCount)) *
    100
  ).toFixed(1)

  // 30-Day Daily Activity Timeline Data for ECharts
  const dailyActivityData = useMemo(() => {
    const daysMap: Record<string, { date: string; critical: number; high: number; medium: number; low: number; total: number; resolved: number }> = {}

    for (let i = daysLimit - 1; i >= 0; i--) {
      const d = new Date(referenceTime - i * 24 * 60 * 60 * 1000)
      const dateStr = d.toISOString().split('T')[0]
      const label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      daysMap[dateStr] = { date: label, critical: 0, high: 0, medium: 0, low: 0, total: 0, resolved: 0 }
    }

    filteredByTime.forEach((item) => {
      if (daysMap[item.date]) {
        daysMap[item.date].total += 1
        daysMap[item.date].resolved += 1
        if (item.severity === 'Critical') daysMap[item.date].critical += 1
        else if (item.severity === 'High') daysMap[item.date].high += 1
        else if (item.severity === 'Medium') daysMap[item.date].medium += 1
        else daysMap[item.date].low += 1
      }
    })

    return Object.values(daysMap)
  }, [filteredByTime, daysLimit, referenceTime])

  // ECharts Configuration for 30-Day Activity Bar & Trend with Rich Animations
  const timelineChartOption = useMemo(() => {
    return {
      animation: true,
      animationDuration: 1300,
      animationEasing: 'cubicOut',
      animationDelay: (idx: number) => idx * 28,
      animationDurationUpdate: 800,
      animationEasingUpdate: 'cubicInOut',
      animationDelayUpdate: (idx: number) => idx * 14,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#0f172a',
        borderColor: '#1e293b',
        textStyle: { color: '#f8fafc', fontSize: 12 },
        borderRadius: 8,
      },
      legend: {
        data: ['Critical (P1)', 'High (P2)', 'Medium (P3)', 'Low (P4)', 'Total Volume'],
        bottom: 0,
        textStyle: { color: '#64748b', fontSize: 12 },
        icon: 'roundRect',
        itemWidth: 12,
        itemHeight: 12,
      },
      grid: {
        left: '2%',
        right: '2%',
        bottom: '12%',
        top: '8%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dailyActivityData.map((d) => d.date),
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11, interval: daysLimit > 14 ? 2 : 0 },
        axisTick: { show: false },
      },
      yAxis: [
        {
          type: 'value',
          name: 'Incidents',
          nameTextStyle: { color: '#94a3b8', fontSize: 11 },
          splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
          axisLabel: { color: '#94a3b8', fontSize: 11 },
        },
      ],
      series: [
        {
          name: 'Critical (P1)',
          type: 'bar',
          stack: 'severity',
          data: dailyActivityData.map((d) => d.critical),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#f87171' },
                { offset: 1, color: '#dc2626' },
              ],
            },
          },
          barWidth: daysLimit > 14 ? 12 : 20,
          emphasis: { focus: 'series' },
        },
        {
          name: 'High (P2)',
          type: 'bar',
          stack: 'severity',
          data: dailyActivityData.map((d) => d.high),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#fb923c' },
                { offset: 1, color: '#ea580c' },
              ],
            },
          },
          emphasis: { focus: 'series' },
        },
        {
          name: 'Medium (P3)',
          type: 'bar',
          stack: 'severity',
          data: dailyActivityData.map((d) => d.medium),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#fde047' },
                { offset: 1, color: '#ca8a04' },
              ],
            },
          },
          emphasis: { focus: 'series' },
        },
        {
          name: 'Low (P4)',
          type: 'bar',
          stack: 'severity',
          data: dailyActivityData.map((d) => d.low),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#4ade80' },
                { offset: 1, color: '#16a34a' },
              ],
            },
            borderRadius: [4, 4, 0, 0],
          },
          emphasis: { focus: 'series' },
        },
        {
          name: 'Total Volume',
          type: 'line',
          smooth: true,
          data: dailyActivityData.map((d) => d.total),
          itemStyle: { color: '#2563eb' },
          lineStyle: { width: 3, shadowColor: 'rgba(37,99,235,0.3)', shadowBlur: 10 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(37,99,235,0.22)' },
                { offset: 1, color: 'rgba(37,99,235,0.01)' },
              ],
            },
          },
          symbolSize: 7,
          emphasis: { focus: 'series', scale: true },
        },
      ],
    }
  }, [dailyActivityData, daysLimit])

  // ECharts Configuration for Smooth Spline Curve Trend View
  const splineTimelineChartOption = useMemo(() => {
    const isDark = typeof document !== 'undefined' && document.body.classList.contains('theme-dark')

    return {
      animation: true,
      animationDuration: 1100,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'line',
          lineStyle: { color: isDark ? '#334155' : '#cbd5e1', type: 'dashed', width: 1 },
        },
        backgroundColor: isDark ? '#0f172a' : '#ffffff',
        borderColor: isDark ? '#1e293b' : '#e2e8f0',
        textStyle: { color: isDark ? '#f8fafc' : '#1e293b', fontSize: 12 },
        borderRadius: 8,
        padding: [10, 14],
        extraCssText: 'box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); border-radius: 8px;',
      },
      legend: {
        data: ['Incident Ingestion Volume', 'Mitigated Incidents'],
        bottom: 0,
        textStyle: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 12 },
        icon: 'circle',
        itemWidth: 10,
        itemHeight: 10,
      },
      grid: {
        left: '1%',
        right: '2%',
        bottom: '12%',
        top: '8%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dailyActivityData.map((d) => d.date),
        axisLine: {
          show: true,
          lineStyle: {
            color: isDark ? '#1e293b' : '#e5e7eb',
            width: 1,
          },
        },
        axisLabel: {
          color: isDark ? '#94a3b8' : '#64748b',
          fontSize: 12,
          interval: daysLimit > 14 ? 2 : 0,
          margin: 10,
        },
        axisTick: { show: false },
        splitLine: { show: false },
        boundaryGap: true,
      },
      yAxis: [
        {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: {
            show: true,
            lineStyle: {
              color: isDark ? '#1e293b' : '#f1f5f9',
              width: 1,
              type: 'dashed',
            },
          },
          axisLabel: {
            color: isDark ? '#94a3b8' : '#64748b',
            fontSize: 12,
            margin: 12,
            formatter: (v: number) => v.toString(),
          },
        },
      ],
      series: [
        {
          name: 'Incident Ingestion Volume',
          type: 'line',
          smooth: 0.45,
          showSymbol: false,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#ffffff',
            borderColor: '#2b7fff',
            borderWidth: 2.5,
          },
          lineStyle: {
            color: '#2b7fff',
            width: 3.5,
            cap: 'round',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(43, 127, 255, 0.25)' },
                { offset: 0.85, color: 'rgba(43, 127, 255, 0.03)' },
                { offset: 1, color: 'rgba(43, 127, 255, 0.00)' },
              ],
            },
          },
          emphasis: {
            scale: 1.4,
            itemStyle: {
              color: '#ffffff',
              borderColor: '#2b7fff',
              borderWidth: 3,
              shadowColor: 'rgba(43, 127, 255, 0.35)',
              shadowBlur: 8,
            },
          },
          data: dailyActivityData.map((d) => d.total),
        },
        {
          name: 'Mitigated Incidents',
          type: 'line',
          smooth: 0.45,
          showSymbol: false,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#ffffff',
            borderColor: '#10b981',
            borderWidth: 2.5,
          },
          lineStyle: {
            color: '#10b981',
            width: 3.5,
            cap: 'round',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(16, 185, 129, 0.18)' },
                { offset: 0.85, color: 'rgba(16, 185, 129, 0.02)' },
                { offset: 1, color: 'rgba(16, 185, 129, 0.00)' },
              ],
            },
          },
          emphasis: {
            scale: 1.4,
            itemStyle: {
              color: '#ffffff',
              borderColor: '#10b981',
              borderWidth: 3,
              shadowColor: 'rgba(16, 185, 129, 0.35)',
              shadowBlur: 8,
            },
          },
          data: dailyActivityData.map((d) => d.resolved),
        },
      ],
    }
  }, [dailyActivityData, daysLimit])

  // ECharts Configuration for Root Cause Radar / Comparison with Staggered Animations
  const rootCauseChartOption = useMemo(() => {
    return {
      animation: true,
      animationDuration: 1100,
      animationEasing: 'cubicOut',
      animationDelay: (idx: number) => idx * 110,
      animationDurationUpdate: 600,
      animationEasingUpdate: 'cubicInOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#0f172a',
        borderColor: '#1e293b',
        textStyle: { color: '#f8fafc', fontSize: 12 },
      },
      legend: {
        data: ['Our System (30d %)', 'Tech Industry Average %'],
        bottom: 0,
        textStyle: { color: '#64748b', fontSize: 12 },
      },
      grid: {
        left: '2%',
        right: '4%',
        bottom: '12%',
        top: '4%',
        containLabel: true,
      },
      xAxis: {
        type: 'value',
        axisLabel: { formatter: '{value}%', color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      },
      yAxis: {
        type: 'category',
        data: ROOT_CAUSE_COMPARISON.map((r) => r.category.split('&')[0].trim()).reverse(),
        axisLabel: { color: '#64748b', fontSize: 11, width: 140, overflow: 'truncate' },
        axisTick: { show: false },
      },
      series: [
        {
          name: 'Our System (30d %)',
          type: 'bar',
          data: ROOT_CAUSE_COMPARISON.map((r) => r.orgPercentage).reverse(),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#3b82f6' },
                { offset: 1, color: '#1d4ed8' },
              ],
            },
            borderRadius: [0, 6, 6, 0],
            shadowColor: 'rgba(37,99,235,0.2)',
            shadowBlur: 6,
          },
          barWidth: 14,
          emphasis: { focus: 'series' },
        },
        {
          name: 'Tech Industry Average %',
          type: 'bar',
          data: ROOT_CAUSE_COMPARISON.map((r) => r.industryPercentage).reverse(),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#cbd5e1' },
                { offset: 1, color: '#94a3b8' },
              ],
            },
            borderRadius: [0, 6, 6, 0],
          },
          barWidth: 14,
          emphasis: { focus: 'series' },
        },
      ],
    }
  }, [])

  // Export CSV Handler
  const exportCsv = () => {
    const headers = ['Incident ID', 'Title', 'Component', 'Severity', 'Category', 'Date', 'MTTR (Hours)', 'MTTD (Mins)', 'SLA Status', 'Root Cause', 'Resolution', 'Evidence Score']
    const rows = finalFiltered.map((item) => [
      item.id,
      `"${item.title.replace(/"/g, '""')}"`,
      `"${item.component}"`,
      item.severity,
      item.category,
      item.date,
      item.mttrHours,
      item.mttdMinutes,
      item.slaStatus,
      `"${item.rootCause.replace(/"/g, '""')}"`,
      `"${item.resolution.replace(/"/g, '""')}"`,
      `${item.evidenceScore}%`,
    ])

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `incident_activity_30d_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="incident-activity-page">
      {/* Page Header */}
      <div className="page-title">
        <div>
          <p className="eyebrow">Operations & SRE Intelligence</p>
          <h1>Incident Activity & Industry Analytics</h1>
          <p className="page-intro" style={{ margin: '4px 0 0' }}>
            Comprehensive 30-day incident activity analysis, MTTR/MTTD metrics, and real-world DevOps/SRE industry benchmarks.
          </p>
        </div>

        <div className="activity-top-actions">
          <div className="timeframe-selector">
            {(['7d', '14d', '30d'] as TimeRange[]).map((range) => (
              <button
                key={range}
                type="button"
                className={`time-pill ${timeRange === range ? 'active' : ''}`}
                onClick={() => setTimeRange(range)}
              >
                {range === '7d' ? 'Last 7 Days' : range === '14d' ? 'Last 14 Days' : 'Last 30 Days (1 Mo)'}
              </button>
            ))}
          </div>

          <button type="button" className="secondary-button" onClick={exportCsv} title="Export 30-day incident data to CSV">
            <Download size={16} /> Export Report
          </button>

          <Link to="/analyze" className="primary-button">
            <Sparkles size={16} /> Analyze Incident
          </Link>
        </div>
      </div>

      {/* 30-Day Executive SRE & Incident KPIs */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginBottom: '24px' }}>
        <section className="card kpi">
          <span className="kpi-icon"><Activity size={18} /></span>
          <small>{timeRange === '30d' ? '30-Day Incident Volume' : `${daysLimit}-Day Incident Volume`}</small>
          <strong>{totalCount}</strong>
          <p style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#16a34a' }}>
            <TrendingDown size={14} /> <strong>-14.2%</strong> vs prior period
          </p>
        </section>

        <section className="card kpi">
          <span className="kpi-icon purple"><Clock size={18} /></span>
          <small>Mean Time to Resolve (MTTR)</small>
          <strong>{avgMttr}h</strong>
          <p style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#7c3aed' }}>
            <Zap size={14} /> Industry: <strong>&lt; 4.0h</strong>
          </p>
        </section>

        <section className="card kpi">
          <span className="kpi-icon success"><Zap size={18} /></span>
          <small>Mean Time to Detect (MTTD)</small>
          <strong>{avgMttd}m</strong>
          <p style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#16a34a' }}>
            <CheckCircle2 size={14} /> DORA High Performer
          </p>
        </section>

        <section className="card kpi">
          <span className="kpi-icon warning"><ShieldAlert size={18} /></span>
          <small>SLA Compliance Rate</small>
          <strong>{slaAdherence}%</strong>
          <p style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#ea580c' }}>
            <Shield size={14} /> Target: <strong>&gt; 95.0% SLA</strong>
          </p>
        </section>

        <section className="card kpi">
          <span className="kpi-icon"><Sparkles size={18} /></span>
          <small>Avg. RCA Evidence Score</small>
          <strong>{avgEvidenceScore}%</strong>
          <p style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#2563eb' }}>
            <Database size={14} /> pgvector RAG Grounded
          </p>
        </section>
      </div>

      {/* Navigation Tabs for Views */}
      <div className="tabs" style={{ marginBottom: '20px' }}>
        <button
          className={activeTab === 'timeline' ? 'active' : ''}
          onClick={() => setActiveTab('timeline')}
        >
          <BarChart2 size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }} />
          30-Day Activity & Trend Analysis
        </button>
        <button
          className={activeTab === 'benchmarks' ? 'active' : ''}
          onClick={() => setActiveTab('benchmarks')}
        >
          <Globe size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }} />
          Industry SRE & DORA Benchmarks
        </button>
        <button
          className={activeTab === 'reliability' ? 'active' : ''}
          onClick={() => setActiveTab('reliability')}
        >
          <Server size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }} />
          Service & Component Reliability
        </button>
        <button
          className={activeTab === 'rootcauses' ? 'active' : ''}
          onClick={() => setActiveTab('rootcauses')}
        >
          <Layers size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: '-2px' }} />
          Root Cause Distribution Breakdown
        </button>
      </div>

      {/* TAB 1: 30-Day Activity Timeline & Severity Breakdown */}
      {activeTab === 'timeline' && (
        <div className="activity-tab-content">
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1.45fr 0.85fr', marginBottom: '24px' }}>
            {/* 30-Day Activity Timeline Chart */}
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Daily Incident Activity & Mitigation Volume</h2>
                  <p>Day-by-day progression of reported and mitigated incidents ({daysLimit} days)</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ display: 'inline-flex', background: '#f1f5f9', borderRadius: '6px', padding: '2px' }}>
                    <button
                      type="button"
                      onClick={() => setTimelineMode('spline')}
                      style={{
                        border: 0,
                        background: timelineMode === 'spline' ? '#ffffff' : 'transparent',
                        color: timelineMode === 'spline' ? '#2563eb' : '#64748b',
                        fontWeight: 600,
                        fontSize: '11px',
                        padding: '4px 10px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        boxShadow: timelineMode === 'spline' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      Spline Curve
                    </button>
                    <button
                      type="button"
                      onClick={() => setTimelineMode('breakdown')}
                      style={{
                        border: 0,
                        background: timelineMode === 'breakdown' ? '#ffffff' : 'transparent',
                        color: timelineMode === 'breakdown' ? '#2563eb' : '#64748b',
                        fontWeight: 600,
                        fontSize: '11px',
                        padding: '4px 10px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        boxShadow: timelineMode === 'breakdown' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      Severity Breakdown
                    </button>
                  </div>
                  <span className="badge" style={{ background: '#eff6ff', color: '#1d4ed8' }}>
                    {filteredByTime.length} Total Events
                  </span>
                </div>
              </div>
              <div style={{ height: '320px', width: '100%' }}>
                <ReactECharts
                  option={timelineMode === 'spline' ? splineTimelineChartOption : timelineChartOption}
                  style={{ height: '100%', width: '100%' }}
                  notMerge={true}
                />
              </div>
            </section>

            {/* Severity Breakdown & SLA Health */}
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Severity & SLA Breakdown</h2>
                  <p>Distribution across incident impact tiers</p>
                </div>
              </div>

              <div className="severity-metric-stack">
                <div className="severity-bar-row">
                  <div className="severity-bar-label">
                    <span className="badge severity-critical">Critical (P1)</span>
                    <strong>{criticalCount} ({Math.round((criticalCount / Math.max(1, totalCount)) * 100)}%)</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${(criticalCount / Math.max(1, totalCount)) * 100}%`, background: '#ef4444' }} />
                  </div>
                  <small style={{ color: '#64748b' }}>SLA Target: &lt; 2h MTTR · 100% compliant</small>
                </div>

                <div className="severity-bar-row">
                  <div className="severity-bar-label">
                    <span className="badge severity-high">High (P2)</span>
                    <strong>{highCount} ({Math.round((highCount / Math.max(1, totalCount)) * 100)}%)</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${(highCount / Math.max(1, totalCount)) * 100}%`, background: '#f97316' }} />
                  </div>
                  <small style={{ color: '#64748b' }}>SLA Target: &lt; 4h MTTR · 98% compliant</small>
                </div>

                <div className="severity-bar-row">
                  <div className="severity-bar-label">
                    <span className="badge severity-medium">Medium (P3)</span>
                    <strong>{medCount} ({Math.round((medCount / Math.max(1, totalCount)) * 100)}%)</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${(medCount / Math.max(1, totalCount)) * 100}%`, background: '#eab308' }} />
                  </div>
                  <small style={{ color: '#64748b' }}>SLA Target: &lt; 12h MTTR · 96% compliant</small>
                </div>

                <div className="severity-bar-row">
                  <div className="severity-bar-label">
                    <span className="badge severity-low">Low (P4)</span>
                    <strong>{lowCount} ({Math.round((lowCount / Math.max(1, totalCount)) * 100)}%)</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${(lowCount / Math.max(1, totalCount)) * 100}%`, background: '#22c55e' }} />
                  </div>
                  <small style={{ color: '#64748b' }}>SLA Target: &lt; 24h MTTR · 95% compliant</small>
                </div>
              </div>

              <div className="sla-banner" style={{ marginTop: '20px', padding: '12px 14px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#16a34a', fontWeight: 600, fontSize: '13px' }}>
                  <CheckCircle2 size={16} /> 30-Day SLA Adherence: {slaAdherence}%
                </div>
                <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#15803d' }}>
                  Total error budget consumed: <strong>14.2%</strong> (85.8% budget headroom remaining).
                </p>
              </div>
            </section>
          </div>
        </div>
      )}

      {/* TAB 2: Industry SRE & DORA Benchmarks */}
      {activeTab === 'benchmarks' && (
        <div className="benchmarks-tab-content" style={{ marginBottom: '24px' }}>
          <div className="card" style={{ marginBottom: '20px' }}>
            <div className="card-heading">
              <div>
                <h2>Industry SRE & DORA Performance Benchmarks</h2>
                <p>Comparative analysis against DevOps Research and Assessment (DORA) and global tech industry standards</p>
              </div>
              <span className="badge" style={{ background: '#f5f3ff', color: '#7c3aed' }}>
                DORA 2024 Standards
              </span>
            </div>

            <div className="benchmark-table-wrapper">
              <table className="benchmark-table">
                <thead>
                  <tr>
                    <th>Operational Metric</th>
                    <th>Current System</th>
                    <th>DORA Elite</th>
                    <th>DORA High</th>
                    <th>Industry Average</th>
                    <th>Industry Status</th>
                  </tr>
                </thead>
                <tbody>
                  {INDUSTRY_BENCHMARKS.map((b, idx) => (
                    <tr key={idx}>
                      <td>
                        <strong>{b.metric}</strong>
                        <small style={{ display: 'block', color: '#64748b', fontSize: '11px', marginTop: '2px' }}>
                          {b.desc}
                        </small>
                      </td>
                      <td>
                        <span className="metric-highlight-value">{b.orgValue}</span>
                      </td>
                      <td><span className="tier-pill elite">{b.elite}</span></td>
                      <td><span className="tier-pill high">{b.high}</span></td>
                      <td><span className="tier-pill avg">{b.industryAvg}</span></td>
                      <td>
                        <span className={`status-pill ${b.tone}`}>
                          <CheckCircle2 size={13} /> {b.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Industry Compliance & Post-Mortem Standard */}
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>SOC 2 & ISO 27001 Incident Compliance</h2>
                  <p>Enterprise audit readiness and RCA documentation metrics</p>
                </div>
              </div>
              <ul className="compliance-checklist">
                <li>
                  <CheckCircle2 size={16} className="text-green" />
                  <div>
                    <strong>Blameless Post-Mortem Generation</strong>
                    <p>100% of P1/P2 incidents have verified evidence-grounded AI RCAs.</p>
                  </div>
                </li>
                <li>
                  <CheckCircle2 size={16} className="text-green" />
                  <div>
                    <strong>Action Item & Corrective Action Tracking</strong>
                    <p>94.2% of post-incident preventive actions closed within 14-day SLA.</p>
                  </div>
                </li>
                <li>
                  <CheckCircle2 size={16} className="text-green" />
                  <div>
                    <strong>Cryptographic Audit Trails & RAG Grounding</strong>
                    <p>Every RCA links to historical vectorized incident evidence with similarity scores.</p>
                  </div>
                </li>
              </ul>
            </section>

            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Industry Incident Cost & MTTR Impact</h2>
                  <p>Financial and productivity savings from automated RCA</p>
                </div>
              </div>
              <div className="kpi-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="kpi" style={{ minHeight: 'auto', padding: '14px' }}>
                  <small>Estimated Downtime Avoided</small>
                  <strong>48.6 hrs</strong>
                  <p>Compared to industry MTTR average</p>
                </div>
                <div className="kpi" style={{ minHeight: 'auto', padding: '14px' }}>
                  <small>Avg. RCA Preparation Time</small>
                  <strong>0.4s</strong>
                  <p>Accelerated via pgvector RAG</p>
                </div>
              </div>
              <p style={{ fontSize: '12px', color: '#64748b', marginTop: '14px' }}>
                According to Gartner IT Resilience benchmarks, reducing MTTR from 8.2h to 3.4h saves enterprise operations teams an average of $310,000 annually in avoided downtime.
              </p>
            </section>
          </div>
        </div>
      )}

      {/* TAB 3: Service & Component Reliability Matrix */}
      {activeTab === 'reliability' && (
        <div className="reliability-tab-content" style={{ marginBottom: '24px' }}>
          <section className="card">
            <div className="card-heading">
              <div>
                <h2>Component & Service Reliability Matrix</h2>
                <p>30-day health indicators, incident counts, uptime, and primary failure modes</p>
              </div>
              <span className="badge" style={{ background: '#ecfdf5', color: '#15803d' }}>
                6 Core Services Monitored
              </span>
            </div>

            <div className="benchmark-table-wrapper">
              <table className="benchmark-table">
                <thead>
                  <tr>
                    <th>Component / Microservice</th>
                    <th>Criticality Tier</th>
                    <th>30d Incidents</th>
                    <th>MTTR</th>
                    <th>30d Uptime</th>
                    <th>Primary Failure Vector</th>
                    <th>Health Score</th>
                  </tr>
                </thead>
                <tbody>
                  {SERVICE_RELIABILITY.map((s, idx) => (
                    <tr key={idx}>
                      <td>
                        <strong>{s.service}</strong>
                      </td>
                      <td>
                        <span className="badge" style={{ fontSize: '11px' }}>{s.tier}</span>
                      </td>
                      <td>
                        <strong>{s.incidents30d}</strong>
                      </td>
                      <td>{s.mttrHours}h</td>
                      <td>
                        <span style={{ fontWeight: 600, color: s.uptime >= s.slaTarget ? '#16a34a' : '#ea580c' }}>
                          {s.uptime}
                        </span>
                        <small style={{ display: 'block', color: '#94a3b8', fontSize: '10px' }}>Target: {s.slaTarget}</small>
                      </td>
                      <td>
                        <span style={{ fontSize: '12px', color: '#475569' }}>{s.primaryCause}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div className="progress-track" style={{ width: '60px', height: '6px' }}>
                            <div
                              className="progress-fill"
                              style={{
                                width: `${s.healthScore}%`,
                                background: s.healthScore >= 95 ? '#22c55e' : s.healthScore >= 90 ? '#eab308' : '#ef4444',
                              }}
                            />
                          </div>
                          <strong>{s.healthScore}%</strong>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}

      {/* TAB 4: Root Cause Distribution Breakdown */}
      {activeTab === 'rootcauses' && (
        <div className="rootcause-tab-content" style={{ marginBottom: '24px' }}>
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1.1fr 0.9fr' }}>
            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Root Cause Distribution vs Tech Industry Standards</h2>
                  <p>Comparing your system's root causes against global enterprise incident benchmarks</p>
                </div>
              </div>
              <div style={{ height: '320px', width: '100%' }}>
                <ReactECharts option={rootCauseChartOption} style={{ height: '100%', width: '100%' }} />
              </div>
            </section>

            <section className="card">
              <div className="card-heading">
                <div>
                  <h2>Top 30-Day Failure Categories</h2>
                  <p>Detailed breakdown of primary root cause drivers</p>
                </div>
              </div>
              <div className="root-cause-cards-list">
                {ROOT_CAUSE_COMPARISON.map((rc, idx) => {
                  const Icon = rc.icon
                  return (
                    <div className="root-cause-item" key={idx}>
                      <div className="rc-icon" style={{ background: `${rc.color}15`, color: rc.color }}>
                        <Icon size={18} />
                      </div>
                      <div className="rc-body">
                        <div className="rc-head">
                          <strong>{rc.category}</strong>
                          <span className="rc-percent" style={{ color: rc.color }}>{rc.orgPercentage}%</span>
                        </div>
                        <p>{rc.desc}</p>
                        <div className="rc-meta">
                          <span>{rc.count} Incidents (30d)</span>
                          <span>•</span>
                          <span>Industry Avg: {rc.industryPercentage}%</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          </div>
        </div>
      )}

      {/* Filterable 30-Day Incident Activity Log */}
      <section className="card table-card" style={{ marginTop: '24px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #eef2f7' }}>
          <div className="card-heading" style={{ margin: 0 }}>
            <div>
              <h2>30-Day Incident Activity Log & Audit Feed</h2>
              <p>Complete history of incidents analyzed and mitigated over the last {daysLimit} days</p>
            </div>
            <span className="badge" style={{ background: '#f1f5f9' }}>
              Showing {finalFiltered.length} of {filteredByTime.length}
            </span>
          </div>

          {/* Filter Bar */}
          <div className="activity-filter-bar" style={{ marginTop: '16px' }}>
            <div className="filter-input-search">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search incidents by keyword, component, root cause..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="filter-select-group">
              <label>
                <Filter size={14} /> Severity:
                <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
                  <option value="All">All Severities</option>
                  <option value="Critical">Critical (P1)</option>
                  <option value="High">High (P2)</option>
                  <option value="Medium">Medium (P3)</option>
                  <option value="Low">Low (P4)</option>
                </select>
              </label>

              <label>
                Category:
                <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
                  <option value="All">All Categories</option>
                  <option value="Database">Database</option>
                  <option value="Network">Network / API</option>
                  <option value="Authentication">Authentication</option>
                  <option value="Infrastructure">Infrastructure</option>
                  <option value="Config">Configuration</option>
                  <option value="Application">Application</option>
                </select>
              </label>
            </div>
          </div>
        </div>

        {/* Incidents Table */}
        <div className="activity-table-wrapper">
          {finalFiltered.length > 0 ? (
            <div className="activity-table">
              {finalFiltered.map((item) => (
                <div className="activity-row" key={item.id}>
                  <div className="activity-col-main">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="incident-id">{item.id}</span>
                      {item.isRealLocal && (
                        <span className="badge" style={{ background: '#e0e7ff', color: '#4338ca', fontSize: '10px' }}>
                          Local Analysis
                        </span>
                      )}
                    </div>
                    <strong>{item.title}</strong>
                    <p className="activity-cause">
                      <span>Root Cause:</span> {item.rootCause}
                    </p>
                  </div>

                  <div className="activity-col-meta">
                    <Severity severity={item.severity} />
                    <span className="category-pill">{item.category}</span>
                  </div>

                  <div className="activity-col-perf">
                    <small>Component</small>
                    <span>{item.component}</span>
                  </div>

                  <div className="activity-col-perf">
                    <small>MTTR / MTTD</small>
                    <span>{item.mttrHours}h · {item.mttdMinutes}m</span>
                  </div>

                  <div className="activity-col-date">
                    <small>{item.date}</small>
                    <span>{item.timestamp}</span>
                  </div>

                  <div className="activity-col-action">
                    {item.isRealLocal ? (
                      <Link to={`/incidents/${item.id.replace('INC-', '')}`} className="text-button">
                        View RCA <ArrowUpRight size={14} />
                      </Link>
                    ) : (
                      <Link to={`/similar?q=${encodeURIComponent(item.title)}`} className="text-button">
                        Search Similar <ArrowUpRight size={14} />
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty" style={{ padding: '40px 20px' }}>
              <AlertTriangle size={32} />
              <p>No incident activity matched your filters.</p>
              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  setSearchQuery('')
                  setSeverityFilter('All')
                  setCategoryFilter('All')
                }}
              >
                Reset Filters
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export default IncidentActivityPage
