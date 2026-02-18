import React, { useEffect, useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "";

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

        if (res.data.performance?.by_category) {
          const categories =
            res.data.performance.by_category
              .slice(0, 6)
              .map(cat => ({
                name: cat.category
                  ? cat.category.substring(0, 15)
                  : "Unknown",
                revenue: cat.revenue,
                transactions: cat.transactions
              }));

          setCategoryData(categories);
        }

        if (res.data.performance?.by_country) {
          const countries =
            res.data.performance.by_country
              .slice(0, 6)
              .map(c => ({
                name: c.country,
                revenue: c.revenue
              }));

          setCountryData(countries);
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

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Dashboard</h2>

      {kpis && (
        <div>
          <p>Total Revenue: {kpis.total_revenue}</p>
          <p>Total Transactions: {kpis.total_transactions}</p>
          <p>Average Order Value: {kpis.avg_order_value}</p>
        </div>
      )}

      <h3>Top Categories</h3>
      <ul>
        {categoryData.map((c, idx) => (
          <li key={idx}>
            {c.name} - Revenue: {c.revenue}
          </li>
        ))}
      </ul>

      <h3>Top Countries</h3>
      <ul>
        {countryData.map((c, idx) => (
          <li key={idx}>
            {c.name} - Revenue: {c.revenue}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
