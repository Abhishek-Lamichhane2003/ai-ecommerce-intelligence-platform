import React, { useEffect, useMemo, useState } from 'react'
import {
  BarChart,
  Bar,
  CartesianGrid,
  Legend,
  LineChart,
  Line,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from './api'

const money = (value) => new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 0,
}).format(Number(value || 0))

const money2 = (value) => new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2,
}).format(Number(value || 0))

const number = (value) => new Intl.NumberFormat('en-US').format(Number(value || 0))

const compactMoney = (value) => {
  const n = Number(value || 0)
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (Math.abs(n) >= 1_000) return `$${Math.round(n / 1_000)}k`
  return money(n)
}

function formatCell(column, value) {
  if (value == null || value === '') return '—'
  const key = String(column).toLowerCase()

  if (key.includes('date') || key.includes('purchase')) {
    return String(value).slice(0, 10)
  }

  if (
    key.includes('revenue') || key.includes('monetary') || key.includes('price') ||
    key.includes('order_value') || key.includes('order value') || key.includes('spend') ||
    key.includes('charges') || key.includes('discount_amount') || key.includes('discount given') ||
    key.includes('gross_sales') || key.includes('net_revenue') || key.includes('invoice_value')
  ) {
    return money2(value)
  }

  if (key.includes('pct') || key.includes('percent') || key === 'gst') {
    const n = Number(value)
    const pct = Math.abs(n) <= 1 ? n * 100 : n
    return `${pct.toFixed(1)}%`
  }

  if (
    key.includes('recency') || key.includes('frequency') || key.includes('tenure') ||
    key.startsWith('avg_') || key.startsWith('avg ')
  ) {
    return Number(value).toLocaleString('en-US', { maximumFractionDigits: 1 })
  }

  if (typeof value === 'number') {
    return Number(value).toLocaleString('en-US', { maximumFractionDigits: 2 })
  }

  return String(value)
}

const navItems = [
  ['overview', 'Overview', '◫'],
  ['sales', 'Sales Intelligence', '↗'],
  ['customers', 'Customer Intelligence', '◎'],
  ['segments', 'Customer Segmentation', '◈'],
  ['ai', 'AI Analyst', '✦'],
  ['data', 'Data Explorer', '⌕'],
]

function Loading() {
  return <div className="loading-card">Loading analytics...</div>
}

function ErrorBox({ message }) {
  return <div className="error-box"><strong>Could not load this page.</strong><span>{message}</span></div>
}

function Metric({ label, value, hint }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {hint && <div className="metric-hint">{hint}</div>}
    </div>
  )
}

function ChartCard({ title, eyebrow, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          {eyebrow && <div className="eyebrow">{eyebrow}</div>}
          <h3>{title}</h3>
        </div>
      </div>
      <div className="chart-wrap">{children}</div>
    </section>
  )
}

function DataTable({ rows, columns }) {
  if (!rows?.length) return <div className="empty-state">No rows to display.</div>
  const cols = columns || Object.keys(rows[0])
  return (
    <div className="table-scroll">
      <table>
        <thead><tr>{cols.map((c) => <th key={c}>{c.replaceAll('_', ' ')}</th>)}</tr></thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {cols.map((c) => <td key={c}>{formatCell(c, row[c])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Hero({ status }) {
  return (
    <header className="hero">
      <div className="hero-glow hero-glow-one" />
      <div className="hero-glow hero-glow-two" />
      <div className="hero-copy">
        <div className="hero-kicker">FULL-STACK DATA + AI PROJECT</div>
        <h1>AI E-Commerce<br/><span>Intelligence Platform</span></h1>
        <p>
          A full-stack analytics product that turns 50K+ e-commerce transaction lines into
          business intelligence, customer segments, and natural-language SQL analysis.
        </p>
        <div className="hero-tags">
          <span>React</span><span>FastAPI</span><span>SQL</span><span>Machine Learning</span><span>AI</span>
        </div>
      </div>
      <div className="hero-status">
        <div className={`status-dot ${status?.ok ? 'online' : ''}`} />
        <div>
          <strong>{status?.ok ? 'Platform online' : 'Backend waiting'}</strong>
          <small>{status?.ai_mode === 'llm' ? 'LLM mode enabled' : 'Demo SQL mode'}</small>
        </div>
      </div>
    </header>
  )
}

function OverviewPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.overview().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <ErrorBox message={error} />
  if (!data) return <Loading />
  const k = data.kpis
  return (
    <>
      <div className="section-title"><div><span className="eyebrow">BUSINESS HEALTH</span><h2>Executive Overview</h2></div><p>{k.start_date} → {k.end_date}</p></div>
      <div className="metrics-grid">
        <Metric label="Net Revenue" value={money(k.revenue)} hint={`${number(k.transaction_lines)} transaction lines`} />
        <Metric label="Orders" value={number(k.orders)} hint="Unique transactions" />
        <Metric label="Customers" value={number(k.customers)} hint="Unique shoppers" />
        <Metric label="Avg Order Value" value={money(k.aov)} hint="Revenue per order" />
        <Metric label="Units Sold" value={number(k.units)} />
        <Metric label="Discounts Given" value={money(k.discounts)} />
        <Metric label="Marketing Spend" value={money(k.marketing_spend)} />
        <Metric label="Revenue / Marketing $" value={k.roas ? `${k.roas.toFixed(2)}x` : '—'} />
      </div>
      <div className="two-col wide-first">
        <ChartCard title="Monthly Revenue Trend" eyebrow="REVENUE">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data.monthly}>
              <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/>
              <XAxis dataKey="Year_Month" stroke="#7d8ca5"/><YAxis stroke="#7d8ca5" tickFormatter={(v) => `$${Math.round(v/1000)}k`}/>
              <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
              <Line type="monotone" dataKey="revenue" stroke="#7c5cff" strokeWidth={3} dot={{fill:'#35d7ff', r:4}}/>
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Revenue by Location" eyebrow="GEOGRAPHY">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data.locations}>
              <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/>
              <XAxis dataKey="location" stroke="#7d8ca5"/><YAxis stroke="#7d8ca5" tickFormatter={(v) => `$${Math.round(v/1000)}k`}/>
              <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
              <Bar dataKey="revenue" fill="#22d3a6" radius={[8,8,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <ChartCard title="Top Product Categories" eyebrow="CATEGORY PERFORMANCE">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={data.categories} layout="vertical" margin={{left:40}}>
            <CartesianGrid stroke="rgba(255,255,255,.08)" horizontal={false}/>
            <XAxis type="number" stroke="#7d8ca5" tickFormatter={(v) => `$${Math.round(v/1000)}k`}/>
            <YAxis type="category" dataKey="category" width={130} stroke="#7d8ca5"/>
            <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
            <Bar dataKey="revenue" fill="#35d7ff" radius={[0,8,8,0]}/>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </>
  )
}

function SalesPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.sales().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <ErrorBox message={error} />
  if (!data) return <Loading />
  return (
    <>
      <div className="section-title"><div><span className="eyebrow">COMMERCIAL PERFORMANCE</span><h2>Sales Intelligence</h2></div><p>Products, categories, coupons and transaction trends</p></div>
      <div className="two-col">
        <ChartCard title="Category Revenue" eyebrow="CATEGORIES">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data.categories.slice(0, 8)}>
              <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/><XAxis dataKey="category" stroke="#7d8ca5" tick={{fontSize:11}}/><YAxis stroke="#7d8ca5" width={72} tickFormatter={compactMoney}/>
              <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
              <Bar dataKey="revenue" fill="#7c5cff" radius={[8,8,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Coupon Performance" eyebrow="PROMOTIONS">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data.coupons}>
              <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/><XAxis dataKey="coupon_status" stroke="#7d8ca5"/><YAxis stroke="#7d8ca5" width={72} tickFormatter={compactMoney}/>
              <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
              <Bar dataKey="revenue" fill="#22d3a6" radius={[8,8,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <section className="panel"><div className="panel-head"><div><div className="eyebrow">TOP PRODUCTS</div><h3>Highest-Revenue Products</h3></div></div><DataTable rows={data.products} /></section>
    </>
  )
}

function CustomersPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.customers().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <ErrorBox message={error} />
  if (!data) return <Loading />
  return (
    <>
      <div className="section-title"><div><span className="eyebrow">CUSTOMER VALUE</span><h2>Customer Intelligence</h2></div><p>Who buys, how often, and how much they spend</p></div>
      <ChartCard title="Customer Revenue by Location" eyebrow="GEOGRAPHY">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data.locations}>
            <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/><XAxis dataKey="location" stroke="#7d8ca5"/><YAxis stroke="#7d8ca5" width={72} tickFormatter={compactMoney}/>
            <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}} formatter={(v) => money(v)}/>
            <Bar dataKey="revenue" fill="#35d7ff" radius={[8,8,0,0]}/>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <section className="panel"><div className="panel-head"><div><div className="eyebrow">CUSTOMER TABLE</div><h3>Top Customers by Revenue</h3></div></div><DataTable rows={data.top_customers} /></section>
    </>
  )
}

function SegmentationPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.segmentation().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <ErrorBox message={error} />
  if (!data) return <Loading />
  const counts = data.profiles.map((p) => ({segment: p.segment, customers: p.customers}))
  return (
    <>
      <div className="section-title"><div><span className="eyebrow">MACHINE LEARNING</span><h2>Customer Segmentation</h2></div><p>K-Means clustering using recency, frequency and monetary value</p></div>
      <div className="metrics-grid compact">
        <Metric label="Customers Segmented" value={number(data.customers.length)} />
        <Metric label="Segments" value={number(data.profiles.length)} />
        <Metric label="Silhouette Score" value={data.silhouette_score ? data.silhouette_score.toFixed(3) : '—'} hint="Cluster separation quality" />
      </div>
      <div className="two-col">
        <ChartCard title="Customers per Segment" eyebrow="SEGMENT SIZE">
          <ResponsiveContainer width="100%" height={330}>
            <BarChart data={counts}>
              <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false}/><XAxis dataKey="segment" stroke="#7d8ca5"/><YAxis stroke="#7d8ca5"/>
              <Tooltip contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}}/>
              <Bar dataKey="customers" fill="#7c5cff" radius={[8,8,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Frequency vs Customer Value" eyebrow="RFM SPACE">
          <ResponsiveContainer width="100%" height={330}>
            <ScatterChart margin={{ top: 8, right: 12, bottom: 12, left: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,.08)"/>
              <XAxis
                type="number"
                dataKey="frequency"
                name="Frequency"
                stroke="#7d8ca5"
                tickCount={6}
                allowDecimals={false}
              />
              <YAxis
                type="number"
                dataKey="monetary"
                name="Customer Value"
                stroke="#7d8ca5"
                width={72}
                tickCount={6}
                tickFormatter={compactMoney}
              />
              <Tooltip
                cursor={{strokeDasharray:'3 3'}}
                contentStyle={{background:'#0f1c30',border:'1px solid #223453',borderRadius:12}}
                formatter={(value, name) => [name === 'Customer Value' ? money2(value) : number(value), name]}
              />
              <Legend />
              <Scatter name="Champions" data={data.customers.filter((d) => d.segment === 'Champions')} fill="#35d7ff"/>
              <Scatter name="Loyal" data={data.customers.filter((d) => d.segment === 'Loyal')} fill="#22d3a6"/>
              <Scatter name="Developing" data={data.customers.filter((d) => d.segment === 'Developing')} fill="#7c5cff"/>
              <Scatter name="At Risk" data={data.customers.filter((d) => d.segment === 'At Risk')} fill="#fb7185"/>
            </ScatterChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <section className="panel"><div className="panel-head"><div><div className="eyebrow">CLUSTER PROFILES</div><h3>Segment Characteristics</h3></div></div><DataTable rows={data.profiles} /></section>
    </>
  )
}

function AIPage() {
  const [question, setQuestion] = useState('Which product categories generate the most revenue?')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const suggestions = [
    'Which locations generate the most revenue?',
    'Show the top 10 products by revenue.',
    'How does coupon usage compare by revenue?',
    'Who are the top customers by total spending?',
    'Show monthly revenue trends.',
  ]
  const run = async () => {
    setLoading(true); setError('')
    try {
      const response = await api.aiQuery(question)
      setResult(response)
      setHistory(await api.aiHistory())
    } catch (e) { setError(e.message) } finally { setLoading(false) }
  }
  useEffect(() => { api.aiHistory().then(setHistory).catch(() => {}) }, [])
  return (
    <>
      <div className="section-title"><div><span className="eyebrow">NATURAL LANGUAGE → SQL</span><h2>AI Data Analyst</h2></div><p>Ask business questions in plain English</p></div>
      <section className="ai-console">
        <div className="ai-orb">✦</div>
        <div className="ai-input-wrap">
          <label>Ask your dataset</label>
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={3}/>
          <div className="suggestions">{suggestions.map((s) => <button key={s} onClick={() => setQuestion(s)}>{s}</button>)}</div>
          <button className="primary-button" onClick={run} disabled={loading}>{loading ? 'Analyzing...' : 'Run AI Analysis'}</button>
        </div>
      </section>
      {error && <ErrorBox message={error}/>} 
      {result && <>
        <section className="insight-card"><div className="eyebrow">AI EXPLANATION</div><p>{result.explanation}</p><div className="mode-pill">{result.mode === 'llm' ? 'LLM mode' : 'Demo SQL mode'} · {result.row_count} rows</div></section>
        <section className="panel"><div className="panel-head"><div><div className="eyebrow">GENERATED SQL</div><h3>Query used by the analyst</h3></div></div><pre className="sql-block">{result.sql}</pre></section>
        <section className="panel"><div className="panel-head"><div><div className="eyebrow">QUERY RESULT</div><h3>Analysis Output</h3></div></div><DataTable rows={result.rows} columns={result.columns}/></section>
      </>}
      <section className="panel"><div className="panel-head"><div><div className="eyebrow">AUDIT TRAIL</div><h3>Recent Query History</h3></div></div><DataTable rows={history}/></section>
    </>
  )
}

function DataPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.preview().then(setData).catch((e) => setError(e.message)) }, [])
  if (error) return <ErrorBox message={error}/>
  if (!data) return <Loading/>
  return <><div className="section-title"><div><span className="eyebrow">RAW DATA</span><h2>Data Explorer</h2></div><p>{number(data.total_rows)} cleaned transaction lines</p></div><section className="panel"><DataTable rows={data.rows} columns={data.columns}/></section></>
}

export default function App() {
  const [page, setPage] = useState('overview')
  const [status, setStatus] = useState(null)
  useEffect(() => { api.status().then(setStatus).catch((e) => setStatus({ok:false,error:e.message})) }, [])
  const content = useMemo(() => ({
    overview: <OverviewPage/>, sales: <SalesPage/>, customers: <CustomersPage/>, segments: <SegmentationPage/>, ai: <AIPage/>, data: <DataPage/>,
  })[page], [page])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">AI</div><div><strong>Commerce IQ</strong><small>Intelligence Platform</small></div></div>
        <nav>{navItems.map(([key,label,icon]) => <button key={key} className={page===key?'active':''} onClick={() => setPage(key)}><span>{icon}</span>{label}</button>)}</nav>
        <div className="sidebar-bottom">
          <div className="stack-title">PROJECT STACK</div>
          <div className="stack-list"><span>React</span><span>FastAPI</span><span>SQL</span><span>scikit-learn</span><span>OpenAI</span></div>
        </div>
      </aside>
      <main>
        <Hero status={status}/>
        {status?.error && <div className="error-box"><strong>Backend setup issue</strong><span>{status.error}</span><span>Make sure data/ecommerce_sales.csv exists.</span></div>}
        <div className="content">{content}</div>
      </main>
    </div>
  )
}
