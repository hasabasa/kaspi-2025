import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from "recharts";
import { Card } from "@/components/ui/card";
import { SalesData } from "@/types";
import { formatDateForChart, filterDataByDateRange, aggregateDataByTimeFrame } from "@/lib/salesUtils";
import { useIsMobile } from "@/hooks/use-mobile";

interface SalesChartProps {
  salesData: SalesData[];
  timeFrame: string;
  dateRange: {
    from?: Date;
    to?: Date;
  };
}

const SalesChart = ({ salesData, timeFrame, dateRange }: SalesChartProps) => {
  const isMobile = useIsMobile();
  const filteredData = filterDataByDateRange(salesData, dateRange);
  const aggregatedData = aggregateDataByTimeFrame(filteredData, timeFrame);

  return (
    <div className={`${isMobile ? 'h-[350px]' : 'h-[500px]'} p-2`}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={aggregatedData}
          margin={{
            top: 20,
            right: isMobile ? 15 : 30,
            left: 0,
            bottom: 10,
          }}
        >
          <defs>
            <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="50%" stopColor="#6366f1" stopOpacity={0.4}/>
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.1}/>
            </linearGradient>
            <linearGradient id="salesStroke" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1d4ed8" stopOpacity={1}/>
              <stop offset="100%" stopColor="#7c3aed" stopOpacity={1}/>
            </linearGradient>
          </defs>
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#e2e8f0" 
            strokeOpacity={0.6}
            vertical={false}
          />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => formatDateForChart(date, timeFrame)}
            fontSize={isMobile ? 11 : 13}
            interval={isMobile ? 'preserveStartEnd' : 'preserveStart'}
            stroke="#64748b"
            strokeWidth={1}
            tickLine={{ stroke: '#cbd5e1', strokeWidth: 1 }}
            axisLine={{ stroke: '#cbd5e1', strokeWidth: 1 }}
          />
          <YAxis hide />
          <Tooltip 
            labelFormatter={(date) => formatDateForChart(date, timeFrame)} 
            formatter={(value) => [`${value.toLocaleString()} ₸`, "Сумма"]}
            contentStyle={{
              fontSize: isMobile ? '13px' : '14px',
              padding: isMobile ? '10px' : '15px',
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15), 0 4px 10px rgba(0, 0, 0, 0.1)',
              backdropFilter: 'blur(10px)'
            }}
            labelStyle={{
              color: '#1e293b',
              fontWeight: '600',
              marginBottom: '4px'
            }}
          />
          <Area 
            type="monotone" 
            dataKey="amount" 
            stroke="url(#salesStroke)"
            fill="url(#salesGradient)"
            strokeWidth={isMobile ? 2.5 : 3}
            activeDot={{ 
              r: isMobile ? 6 : 8,
              fill: '#1d4ed8',
              stroke: '#ffffff',
              strokeWidth: 3,
              filter: 'drop-shadow(0 4px 8px rgba(29, 78, 216, 0.3))'
            }}
            dot={{
              fill: '#3b82f6',
              stroke: '#ffffff',
              strokeWidth: 2,
              r: isMobile ? 3 : 4
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SalesChart;
