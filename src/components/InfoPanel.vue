<template>
    <div class="info-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King’sCross to Farringdon(25km²)</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <!-- 图片部分 -->
            <div class="image-section">
                <img src="@/assets/main-home.jpg" alt="Holborn Bridge" />
            </div>

            <!-- 拥堵率趋势图 -->
            <div class="chart-section">
                <h4>Congestion Rate Trend</h4>
                <div id="congestionChart" style="width: 100%; height: 200px;"></div>
            </div>

            <!-- 拥堵记录表格 -->
            <div class="table-section">
                <h4>Severe Congestion Records</h4>
                <div class="congestion-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Congestion Rate</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="record in congestionRecords" :key="record.id">
                                <td>{{ record.date }}</td>
                                <td>{{ record.time }}</td>
                                <td>{{ record.rate }}%</td>
                                <td :class="record.status.toLowerCase()">{{ record.status }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
    name: 'InfoPanel',
    data() {
        return {
            congestionRecords: [
                { id: 1, date: '2023-12-01', time: '08:30', rate: 85, status: 'Severe' },
                { id: 2, date: '2023-12-01', time: '17:30', rate: 78, status: 'High' },
                { id: 3, date: '2023-12-02', time: '09:00', rate: 82, status: 'Severe' },
                // 可以添加更多记录
            ]
        }
    },
    mounted() {
        this.initCongestionChart()
    },
    methods: {
        initCongestionChart() {
            const chart = echarts.init(document.getElementById('congestionChart'))
            chart.setOption({
                grid: {
                    top: 30,
                    right: 20,
                    bottom: 30,
                    left: 50
                },
                xAxis: {
                    type: 'category',
                    data: ['2016', '2017', '2018', '2019', '2020'],
                    axisLabel: {
                        color: '#666'
                    }
                },
                yAxis: {
                    type: 'value',
                    min: 0,
                    max: 100,
                    axisLabel: {
                        formatter: '{value}%',
                        color: '#666'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: '{b}: {c}%'
                },
                series: [{
                    data: [30, 35, 45, 40, 35],
                    type: 'line',
                    smooth: true,
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                            offset: 0,
                            color: 'rgba(58,177,255,0.5)'
                        }, {
                            offset: 1,
                            color: 'rgba(58,177,255,0.1)'
                        }])
                    },
                    lineStyle: {
                        color: '#3AB1FF'
                    },
                    itemStyle: {
                        color: '#3AB1FF'
                    }
                }]
            })

            // 监听窗口大小变化
            window.addEventListener('resize', () => {
                chart.resize()
            })
        }
    }
}
</script>

<style scoped>
.info-panel {
    position: fixed;
    left: 20px;
    top: 80px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 20px;
    width: 400px;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 1000;
}

.panel-header {
    position: relative;
    margin-bottom: 20px;
}

.panel-header h2 {
    margin: 0;
    font-size: 24px;
    color: #333;
    text-align: center;
}

.panel-header h3 {
    margin: 5px 0 0;
    font-size: 16px;
    color: #666;
    font-weight: normal;
    text-align: center;
}

.close-btn {
    position: absolute;
    top: 0;
    right: 0;
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 5px;
}

.image-section {
    margin-bottom: 20px;
}

.image-section img {
    width: 100%;
    border-radius: 8px;
}

.chart-section {
    margin-bottom: 20px;
}

.chart-section h4,
.table-section h4 {
    margin: 0 0 10px;
    color: #333;
    text-align: center;
}

.congestion-table {
    width: 100%;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #f5f5f5;
    color: #333;
}

td {
    color: #666;
}

.severe {
    color: #ff4d4f;
}

.high {
    color: #faad14;
}

.normal {
    color: #52c41a;
}
</style> 