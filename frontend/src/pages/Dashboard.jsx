import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";
import { 
  DollarSign, 
  Users, 
  ShoppingCart, 
  TrendingUp, 
  Globe,
  Package,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
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
  LineChart,
  Line,
  Legend
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const COLORS = ["#2563EB", "#06B6D4", "#8B5CF6", "#F59E0B", "#EC4899", "#10B981"];

// KPI Card Component
const KPICard = ({ title, value, icon: Icon, trend, trendValue, loading }) => {
  if (loading) {
    return (
      <Card className="bg-white border-border shadow-sm hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-8 w-32" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white border-border shadow-sm hover:shadow-md transition-all duration-200" data-testid={`kpi-${title?.toLowerCase().replace(/\s/g, '-')}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
            <h3 className="text-2xl font-bold text-[#0F172A]">{value}</h3>
            {trend !== undefined && (
              <div className={`flex items-center gap-1 mt-2 text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                {trend >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span>{Math.abs(trend).toFixed(1)}%</span>
              </div>
            )}
          </div>
          <div className="w-12 h-12 rounded-lg bg-[#2563EB]/10 flex items-center justify-center">
            <Icon className="w-6 h-6 text-[#2563EB]" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Chart Card Component
const ChartCard = ({ title, children, className = "" }) => (
  <Card className={`bg-white border-border shadow-sm ${className}`}>
    <CardHeader className="pb-2">
      <CardTitle className="text-lg font-semibold text-[#0F172A]">{title}</CardTitle>
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [categoryData, setCategoryData] = useState([]);
  const [countryData, setCountryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
          const res = await axios.get(`${API}/pipeline/results`);
          setKpis(res.data.kpis);
          setPerformance(res.data.performance);
          } catch (err) {
      console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data");
        }
        
        // Process category data
        if (res.data.performance?.by_category) {
          setCategoryData(
            res.data.performance.by_category.slice(0, 6).map(cat => ({
              name: cat.category?.substring(0, 15) || "Unknown",
              revenue: cat.revenue,
              transactions: cat.transactions
            }))
          );
        }
        
        // Process country data
        if (perfRes.data.by_country) {
          setCountryData(perfRes.data.by_country.slice(0, 6).map(c => ({
            name: c.country?.substring(0, 12) || 'Unknown',
            value: c.revenue
          })));
        }

      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatCurrency = (value) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
    return `$${value?.toFixed(2) || 0}`;
  };

  const formatNumber = (value) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value?.toLocaleString() || 0;
  };

  const revenueKpis = kpis?.kpis?.revenue || {};
  const customerKpis = kpis?.kpis?.customer || {};
  const growthKpis = kpis?.kpis?.growth || {};

  return (
    <div className="space-y-8 animate-fade-in" data-testid="dashboard-page">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Revenue"
          value={formatCurrency(revenueKpis.total_revenue)}
          icon={DollarSign}
          trend={growthKpis.mom_growth}
          loading={loading}
        />
        <KPICard
          title="Unique Customers"
          value={formatNumber(customerKpis.unique_customers)}
          icon={Users}
          loading={loading}
        />
        <KPICard
          title="Total Transactions"
          value={formatNumber(revenueKpis.total_transactions)}
          icon={ShoppingCart}
          loading={loading}
        />
        <KPICard
          title="Avg Order Value"
          value={formatCurrency(revenueKpis.avg_order_value)}
          icon={TrendingUp}
          loading={loading}
        />
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard
          title="Repeat Customer Rate"
          value={`${customerKpis.repeat_customer_rate || 0}%`}
          icon={Users}
          loading={loading}
        />
        <KPICard
          title="Total Items Sold"
          value={formatNumber(revenueKpis.total_items_sold)}
          icon={Package}
          loading={loading}
        />
        <KPICard
          title="Countries"
          value={kpis?.kpis?.geographic?.unique_countries || 0}
          icon={Globe}
          loading={loading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Revenue Trend */}
        <ChartCard title="Monthly Revenue Trend">
          {loading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performance?.monthly?.slice(-12) || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis 
                  dataKey="period" 
                  tick={{ fontSize: 12, fill: '#64748B' }}
                  tickFormatter={(val) => val?.substring(5) || ''}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#64748B' }}
                  tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
                />
                <Tooltip 
                  formatter={(value) => [`$${value?.toLocaleString()}`, 'Revenue']}
                  contentStyle={{ 
                    background: '#fff', 
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#2563EB" 
                  strokeWidth={2}
                  dot={{ fill: '#2563EB', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Revenue by Country */}
        <ChartCard title="Revenue by Country">
          {loading ? (
            <Skeleton className="h-[300px] w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={countryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {countryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [`$${value?.toLocaleString()}`, 'Revenue']}
                  contentStyle={{ 
                    background: '#fff', 
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px'
                  }}
                />
                <Legend 
                  layout="vertical" 
                  align="right" 
                  verticalAlign="middle"
                  formatter={(value) => <span className="text-sm text-gray-600">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </div>

      {/* Category Performance */}
      <ChartCard title="Revenue by Product Category">
        {loading ? (
          <Skeleton className="h-[300px] w-full" />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                type="number" 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <YAxis 
                type="category" 
                dataKey="name" 
                width={120}
                tick={{ fontSize: 12, fill: '#64748B' }}
              />
              <Tooltip 
                formatter={(value) => [`$${value?.toLocaleString()}`, 'Revenue']}
                contentStyle={{ 
                  background: '#fff', 
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="revenue" fill="#2563EB" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </ChartCard>

      {/* Top Products Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-[#0F172A]">Top Products</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Product</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Quantity</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Transactions</th>
                  </tr>
                </thead>
                <tbody>
                  {performance?.top_products?.slice(0, 5).map((product, index) => (
                    <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                      <td className="py-3 px-4">
                        <div>
                          <p className="font-medium text-[#0F172A]">{product.product_code}</p>
                          <p className="text-sm text-muted-foreground truncate max-w-xs">{product.description}</p>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right font-medium">{formatCurrency(product.revenue)}</td>
                      <td className="py-3 px-4 text-right">{formatNumber(product.quantity_sold)}</td>
                      <td className="py-3 px-4 text-right">{formatNumber(product.transactions)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
