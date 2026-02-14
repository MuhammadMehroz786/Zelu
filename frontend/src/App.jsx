import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  LayoutDashboard,
  GitMerge,
  Package,
  Terminal,
  Settings,
  BarChart3,
  ScrollText,
  Moon,
  Sun,
  Plus,
  Search,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Play,
  Pause,
  Eye,
  Edit3,
  Download,
  ChevronRight,
  ChevronDown,
  Save,
  RotateCcw,
  ExternalLink,
  MoreHorizontal,
  X,
  Check,
  Cpu
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

/**
 * CONFIGURATION & MOCK DATA
 * Toggle USE_MOCK_API to false to hit the real Flask endpoints.
 */
const USE_MOCK_API = true;
const API_BASE_URL = "http://localhost:5000";

// --- Mock Data Generators ---
const generateId = () => Math.random().toString(36).substr(2, 9);
const PHASES = [
  "Trend Discovery", "Niche Validation", "Audience Profiling",
  "Product Structure", "Content Writing", "Visual Design",
  "Funnel & Copy", "Campaign Launch"
];

// --- API Service Layer ---
const api = {
  request: async (endpoint, method = 'GET', data = null) => {
    if (USE_MOCK_API) {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 600));
      return mockBackend(endpoint, method, data);
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null,
      });
      if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error(error);
      throw error;
    }
  }
};

// --- Mock Backend Logic ---
let mockPipelines = [
  {
    id: "p1", niche: "AI Productivity", topic: "Notion Templates", status: "running",
    currentPhase: 4, lastUpdated: new Date().toISOString(),
    phases: PHASES.map((name, i) => ({
      id: i + 1, name, status: i < 4 ? 'completed' : i === 4 ? 'running' : 'pending',
      output: i < 4 ? { data: "Sample JSON output for this phase..." } : null,
      duration: "2m 30s"
    }))
  },
  {
    id: "p2", niche: "Keto Diet", topic: "30 Day Meal Plan", status: "paused",
    currentPhase: 2, lastUpdated: new Date(Date.now() - 86400000).toISOString(),
    phases: PHASES.map((name, i) => ({
      id: i + 1, name, status: i < 2 ? 'completed' : i === 2 ? 'waiting_approval' : 'pending',
      output: i < 2 ? { data: "Approved data" } : i === 2 ? { trend_score: 98, competition: "high" } : null,
      duration: "1m 15s"
    }))
  }
];

let mockProducts = [
  { id: "prod1", name: "Ultimate Notion Brain", niche: "AI Productivity", type: "main", status: "published", price: 49, created: "2023-10-25" },
  { id: "prod2", name: "Keto Quickstart Guide", niche: "Keto Diet", type: "lead_magnet", status: "draft", price: 0, created: "2023-10-26" },
];

let mockPrompts = PHASES.map((phase, i) => ({
  id: `pmt${i}`, phase, name: `${phase} Generator`, version: "1.2",
  template: `You are an expert in {{niche}}. Analyze the following audience: {{audience}}...`,
  variables: ["niche", "audience"], updatedAt: "2023-10-20"
}));

const mockBackend = (endpoint, method, data) => {
  if (endpoint === '/api/pipelines/') {
    if (method === 'POST') {
      const newPipeline = {
        id: generateId(),
        niche: data.niche,
        topic: data.topic,
        status: data.auto_start ? 'running' : 'pending',
        currentPhase: 0,
        lastUpdated: new Date().toISOString(),
        phases: PHASES.map((name, i) => ({ id: i+1, name, status: 'pending', output: null }))
      };
      mockPipelines.unshift(newPipeline);
      return newPipeline;
    }
    return { pipelines: mockPipelines };
  }
  if (endpoint.startsWith('/api/pipelines/')) {
    const id = endpoint.split('/')[3];
    if (method === 'GET') return mockPipelines.find(p => p.id === id);
    if (endpoint.includes('/start')) {
      const p = mockPipelines.find(p => p.id === id);
      if(p) p.status = 'running';
      return p;
    }
    if (endpoint.includes('/stop')) {
      const p = mockPipelines.find(p => p.id === id);
      if(p) p.status = 'paused';
      return p;
    }
  }
  if (endpoint === '/api/analytics/dashboard') {
    return {
      productsCreated: 124,
      activePipelines: mockPipelines.filter(p => p.status === 'running').length,
      pendingApprovals: 3,
      dailyOutput: 12
    };
  }
  if (endpoint === '/api/products') return { products: mockProducts };
  if (endpoint === '/api/prompts') return { prompts: mockPrompts };

  return {};
};

// --- UI Components ---

const Card = ({ children, className = "" }) => (
  <div className={`bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, variant = "default", className = "" }) => {
  const variants = {
    default: "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900",
    secondary: "bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100",
    outline: "border border-slate-200 text-slate-900 dark:border-slate-700 dark:text-slate-100",
    destructive: "bg-red-500 text-white",
    success: "bg-emerald-500 text-white",
    warning: "bg-amber-500 text-white",
    info: "bg-blue-500 text-white",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

const Button = ({ children, onClick, variant = "default", size = "default", className = "", disabled = false, icon: Icon }) => {
  const baseStyle = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50";
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700 shadow",
    destructive: "bg-red-500 text-white hover:bg-red-600 shadow",
    outline: "border border-slate-200 bg-transparent hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800",
    ghost: "hover:bg-slate-100 dark:hover:bg-slate-800",
    link: "text-blue-600 underline-offset-4 hover:underline",
  };
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {Icon && <Icon className="mr-2 h-4 w-4" />}
      {children}
    </button>
  );
};

const Modal = ({ isOpen, onClose, title, children, footer }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-800 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button onClick={onClose}><X className="h-4 w-4" /></button>
        </div>
        <div className="p-6">{children}</div>
        {footer && (
          <div className="flex items-center justify-end p-6 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 rounded-b-lg gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

// --- Pages ---

// 1. Dashboard
const Dashboard = ({ navigate }) => {
  const [stats, setStats] = useState(null);
  const [pipelines, setPipelines] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPipeline, setNewPipeline] = useState({ niche: '', topic: '', auto_start: false });

  useEffect(() => {
    const fetchData = async () => {
      const s = await api.request('/api/analytics/dashboard');
      const p = await api.request('/api/pipelines/');
      setStats(s);
      setPipelines(p.pipelines);
    };
    fetchData();
  }, []);

  const handleCreate = async () => {
    await api.request('/api/pipelines/', 'POST', newPipeline);
    setIsModalOpen(false);
    const p = await api.request('/api/pipelines/');
    setPipelines(p.pipelines);
  };

  if (!stats) return <div className="p-8 text-center">Loading Dashboard...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Products Created", value: stats.productsCreated, icon: Package, color: "text-blue-500" },
          { label: "Active Pipelines", value: stats.activePipelines, icon: Cpu, color: "text-emerald-500" },
          { label: "Pending Approvals", value: stats.pendingApprovals, icon: AlertCircle, color: "text-amber-500" },
          { label: "Today's Output", value: stats.dailyOutput, icon: BarChart3, color: "text-indigo-500" },
        ].map((stat, i) => (
          <Card key={i} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
                <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
              </div>
              <stat.icon className={`h-8 w-8 ${stat.color}`} />
            </div>
          </Card>
        ))}
      </div>

      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Recent Pipelines</h2>
        <Button onClick={() => setIsModalOpen(true)} icon={Plus}>New Pipeline</Button>
      </div>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase bg-slate-50 dark:bg-slate-900 text-slate-500">
              <tr>
                <th className="px-6 py-3">Topic / Niche</th>
                <th className="px-6 py-3">Current Phase</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Last Updated</th>
              </tr>
            </thead>
            <tbody>
              {pipelines.map((p) => (
                <tr
                  key={p.id}
                  onClick={() => navigate('pipeline', p.id)}
                  className="border-b border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer"
                >
                  <td className="px-6 py-4 font-medium">
                    <div className="text-slate-900 dark:text-white">{p.topic || "Untitled"}</div>
                    <div className="text-xs text-slate-500">{p.niche}</div>
                  </td>
                  <td className="px-6 py-4">{PHASES[p.currentPhase] || "Finished"}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {new Date(p.lastUpdated).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Start New Product Pipeline"
        footer={<Button onClick={handleCreate}>Start Engine</Button>}
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Niche (Required)</label>
            <input
              className="w-full p-2 rounded border bg-transparent dark:border-slate-700"
              placeholder="e.g. Yoga for Seniors"
              value={newPipeline.niche}
              onChange={e => setNewPipeline({...newPipeline, niche: e.target.value})}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Topic (Optional)</label>
            <input
              className="w-full p-2 rounded border bg-transparent dark:border-slate-700"
              placeholder="e.g. 15 Minute Morning Routine"
              value={newPipeline.topic}
              onChange={e => setNewPipeline({...newPipeline, topic: e.target.value})}
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={newPipeline.auto_start}
              onChange={e => setNewPipeline({...newPipeline, auto_start: e.target.checked})}
            />
            <label className="text-sm">Auto-start pipeline immediately</label>
          </div>
        </div>
      </Modal>
    </div>
  );
};

// 2. Pipeline View
const PipelineView = ({ id, navigate }) => {
  const [pipeline, setPipeline] = useState(null);
  const [expandedPhase, setExpandedPhase] = useState(null);

  useEffect(() => {
    const load = async () => {
      const data = await api.request(`/api/pipelines/${id}`);
      setPipeline(data);
    };
    load();
  }, [id]);

  if (!pipeline) return <div>Loading Pipeline {id}...</div>;

  const handleAction = async (action) => {
    const updated = await api.request(`/api/pipelines/${id}/${action}`, 'POST');
    setPipeline(updated);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button onClick={() => navigate('dashboard')} className="text-sm text-slate-500 hover:text-blue-500 mb-2 flex items-center gap-1">
            <RotateCcw className="h-3 w-3" /> Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            {pipeline.topic}
            <StatusBadge status={pipeline.status} />
          </h1>
          <p className="text-slate-500">{pipeline.niche}</p>
        </div>
        <div className="flex gap-2">
          {pipeline.status === 'running' ? (
            <Button variant="destructive" icon={Pause} onClick={() => handleAction('stop')}>Pause Pipeline</Button>
          ) : (
            <Button variant="default" icon={Play} onClick={() => handleAction('start')}>Resume Pipeline</Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {pipeline.phases.map((phase, index) => (
          <Card key={phase.id} className={`border-l-4 ${
            phase.status === 'completed' ? 'border-l-emerald-500' :
            phase.status === 'running' ? 'border-l-blue-500' :
            phase.status === 'waiting_approval' ? 'border-l-amber-500' :
            phase.status === 'failed' ? 'border-l-red-500' : 'border-l-slate-200'
          }`}>
            <div className="p-4">
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setExpandedPhase(expandedPhase === index ? null : index)}
              >
                <div className="flex items-center gap-4">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                    ${phase.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                      phase.status === 'running' ? 'bg-blue-100 text-blue-700 animate-pulse' :
                      'bg-slate-100 text-slate-500'}
                  `}>
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold">{phase.name}</h3>
                    <p className="text-xs text-slate-500 capitalize">{phase.status.replace('_', ' ')} • {phase.duration || '0s'}</p>
                  </div>
                </div>
                {expandedPhase === index ? <ChevronDown className="h-5 w-5 text-slate-400" /> : <ChevronRight className="h-5 w-5 text-slate-400" />}
              </div>

              {expandedPhase === index && (
                <div className="mt-4 pl-12 border-t pt-4 border-slate-100 dark:border-slate-800">
                  {phase.output ? (
                    <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm overflow-x-auto">
                      <pre>{JSON.stringify(phase.output, null, 2)}</pre>
                    </div>
                  ) : (
                    <div className="text-slate-400 text-sm italic">No output generated yet.</div>
                  )}

                  {phase.status === 'waiting_approval' && (
                    <div className="mt-4 flex gap-2">
                      <Button size="sm" variant="default" icon={Check} className="bg-emerald-600 hover:bg-emerald-700">Approve</Button>
                      <Button size="sm" variant="destructive" icon={X}>Reject</Button>
                      <Button size="sm" variant="outline" icon={Edit3}>Edit Output</Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

// 3. Products List
const ProductsList = () => {
  const [products, setProducts] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    api.request('/api/products').then(d => setProducts(d.products));
  }, []);

  const filtered = products.filter(p => p.name.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Products Library</h1>
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search products..."
            className="pl-9 pr-4 py-2 border rounded-md bg-white dark:bg-slate-900 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filter}
            onChange={e => setFilter(e.target.value)}
          />
        </div>
      </div>

      <Card>
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase bg-slate-50 dark:bg-slate-900 text-slate-500">
            <tr>
              <th className="px-6 py-3">Product Name</th>
              <th className="px-6 py-3">Niche</th>
              <th className="px-6 py-3">Type</th>
              <th className="px-6 py-3">Price</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((product) => (
              <tr key={product.id} className="border-b border-slate-100 dark:border-slate-700">
                <td className="px-6 py-4 font-medium">{product.name}</td>
                <td className="px-6 py-4">{product.niche}</td>
                <td className="px-6 py-4 capitalize">{product.type.replace('_', ' ')}</td>
                <td className="px-6 py-4">${product.price}</td>
                <td className="px-6 py-4">
                  <Badge variant={product.status === 'published' ? 'success' : 'secondary'}>
                    {product.status}
                  </Badge>
                </td>
                <td className="px-6 py-4 flex gap-2">
                  <Button size="sm" variant="ghost" icon={Download} />
                  <Button size="sm" variant="ghost" icon={ExternalLink} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

// 4. Prompt Editor
const PromptsPage = () => {
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);

  useEffect(() => {
    api.request('/api/prompts').then(d => setPrompts(d.prompts));
  }, []);

  return (
    <div className="h-[calc(100vh-100px)] flex gap-6">
      {/* Sidebar List */}
      <Card className="w-1/3 overflow-y-auto">
        <div className="p-4 border-b dark:border-slate-700">
          <h2 className="font-bold">System Prompts</h2>
        </div>
        <div>
          {prompts.map(p => (
            <div
              key={p.id}
              onClick={() => setSelectedPrompt(p)}
              className={`p-4 border-b dark:border-slate-700 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 ${selectedPrompt?.id === p.id ? 'bg-blue-50 dark:bg-slate-800 border-l-4 border-l-blue-500' : ''}`}
            >
              <div className="font-medium">{p.name}</div>
              <div className="text-xs text-slate-500 mt-1 flex justify-between">
                <span>{p.phase}</span>
                <span>v{p.version}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Editor Area */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        {selectedPrompt ? (
          <>
            <div className="p-4 border-b dark:border-slate-700 flex justify-between items-center">
              <div>
                <h2 className="font-bold text-lg">{selectedPrompt.name}</h2>
                <div className="flex gap-2 mt-1">
                  {selectedPrompt.variables.map(v => (
                    <Badge key={v} variant="outline" className="font-mono text-[10px]">{`{{${v}}}`}</Badge>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" icon={Terminal}>Test</Button>
                <Button size="sm" icon={Save}>Save Version</Button>
              </div>
            </div>
            <div className="flex-1 p-4 bg-slate-50 dark:bg-slate-950">
              <textarea
                className="w-full h-full bg-transparent resize-none focus:outline-none font-mono text-sm leading-relaxed"
                value={selectedPrompt.template}
                onChange={(e) => setSelectedPrompt({...selectedPrompt, template: e.target.value})}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-400">
            Select a prompt to edit
          </div>
        )}
      </Card>
    </div>
  );
};

// 5. Analytics
const Analytics = () => {
  const data = [
    { name: 'Mon', products: 4, spend: 200, rev: 400 },
    { name: 'Tue', products: 3, spend: 150, rev: 300 },
    { name: 'Wed', products: 7, spend: 400, rev: 900 },
    { name: 'Thu', products: 5, spend: 300, rev: 600 },
    { name: 'Fri', products: 9, spend: 500, rev: 1200 },
    { name: 'Sat', products: 6, spend: 350, rev: 800 },
    { name: 'Sun', products: 4, spend: 200, rev: 450 },
  ];

  const pieData = [
    { name: 'Health', value: 400 },
    { name: 'Wealth', value: 300 },
    { name: 'Love', value: 300 },
    { name: 'Tech', value: 200 },
  ];
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Performance Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Products Created & Revenue</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                />
                <Legend />
                <Line type="monotone" dataKey="products" stroke="#3b82f6" activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="rev" stroke="#10b981" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-4">Niche Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="font-semibold mb-4">Ad Campaign Performance</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 dark:bg-slate-900 text-slate-500">
              <tr>
                <th className="p-3">Campaign</th>
                <th className="p-3">Impressions</th>
                <th className="p-3">Clicks</th>
                <th className="p-3">CTR</th>
                <th className="p-3">Spend</th>
                <th className="p-3">ROAS</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="p-3 font-medium">Notion Bundle FB_01</td>
                <td className="p-3">12,405</td>
                <td className="p-3">450</td>
                <td className="p-3">3.6%</td>
                <td className="p-3">$210.50</td>
                <td className="p-3 text-emerald-500 font-bold">3.2x</td>
              </tr>
              <tr>
                <td className="p-3 font-medium">Keto Guide IG_Story</td>
                <td className="p-3">8,100</td>
                <td className="p-3">210</td>
                <td className="p-3">2.1%</td>
                <td className="p-3">$150.00</td>
                <td className="p-3 text-emerald-500 font-bold">1.8x</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

// 6. Logs
const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  // Simulate incoming logs
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        const levels = ['info', 'info', 'info', 'warning', 'error'];
        const level = levels[Math.floor(Math.random() * levels.length)];
        const messages = [
          "Phase 2 completed for pipeline p1",
          "Generated image assets for p3",
          "Waiting for user approval on phase 4",
          "API Latency high on image generation",
          "Failed to connect to Stripe API"
        ];
        const newLog = {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
          level,
          message: messages[Math.floor(Math.random() * messages.length)]
        };
        setLogs(prev => [...prev.slice(-99), newLog]); // Keep last 100
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <Card className="h-[calc(100vh-100px)] flex flex-col bg-slate-950 text-slate-300 font-mono text-xs">
      <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900">
        <span className="font-bold flex items-center gap-2"><Terminal className="h-4 w-4"/> System Live Stream</span>
        <Button size="sm" variant="ghost" onClick={() => setLogs([])}>Clear</Button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {logs.map(log => (
          <div key={log.id} className="flex gap-3">
            <span className="text-slate-500">[{log.timestamp}]</span>
            <span className={`uppercase font-bold w-16 ${
              log.level === 'error' ? 'text-red-500' :
              log.level === 'warning' ? 'text-amber-500' : 'text-blue-500'
            }`}>{log.level}</span>
            <span>{log.message}</span>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </Card>
  );
};

// 7. Settings
const SettingsPage = () => {
  const [toggles, setToggles] = useState(
    PHASES.map((p, i) => ({ id: i, name: p, requireApproval: true, enabled: true }))
  );

  const handleToggle = (id, field) => {
    setToggles(toggles.map(t => t.id === id ? { ...t, [field]: !t[field] } : t));
  };

  return (
    <div className="space-y-6">
      <Card className="p-4 bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800">
        <div className="flex gap-3 items-center text-amber-800 dark:text-amber-400">
          <AlertCircle />
          <p className="text-sm font-medium">Safety Mode Active: All automated actions require human approval by default.</p>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {toggles.map(phase => (
          <Card key={phase.id} className="p-6 flex items-center justify-between">
            <div className="font-medium">{phase.name}</div>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <div className={`w-10 h-6 rounded-full p-1 transition-colors ${phase.enabled ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-700'}`}
                     onClick={() => handleToggle(phase.id, 'enabled')}>
                  <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${phase.enabled ? 'translate-x-4' : ''}`} />
                </div>
                <span className="text-xs text-slate-500">Enable</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <div className={`w-10 h-6 rounded-full p-1 transition-colors ${phase.requireApproval ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-700'}`}
                     onClick={() => handleToggle(phase.id, 'requireApproval')}>
                  <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${phase.requireApproval ? 'translate-x-4' : ''}`} />
                </div>
                <span className="text-xs text-slate-500">Require Approval</span>
              </label>
            </div>
          </Card>
        ))}
      </div>
      <div className="flex justify-end">
        <Button icon={Save}>Save Configuration</Button>
      </div>
    </div>
  );
};

// --- Helper Functions ---
const StatusBadge = ({ status }) => {
  const map = {
    running: 'info',
    completed: 'success',
    failed: 'destructive',
    paused: 'warning',
    waiting_approval: 'warning',
    pending: 'secondary',
    published: 'success',
    draft: 'secondary'
  };
  return <Badge variant={map[status] || 'default'}>{status.replace('_', ' ')}</Badge>;
};

// --- Main App Component ---

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentPipelineId, setCurrentPipelineId] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Navigation Helper
  const navigate = (tab, id = null) => {
    setActiveTab(tab);
    if (id) setCurrentPipelineId(id);
  };

  // Render View
  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard': return <Dashboard navigate={navigate} />;
      case 'pipeline': return <PipelineView id={currentPipelineId} navigate={navigate} />;
      case 'products': return <ProductsList />;
      case 'prompts': return <PromptsPage />;
      case 'settings': return <SettingsPage />;
      case 'analytics': return <Analytics />;
      case 'logs': return <LogsPage />;
      default: return <Dashboard navigate={navigate} />;
    }
  };

  return (
    <div className={`min-h-screen font-sans ${isDarkMode ? 'dark' : ''}`}>
      <div className="flex min-h-screen bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-200">

        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex flex-col">
          <div className="p-6 flex items-center gap-2 border-b border-slate-200 dark:border-slate-800">
            <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <GitMerge className="text-white h-5 w-5" />
            </div>
            <span className="text-xl font-bold tracking-tight">ZEULE</span>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {[
              { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
              { id: 'products', icon: Package, label: 'Products' },
              { id: 'prompts', icon: ScrollText, label: 'Prompts' },
              { id: 'analytics', icon: BarChart3, label: 'Analytics' },
              { id: 'settings', icon: Settings, label: 'Settings' },
              { id: 'logs', icon: Terminal, label: 'System Logs' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => navigate(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === item.id
                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800'
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
          </nav>

          <div className="p-4 border-t border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-xs font-bold">
                AD
              </div>
              <div>
                <p className="text-sm font-medium">Admin User</p>
                <p className="text-xs text-slate-500">admin@zeule.ai</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0">
          <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-end px-8 gap-4">
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
            >
              {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </header>

          <div className="flex-1 overflow-y-auto p-8">
            {renderContent()}
          </div>
        </main>

      </div>
    </div>
  );
}
