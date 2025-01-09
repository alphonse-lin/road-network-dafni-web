<template>
    <div class="transportation-statistics-panel">
        <div class="panel-header">
            <h2>Transportation Simulation Report</h2>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <!-- 统计类型选择器 -->
            <div class="stats-header">
                <select v-model="selectedStatsType" class="stats-selector">
                    <option value="basic">Basic Statistics</option>
                    <option value="simulation">Simulation Results</option>
                </select>
            </div>

            <!-- 基础统计信息 -->
            <div v-if="selectedStatsType === 'basic'" class="basic-stats">
                <div class="stats-section">
                    <h3>Infrastructure Statistics</h3>
                    <p>Total Buildings: 2,345</p>
                    <p>Road Network Length: 156.7 km</p>
                </div>

                <div class="chart-container">
                    <h3>Land Use Distribution</h3>
                    <div ref="landUseChart" style="height: 300px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Vehicle Type Distribution</h3>
                    <div ref="vehicleChart" style="height: 300px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Age Structure</h3>
                    <div ref="ageChart" style="height: 300px;"></div>
                </div>
            </div>

            <!-- 模拟结果统计 -->
            <div v-if="selectedStatsType === 'simulation'" class="simulation-stats">
                <div class="simulation-info">
                    <h3>Simulation Parameters</h3>
                    <p>Duration: 30 hours</p>
                    <p>Total Agents: 10,000</p>
                </div>

                <div class="chart-container">
                    <h3>Convergence Analysis</h3>
                    <div ref="convergenceChart" style="height: 250px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Original Traffic Flow</h3>
                    <div ref="normalTrafficChart" style="height: 250px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Traffic Flow During Rain</h3>
                    <div ref="rainTrafficChart" style="height: 250px;"></div>
                </div>

                <div class="legend">
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #FF4D4F;"></span>
                        <span>departures</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #4096FF;"></span>
                        <span>arrivals</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: #52C41A;"></span>
                        <span>en-route</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const selectedStatsType = ref('basic')

// 图表引用
const landUseChart = ref(null)
const vehicleChart = ref(null)
const ageChart = ref(null)
const convergenceChart = ref(null)
const normalTrafficChart = ref(null)
const rainTrafficChart = ref(null)

// 初始化饼图
const initPieChart = (chartRef, data, title) => {
    console.log(title)
    const chart = echarts.init(chartRef)
    chart.setOption({
        tooltip: {
            trigger: 'item'
        },
        series: [{
            type: 'pie',
            radius: '70%',
            data: data,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    })
}

// 初始化交通流量图
const initTrafficChart = (chartRef, data) => {
    const chart = echarts.init(chartRef)
    chart.setOption({
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: Array.from({length: 30}, (_, i) => i),
            name: 'Time(hours)'
        },
        yAxis: {
            type: 'value',
            name: 'Number of People'
        },
        series: [
            {
                name: 'departures',
                type: 'line',
                data: data.departures,
                itemStyle: { color: '#FF4D4F' }
            },
            {
                name: 'arrivals',
                type: 'line',
                data: data.arrivals,
                itemStyle: { color: '#4096FF' }
            },
            {
                name: 'en-route',
                type: 'line',
                data: data.enRoute,
                itemStyle: { color: '#52C41A' }
            }
        ]
    })
}

// 生成模拟数据
const generateTrafficData = () => {
    return {
        departures: Array.from({length: 30}, () => Math.floor(Math.random() * 400)),
        arrivals: Array.from({length: 30}, () => Math.floor(Math.random() * 400)),
        enRoute: Array.from({length: 30}, () => Math.floor(Math.random() * 400))
    }
}

// 添加收敛分析图表的初始化函数
const initConvergenceChart = (chartRef) => {
    const chart = echarts.init(chartRef)
    chart.setOption({
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: Array.from({length: 10}, (_, i) => `Iteration ${i+1}`),
            name: 'Iteration'
        },
        yAxis: {
            type: 'value',
            name: 'Score'
        },
        series: [{
            data: Array.from({length: 10}, () => Math.random() * 100),
            type: 'line',
            smooth: true
        }]
    })
}

// 修改初始化图表的函数
const initCharts = async () => {
    await nextTick()  // 等待 DOM 更新
    
    if (selectedStatsType.value === 'basic') {
        if (landUseChart.value) {
            initPieChart(landUseChart.value, [
                { value: 35, name: 'Residential' },
                { value: 25, name: 'Commercial' },
                { value: 20, name: 'Industrial' },
                { value: 15, name: 'Green Space' },
                { value: 5, name: 'Others' }
            ])
        }
        
        if (vehicleChart.value) {
            initPieChart(vehicleChart.value, [
                { value: 60, name: 'Private Cars' },
                { value: 20, name: 'Public Transit' },
                { value: 15, name: 'Bicycles' },
                { value: 5, name: 'Others' }
            ])
        }
        
        if (ageChart.value) {
            initPieChart(ageChart.value, [
                { value: 15, name: '0-14' },
                { value: 25, name: '15-29' },
                { value: 35, name: '30-44' },
                { value: 15, name: '45-59' },
                { value: 10, name: '60+' }
            ])
        }
    } else {
        if (convergenceChart.value) {
            initConvergenceChart(convergenceChart.value)
        }
        if (normalTrafficChart.value) {
            initTrafficChart(normalTrafficChart.value, generateTrafficData())
        }
        if (rainTrafficChart.value) {
            initTrafficChart(rainTrafficChart.value, generateTrafficData())
        }
    }
}

// 修改 watch
watch(selectedStatsType, async () => {
    await initCharts()
})

// 修改 onMounted
onMounted(async () => {
    await initCharts()
    window.addEventListener('resize', handleResize)
})

// 清理事件监听
onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
})

// 处理窗口大小变化
const handleResize = () => {
    const charts = [
        landUseChart.value, 
        vehicleChart.value, 
        ageChart.value,
        convergenceChart.value,
        normalTrafficChart.value,
        rainTrafficChart.value
    ]
    
    charts.forEach(chart => {
        if (chart) {
            const echartInstance = echarts.getInstanceByDom(chart)
            if (echartInstance) {
                echartInstance.resize()
            }
        }
    })
}

defineEmits(['close'])
</script>

<style scoped>
.transportation-statistics-panel {
    position: fixed;
    right: 20px;
    top: 80px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 20px;
    width: 500px;
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
    font-size: 20px;
    color: #333;
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

.stats-header {
    margin-bottom: 20px;
}

.stats-selector {
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
}

.chart-container {
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

h3 {
    margin: 0 0 15px;
    font-size: 16px;
    color: #333;
}

.simulation-info {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.simulation-info p {
    margin: 5px 0;
    color: #666;
}

.legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 20px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.legend-color {
    width: 20px;
    height: 10px;
    border-radius: 2px;
}
</style> 