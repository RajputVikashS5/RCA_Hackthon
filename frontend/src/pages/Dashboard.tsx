import React from 'react';
import StatCard from '../components/dashboard/StatCard';
import ChartCard from '../components/dashboard/ChartCard';
import TransactionList from '../components/dashboard/TransactionList';
import ReactECharts from 'echarts-for-react';

const Dashboard: React.FC = () => {
  const barData = [
    { name: 'Mon', income: 4000, expenses: 2400 },
    { name: 'Tue', income: 3000, expenses: 1398 },
    { name: 'Wed', income: 2000, expenses: 9800 },
    { name: 'Thu', income: 2780, expenses: 3908 },
    { name: 'Fri', income: 1890, expenses: 4800 },
    { name: 'Sat', income: 2390, expenses: 3800 },
    { name: 'Sun', income: 3490, expenses: 4300 },
  ];

  const pieData = [
    { name: 'Completed', value: 68 },
    { name: 'Pending', value: 16 },
    { name: 'Failed', value: 16 },
  ];
  const COLORS = ['#9bcc2b', '#10b981', '#f59e0b'];

  const recentIncidents = [
    { id: '1', title: 'Payment Gateway Timeout', date: 'Jul 12th 2024', status: 'Completed' as const, reference: 'INC-7821' },
    { id: '2', title: 'High CPU on Auth Service', date: 'Jul 12th 2024', status: 'Pending' as const, reference: 'INC-7822' },
    { id: '3', title: 'Database Connection Lost', date: 'Jul 12th 2024', status: 'Pending' as const, reference: 'INC-7823' },
    { id: '4', title: 'Frontend 500 Errors', date: 'Jul 12th 2024', status: 'Completed' as const, reference: 'INC-7824' },
    { id: '5', title: 'Missing User Avatars', date: 'Jul 12th 2024', status: 'Completed' as const, reference: 'INC-7825' },
  ];

  const barOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' }
    },
    grid: { left: 0, right: 0, bottom: 0, top: 0, containLabel: true },
    xAxis: {
      type: 'category',
      data: barData.map(d => d.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#9ca3af', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    series: [
      {
        name: 'Income',
        type: 'bar',
        data: barData.map(d => d.income),
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [4, 4, 0, 0] },
        itemStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#047857' }, { offset: 1, color: '#064e3b' }]
          }, 
          borderRadius: [4, 4, 0, 0] 
        },
        barWidth: 12
      },
      {
        name: 'Expenses',
        type: 'bar',
        data: barData.map(d => d.expenses),
        showBackground: true,
        backgroundStyle: { color: 'rgba(0,0,0,0.03)', borderRadius: [4, 4, 0, 0] },
        itemStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#059669' }]
          }, 
          borderRadius: [4, 4, 0, 0] 
        },
        barWidth: 12
      }
    ]
  };

  const pieOption = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: ['60%', '80%'],
        avoidLabelOverlap: false,
        label: { show: false },
        data: pieData.map((d, i) => ({
          value: d.value,
          name: d.name,
          itemStyle: { color: COLORS[i % COLORS.length] }
        }))
      }
    ]
  };

  return (
    <div style={{ display: 'flex', gap: '24px' }}>
      {/* Left Column */}
      <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div className="grid grid-cols-3">
          <StatCard 
            title="Analysis Usage"
            value="193.000"
            change="+35%"
            trend="up"
            trendText="from last month"
            date="Feb 12th 2024"
            isDark={true}
          />
          <StatCard 
            title="Total Incidents"
            value="193.000"
            change="+35%"
            trend="up"
            trendText="from last month"
            date="Feb 12th 2024"
          />
          <StatCard 
            title="Total Resolved"
            value="32.000"
            change="-24%"
            trend="down"
            trendText="from last month"
            date="Feb 12th 2024"
          />
        </div>

        <div className="grid grid-cols-2">
          <TransactionList transactions={recentIncidents} title="Recent Activity" />
          
          <ChartCard title="Incident Volume">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
              <div style={{ fontSize: '28px', fontWeight: '700', fontFamily: 'var(--font-display)' }}>193.000</div>
              <div className="stat-change" style={{ margin: 0 }}>
                <span className="trend-up">+35%</span>
                <span className="trend-text">from last month</span>
              </div>
            </div>
            <div style={{ flex: 1, minHeight: '200px' }}>
              <ReactECharts option={barOption} style={{ height: '100%', width: '100%' }} />
            </div>
          </ChartCard>
        </div>
      </div>

      {/* Right Column */}
      <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <ChartCard title="Resolution Performance">
          <div style={{ position: 'relative', height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ReactECharts option={pieOption} style={{ height: '100%', width: '100%' }} />
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Total Count</div>
              <div style={{ fontSize: '24px', fontWeight: '700' }}>565K</div>
            </div>
          </div>
          <div style={{ textAlign: 'center', fontSize: '13px', color: 'var(--muted)', margin: '16px 0' }}>
            Here are some tips on how to improve your score.
          </div>
          <button className="btn-secondary" style={{ width: '100%' }}>Guide Views</button>
        </ChartCard>
      </div>
    </div>
  );
};

export default Dashboard;
