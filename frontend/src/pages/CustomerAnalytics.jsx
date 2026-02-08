import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from "recharts";
import { Users, Target, TrendingUp, AlertTriangle, Crown, DollarSign } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const COLORS = ["#2563EB", "#06B6D4", "#8B5CF6", "#F59E0B", "#EC4899", "#10B981", "#EF4444", "#6366F1"];

const SEGMENT_COLORS = {
  'Champions': '#10B981',
  'Loyal Customers': '#2563EB',
  'Potential Loyalists': '#06B6D4',
  'Recent Customers': '#8B5CF6',
  'Promising': '#F59E0B',
  'Need Attention': '#EC4899',
  'About to Sleep': '#F97316',
  'At Risk': '#EF4444',
  "Can't Lose Them": '#DC2626',
  'Hibernating': '#94A3B8',
  'Lost': '#64748B'
};

// Summary Card Component
const SummaryCard = ({ title, value, subtitle, icon: Icon, color = "#2563EB" }) => (
  <Card className="bg-white border-border shadow-sm">
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-2xl font-bold text-[#0F172A] mt-1">{value}</h3>
          {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
          <Icon className="w-6 h-6" style={{ color }} />
        </div>
      </div>
    </CardContent>
  </Card>
);

// RFM Tab Component
const RFMAnalysis = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  const segmentData = data?.segment_summary || [];
  const distribution = data?.rfm_distribution?.segment_distribution || {};

  const pieData = Object.entries(distribution).map(([name, value]) => ({ 
    name, 
    value,
    color: SEGMENT_COLORS[name] || '#64748B'
  }));

  return (
    <div className="space-y-6">
      {/* Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Customers"
          value={data?.total_customers?.toLocaleString() || 0}
          icon={Users}
          color="#2563EB"
        />
        <SummaryCard
          title="Avg Recency"
          value={`${data?.metrics_summary?.avg_recency || 0} days`}
          icon={Target}
          color="#06B6D4"
        />
        <SummaryCard
          title="Avg Frequency"
          value={data?.metrics_summary?.avg_frequency?.toFixed(1) || 0}
          icon={TrendingUp}
          color="#8B5CF6"
        />
        <SummaryCard
          title="Total Revenue"
          value={`$${(data?.metrics_summary?.total_revenue || 0).toLocaleString()}`}
          icon={DollarSign}
          color="#10B981"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Segment Distribution Pie */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle>Customer Segment Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  dataKey="value"
                  label={({ name, percent }) => `${name.substring(0, 10)}.. (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Segment Revenue */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle>Revenue by Segment</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={segmentData.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis 
                  type="number" 
                  tick={{ fontSize: 12, fill: '#64748B' }}
                  tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
                />
                <YAxis 
                  type="category" 
                  dataKey="segment" 
                  width={100}
                  tick={{ fontSize: 11, fill: '#64748B' }}
                />
                <Tooltip 
                  formatter={(value) => [`$${value?.toLocaleString()}`, 'Revenue']}
                  contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
                />
                <Bar dataKey="total_monetary" radius={[0, 4, 4, 0]}>
                  {segmentData.slice(0, 8).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[entry.segment] || COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Segment Details Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Segment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Segment</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Customers</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">% of Total</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Recency</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Frequency</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue %</th>
                </tr>
              </thead>
              <tbody>
                {segmentData.map((seg, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: SEGMENT_COLORS[seg.segment] || '#64748B' }}
                        />
                        <span className="font-medium text-[#0F172A]">{seg.segment}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">{seg.customer_count?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{seg.customer_pct}%</td>
                    <td className="py-3 px-4 text-right">{seg.avg_recency?.toFixed(0)} days</td>
                    <td className="py-3 px-4 text-right">{seg.avg_frequency?.toFixed(1)}</td>
                    <td className="py-3 px-4 text-right font-medium">${seg.total_monetary?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <Badge variant="secondary">{seg.revenue_pct}%</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// K-Means Segmentation Tab
const KMeansSegmentation = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  const profiles = data?.cluster_profiles || [];
  const elbowData = data?.elbow_analysis || {};

  // Prepare elbow curve data
  const elbowChartData = elbowData.k_values?.map((k, i) => ({
    k,
    inertia: elbowData.inertias?.[i],
    silhouette: elbowData.silhouette_scores?.[i]
  })) || [];

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard
          title="Optimal Clusters"
          value={data?.n_clusters || 0}
          subtitle={`Silhouette: ${data?.silhouette_score?.toFixed(3)}`}
          icon={Target}
          color="#2563EB"
        />
        <SummaryCard
          title="Total Customers"
          value={data?.total_customers?.toLocaleString() || 0}
          icon={Users}
          color="#06B6D4"
        />
        <SummaryCard
          title="Features Used"
          value={data?.features_used?.length || 0}
          icon={TrendingUp}
          color="#8B5CF6"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Elbow Curve */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle>Elbow Analysis</CardTitle>
            <CardDescription>Silhouette score by cluster count</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={elbowChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="k" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip 
                  contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
                />
                <Bar dataKey="silhouette" fill="#2563EB" radius={[4, 4, 0, 0]} name="Silhouette Score" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Cluster Distribution */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle>Cluster Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={profiles}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="customer_count"
                  nameKey="label"
                  label={({ label, percentage }) => `${label} (${percentage}%)`}
                >
                  {profiles.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Cluster Profiles */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Cluster Profiles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Cluster</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Label</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Customers</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Transactions</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Spend</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Total Revenue</th>
                </tr>
              </thead>
              <tbody>
                {profiles.map((profile, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4">
                      <Badge style={{ backgroundColor: COLORS[index % COLORS.length] }}>
                        Cluster {profile.cluster_id}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 font-medium text-[#0F172A]">{profile.label}</td>
                    <td className="py-3 px-4 text-right">{profile.customer_count?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{profile.avg_transactions?.toFixed(1)}</td>
                    <td className="py-3 px-4 text-right">${profile.avg_spend?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right font-medium">${profile.total_revenue?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// CLV Tab
const CLVAnalysis = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  const summary = data?.summary || {};
  const distribution = data?.distribution || [];
  const topCustomers = data?.top_customers || [];
  const atRisk = data?.at_risk_customers || [];

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Predicted CLV"
          value={`$${summary.total_predicted_clv?.toLocaleString() || 0}`}
          icon={DollarSign}
          color="#10B981"
        />
        <SummaryCard
          title="Average CLV"
          value={`$${summary.avg_clv?.toLocaleString() || 0}`}
          icon={TrendingUp}
          color="#2563EB"
        />
        <SummaryCard
          title="Avg Order Value"
          value={`$${summary.avg_order_value?.toFixed(2) || 0}`}
          icon={Target}
          color="#8B5CF6"
        />
        <SummaryCard
          title="Avg Churn Risk"
          value={`${((summary.avg_churn_probability || 0) * 100).toFixed(1)}%`}
          icon={AlertTriangle}
          color="#F59E0B"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CLV Distribution */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle>CLV Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip 
                  contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
                />
                <Bar dataKey="customer_count" fill="#2563EB" radius={[4, 4, 0, 0]} name="Customers" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* At Risk Customers */}
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              High-Value At-Risk Customers
            </CardTitle>
          </CardHeader>
          <CardContent>
            {atRisk.length > 0 ? (
              <div className="space-y-3">
                {atRisk.slice(0, 5).map((customer, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                    <div>
                      <p className="font-medium text-[#0F172A]">Customer {customer.customer_id}</p>
                      <p className="text-sm text-muted-foreground">
                        {customer.days_since_last} days inactive
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-[#0F172A]">${customer.predictive_clv?.toLocaleString()}</p>
                      <Badge variant="destructive">{(customer.churn_probability * 100).toFixed(0)}% risk</Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">No at-risk customers identified</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top Customers */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Crown className="w-5 h-5 text-amber-500" />
            Top Customers by CLV
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Customer ID</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Orders</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Total Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Order</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Predicted CLV</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Churn Risk</th>
                </tr>
              </thead>
              <tbody>
                {topCustomers.map((customer, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 font-medium">{customer.customer_id}</td>
                    <td className="py-3 px-4 text-right">{customer.total_orders}</td>
                    <td className="py-3 px-4 text-right">${customer.total_revenue?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">${customer.avg_order_value?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right font-bold text-[#10B981]">${customer.predictive_clv?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <Badge variant={customer.churn_probability > 0.5 ? "destructive" : "secondary"}>
                        {(customer.churn_probability * 100).toFixed(0)}%
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Component
const CustomerAnalytics = () => {
  const [rfmData, setRfmData] = useState(null);
  const [segmentationData, setSegmentationData] = useState(null);
  const [clvData, setClvData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("rfm");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [rfmRes, segRes, clvRes] = await Promise.all([
        axios.get(`${API}/rfm`),
        axios.get(`${API}/segmentation`),
        axios.get(`${API}/clv`)
      ]);

      setRfmData(rfmRes.data);
      setSegmentationData(segRes.data);
      setClvData(clvRes.data);
    } catch (err) {
      console.error("Error fetching customer analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="customer-analytics-page">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="rfm" data-testid="tab-rfm">RFM Analysis</TabsTrigger>
          <TabsTrigger value="kmeans" data-testid="tab-kmeans">K-Means Segmentation</TabsTrigger>
          <TabsTrigger value="clv" data-testid="tab-clv">Customer Lifetime Value</TabsTrigger>
        </TabsList>

        <TabsContent value="rfm">
          <RFMAnalysis data={rfmData} loading={loading} />
        </TabsContent>

        <TabsContent value="kmeans">
          <KMeansSegmentation data={segmentationData} loading={loading} />
        </TabsContent>

        <TabsContent value="clv">
          <CLVAnalysis data={clvData} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CustomerAnalytics;
