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
  Area,
  AreaChart,
  ComposedChart
} from "recharts";
import { TrendingUp, Calendar, BarChart3, Sparkles } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const COLORS = {
  historical: "#64748B",
  forecast: "#2563EB",
  trend: "#10B981",
  smoothed: "#8B5CF6"
};

// Summary Card
const ForecastCard = ({ title, value, subtitle, color = "#2563EB" }) => (
  <Card className="bg-white border-border shadow-sm">
    <CardContent className="p-6">
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
      <h3 className="text-2xl font-bold mt-1" style={{ color }}>{value}</h3>
      {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
    </CardContent>
  </Card>
);

// Linear Trend Tab
const LinearTrendForecast = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-[500px]" />;
  }

  const forecast = data?.forecasts?.linear_trend || {};
  const historical = forecast.historical || [];
  const predictions = forecast.forecast || [];
  const params = forecast.parameters || {};

  // Combine data for chart
  const chartData = [
    ...historical.map(h => ({
      date: h.date,
      revenue: h.revenue,
      trend: h.trend,
      type: 'historical'
    })),
    ...predictions.map(p => ({
      date: p.date,
      forecast: p.revenue,
      type: 'forecast'
    }))
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <ForecastCard
          title="Total Forecast"
          value={`$${forecast.total_forecasted_revenue?.toLocaleString() || 0}`}
          subtitle="Next 6 months"
          color="#2563EB"
        />
        <ForecastCard
          title="Monthly Slope"
          value={`$${params.slope?.toLocaleString() || 0}`}
          subtitle="Per period"
          color={params.slope >= 0 ? "#10B981" : "#EF4444"}
        />
        <ForecastCard
          title="R² Score"
          value={params.r_squared?.toFixed(3) || 0}
          subtitle="Model fit"
          color="#8B5CF6"
        />
        <ForecastCard
          title="Forecast Periods"
          value="6"
          subtitle="Months ahead"
          color="#06B6D4"
        />
      </div>

      {/* Main Chart */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Linear Trend Forecast</CardTitle>
          <CardDescription>Historical data with linear regression trend line and future predictions</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={450}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 10, fill: '#64748B' }}
                tickFormatter={(val) => val?.substring(5, 7) || ''}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value, name) => [`$${value?.toLocaleString()}`, name]}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke={COLORS.historical} 
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Historical"
              />
              <Line 
                type="monotone" 
                dataKey="trend" 
                stroke={COLORS.trend} 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Trend Line"
              />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                stroke={COLORS.forecast} 
                strokeWidth={3}
                dot={{ r: 5, fill: COLORS.forecast }}
                name="Forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Forecast Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Forecast Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">Period</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">Forecasted Revenue</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred, index) => (
                  <tr key={index} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 font-medium">{pred.date}</td>
                    <td className="py-3 px-4 text-right font-bold text-[#2563EB]">${pred.revenue?.toLocaleString()}</td>
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

// Moving Average Tab
const MovingAverageForecast = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-[500px]" />;
  }

  const forecast = data?.forecasts?.moving_average || {};
  const historical = forecast.historical || [];
  const predictions = forecast.forecast || [];

  const chartData = [
    ...historical.slice(-12).map(h => ({
      date: h.date,
      revenue: h.revenue,
      type: 'historical'
    })),
    ...predictions.map(p => ({
      date: p.date,
      forecast: p.revenue,
      type: 'forecast'
    }))
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ForecastCard
          title="Total Forecast"
          value={`$${forecast.total_forecasted_revenue?.toLocaleString() || 0}`}
          subtitle="Next 6 months"
          color="#2563EB"
        />
        <ForecastCard
          title="Method"
          value="3-Period MA"
          subtitle="Moving Average"
          color="#06B6D4"
        />
        <ForecastCard
          title="Monthly Average"
          value={`$${Math.round(forecast.total_forecasted_revenue / 6)?.toLocaleString() || 0}`}
          subtitle="Per month"
          color="#8B5CF6"
        />
      </div>

      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Moving Average Forecast</CardTitle>
          <CardDescription>3-period moving average with flat forecast projection</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 10, fill: '#64748B' }}
                tickFormatter={(val) => val?.substring(5) || ''}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value) => [`$${value?.toLocaleString()}`, 'Revenue']}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke={COLORS.historical}
                fill="transparent"
                strokeWidth={2}
                name="Historical"
              />
              <Area
                type="monotone"
                dataKey="forecast"
                stroke={COLORS.forecast}
                fillOpacity={1}
                fill="url(#colorForecast)"
                strokeWidth={2}
                name="Forecast"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

// Exponential Smoothing Tab
const ExponentialSmoothingForecast = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-[500px]" />;
  }

  const forecast = data?.forecasts?.exponential_smoothing || {};
  const historical = forecast.historical || [];
  const predictions = forecast.forecast || [];
  const params = forecast.parameters || {};

  const chartData = [
    ...historical.slice(-12).map(h => ({
      date: h.date,
      revenue: h.revenue,
      smoothed: h.smoothed,
      type: 'historical'
    })),
    ...predictions.map(p => ({
      date: p.date,
      forecast: p.revenue,
      type: 'forecast'
    }))
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ForecastCard
          title="Total Forecast"
          value={`$${forecast.total_forecasted_revenue?.toLocaleString() || 0}`}
          subtitle="Next 6 months"
          color="#2563EB"
        />
        <ForecastCard
          title="Alpha (α)"
          value={params.alpha || 0}
          subtitle="Smoothing factor"
          color="#8B5CF6"
        />
        <ForecastCard
          title="Monthly Average"
          value={`$${Math.round(forecast.total_forecasted_revenue / 6)?.toLocaleString() || 0}`}
          subtitle="Per month"
          color="#10B981"
        />
      </div>

      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Exponential Smoothing Forecast</CardTitle>
          <CardDescription>Simple exponential smoothing with α={params.alpha}</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 10, fill: '#64748B' }}
                tickFormatter={(val) => val?.substring(5) || ''}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`}
              />
              <Tooltip 
                formatter={(value) => [`$${value?.toLocaleString()}`, '']}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke={COLORS.historical} 
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Historical"
              />
              <Line 
                type="monotone" 
                dataKey="smoothed" 
                stroke={COLORS.smoothed} 
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={false}
                name="Smoothed"
              />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                stroke={COLORS.forecast} 
                strokeWidth={3}
                dot={{ r: 5, fill: COLORS.forecast }}
                name="Forecast"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

// Seasonal Analysis Tab
const SeasonalAnalysis = ({ data, loading }) => {
  if (loading || !data) {
    return <Skeleton className="h-[500px]" />;
  }

  const seasonal = data?.seasonal_analysis || {};
  const indices = seasonal.seasonal_indices || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ForecastCard
          title="Peak Month"
          value={seasonal.peak_month || '-'}
          subtitle="Highest sales"
          color="#10B981"
        />
        <ForecastCard
          title="Low Month"
          value={seasonal.low_month || '-'}
          subtitle="Lowest sales"
          color="#EF4444"
        />
        <ForecastCard
          title="Seasonality Strength"
          value={seasonal.seasonality_strength?.toFixed(3) || 0}
          subtitle="Variation index"
          color="#8B5CF6"
        />
      </div>

      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Seasonal Indices by Month</CardTitle>
          <CardDescription>Values above 1.0 indicate above-average sales periods</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={indices}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis 
                dataKey="month_name" 
                tick={{ fontSize: 12, fill: '#64748B' }}
              />
              <YAxis 
                tick={{ fontSize: 12, fill: '#64748B' }}
                domain={[0, 'auto']}
              />
              <Tooltip 
                formatter={(value) => [value?.toFixed(3), 'Seasonal Index']}
                contentStyle={{ background: '#fff', border: '1px solid #E2E8F0', borderRadius: '8px' }}
              />
              <Bar 
                dataKey="seasonal_index" 
                radius={[4, 4, 0, 0]}
                name="Seasonal Index"
              >
                {indices.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.seasonal_index >= 1 ? '#10B981' : '#F59E0B'} 
                  />
                ))}
              </Bar>
              {/* Reference line at 1.0 */}
              <ReferenceLine y={1} stroke="#64748B" strokeDasharray="3 3" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Seasonal Data Table */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Monthly Seasonal Factors</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {indices.map((item, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg text-center ${
                  item.seasonal_index >= 1 ? 'bg-green-50' : 'bg-amber-50'
                }`}
              >
                <p className="text-sm font-medium text-muted-foreground">{item.month_name}</p>
                <p className={`text-xl font-bold ${
                  item.seasonal_index >= 1 ? 'text-green-600' : 'text-amber-600'
                }`}>
                  {item.seasonal_index?.toFixed(2)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  ${item.avg_revenue?.toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

import { Cell, ReferenceLine } from "recharts";

// Main Component
const Forecasting = () => {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("linear");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/forecast`);
      setForecastData(res.data);
    } catch (err) {
      console.error("Error fetching forecast data:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="forecasting-page">
      {/* Comparison Summary */}
      {forecastData?.comparison && (
        <Card className="bg-white border-border shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              Forecast Comparison Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-muted-foreground">Average Forecast</p>
                <p className="text-2xl font-bold text-[#2563EB]">
                  ${forecastData.comparison.forecast_summary?.average_forecast?.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-muted-foreground">Optimistic Forecast</p>
                <p className="text-2xl font-bold text-green-600">
                  ${forecastData.comparison.forecast_summary?.max_forecast?.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-amber-50 rounded-lg">
                <p className="text-sm font-medium text-muted-foreground">Conservative Forecast</p>
                <p className="text-2xl font-bold text-amber-600">
                  ${forecastData.comparison.forecast_summary?.min_forecast?.toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="linear" data-testid="tab-linear">
            <TrendingUp className="w-4 h-4 mr-2" />
            Linear Trend
          </TabsTrigger>
          <TabsTrigger value="ma" data-testid="tab-ma">
            <BarChart3 className="w-4 h-4 mr-2" />
            Moving Average
          </TabsTrigger>
          <TabsTrigger value="exp" data-testid="tab-exp">
            <Sparkles className="w-4 h-4 mr-2" />
            Exp. Smoothing
          </TabsTrigger>
          <TabsTrigger value="seasonal" data-testid="tab-seasonal">
            <Calendar className="w-4 h-4 mr-2" />
            Seasonal
          </TabsTrigger>
        </TabsList>

        <TabsContent value="linear">
          <LinearTrendForecast data={forecastData} loading={loading} />
        </TabsContent>

        <TabsContent value="ma">
          <MovingAverageForecast data={forecastData} loading={loading} />
        </TabsContent>

        <TabsContent value="exp">
          <ExponentialSmoothingForecast data={forecastData} loading={loading} />
        </TabsContent>

        <TabsContent value="seasonal">
          <SeasonalAnalysis data={forecastData} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Forecasting;
