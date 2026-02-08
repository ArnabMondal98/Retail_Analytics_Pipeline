import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Badge } from "../components/ui/badge";
import { Skeleton } from "../components/ui/skeleton";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area
} from "recharts";
import { TrendingUp, TrendingDown, Calendar, Globe, Package, DollarSign } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const COLORS = ["#2563EB", "#06B6D4", "#8B5CF6", "#F59E0B", "#EC4899", "#10B981"];

// Monthly Performance Tab
const MonthlyPerformance = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[400px]" />
        <Skeleton className="h-[300px]" />
      </div>
    );
  }

  const monthly = data || [];

  return (
    <div className="space-y-6">
      {/* Revenue Trend */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Monthly Revenue Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={monthly}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="period" 
                tick={{ fontSize: 11, fill: '#64748B' }}
                tickFormatter={(val) => val?.substring(5) || ''}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? `$${value?.toLocaleString()}` : value?.toLocaleString(),
                  name === 'revenue' ? 'Revenue' : name
                ]}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#2563EB" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorRevenue)" 
                name="Revenue"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Growth Rate */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Month-over-Month Growth Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthly.slice(1)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="period" 
                tick={{ fontSize: 11, fill: '#64748B' }}
                tickFormatter={(val) => val?.substring(5) || ''}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `${val}%`}
              />
              <Tooltip 
                formatter={(value) => [`${value?.toFixed(1)}%`, 'Growth']}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Bar 
                dataKey="revenue_growth" 
                name="Revenue Growth"
                radius={[4, 4, 0, 0]}
              >
                {monthly.slice(1).map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.revenue_growth >= 0 ? '#10B981' : '#EF4444'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Monthly Data Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Monthly Performance Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Period</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Transactions</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Customers</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Transaction</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Growth</th>
                </tr>
              </thead>
              <tbody>
                {monthly.slice(-12).reverse().map((month, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 font-medium">{month.period}</td>
                    <td className="py-3 px-4 text-right">${month.revenue?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{month.unique_transactions?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{month.unique_customers?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">${month.avg_transaction?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right">
                      {month.revenue_growth !== 0 && (
                        <span className={`flex items-center justify-end gap-1 ${
                          month.revenue_growth >= 0 ? 'text-green-600' : 'text-red-500'
                        }`}>
                          {month.revenue_growth >= 0 ? 
                            <TrendingUp className="w-4 h-4" /> : 
                            <TrendingDown className="w-4 h-4" />
                          }
                          {Math.abs(month.revenue_growth)?.toFixed(1)}%
                        </span>
                      )}
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

// Need Cell import for conditional coloring
import { Cell } from "recharts";

// Category Performance Tab
const CategoryPerformance = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  const categories = data || [];

  return (
    <div className="space-y-6">
      {/* Category Revenue Chart */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Revenue by Category</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={categories.slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                type="number" 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <YAxis 
                type="category" 
                dataKey="category" 
                width={120}
                tick={{ fontSize: 11, fill: '#64748B' }}
              />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? `$${value?.toLocaleString()}` : value?.toLocaleString(),
                  name === 'revenue' ? 'Revenue' : name
                ]}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Bar dataKey="revenue" fill="#2563EB" radius={[0, 4, 4, 0]} name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Category Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Category Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Category</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Market Share</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Transactions</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Items Sold</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Transaction</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((cat, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Package className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium text-[#0F172A]">{cat.category}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right font-medium">${cat.revenue?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <Badge variant="secondary">{cat.market_share}%</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">{cat.transactions?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{cat.items_sold?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">${cat.avg_transaction?.toFixed(2)}</td>
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

// Country Performance Tab
const CountryPerformance = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  const countries = data || [];

  return (
    <div className="space-y-6">
      {/* Country Revenue Chart */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Revenue by Country</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={countries.slice(0, 15)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="country" 
                tick={{ fontSize: 10, fill: '#64748B', angle: -45, textAnchor: 'end' }}
                height={80}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? `$${value?.toLocaleString()}` : value?.toLocaleString(),
                  name === 'revenue' ? 'Revenue' : name
                ]}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Bar dataKey="revenue" fill="#2563EB" radius={[4, 4, 0, 0]} name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Country Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Country Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Country</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Revenue</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Market Share</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Customers</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Transactions</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Avg Transaction</th>
                </tr>
              </thead>
              <tbody>
                {countries.map((country, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium text-[#0F172A]">{country.country}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right font-medium">${country.revenue?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <Badge variant="secondary">{country.market_share}%</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">{country.unique_customers?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">{country.transactions?.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">${country.avg_transaction?.toFixed(2)}</td>
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
const Performance = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("monthly");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/performance`);
      setPerformanceData(res.data);
    } catch (err) {
      console.error("Error fetching performance data:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="performance-page">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="monthly" data-testid="tab-monthly">
            <Calendar className="w-4 h-4 mr-2" />
            Monthly
          </TabsTrigger>
          <TabsTrigger value="category" data-testid="tab-category">
            <Package className="w-4 h-4 mr-2" />
            Category
          </TabsTrigger>
          <TabsTrigger value="country" data-testid="tab-country">
            <Globe className="w-4 h-4 mr-2" />
            Country
          </TabsTrigger>
        </TabsList>

        <TabsContent value="monthly">
          <MonthlyPerformance data={performanceData?.monthly} loading={loading} />
        </TabsContent>

        <TabsContent value="category">
          <CategoryPerformance data={performanceData?.by_category} loading={loading} />
        </TabsContent>

        <TabsContent value="country">
          <CountryPerformance data={performanceData?.by_country} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Performance;
