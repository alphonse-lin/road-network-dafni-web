<template>
    <div class="index-statistics-panel">
        <div class="panel-header">
            <h2>Index Analysis Results</h2>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>

        <div class="panel-content">
            <!-- 基础信息 -->
            <div class="basic-info">
                <h3>Basic Information</h3>
                <div class="info-item">
                    <p>Total Road Segments: 2,345</p>
                    <p>Calculation Interval: 100</p>
                    <p>Time Period: 0:00 - 24:00</p>
                </div>
            </div>

            <!-- 详细统计信息部分 -->
            <div class="detailed-stats-section">
                <h3>Detailed Statistics</h3>
                <div class="stats-selector">
                    <el-select 
                        v-model="selectedCalculationType" 
                        placeholder="Select Calculation Type"
                        @change="handleCalculationTypeChange"
                    >
                        <el-option label="Vulnerability Calculation" value="vulnerability" />
                        <el-option label="Risk Index Calculation" value="risk" />
                    </el-select>
                </div>

                <!-- 统计信息内容 -->
                <div class="calculation-stats">
                    <!-- 脆弱性指数统计 -->
                    <template v-if="selectedCalculationType === 'vulnerability'">
                        <div class="description-section">
                            <h4>Description of Vulnerability Index</h4>
                            <div class="image-container" @click="showLargeImage = true">
                                <img :src="vulnerabilityDescImg" alt="Vulnerability Description" />
                                <span class="zoom-hint">Click to zoom</span>
                            </div>
                        </div>

                        <div class="chart-section">
                            <h4>Network Structure Statistics</h4>
                            <div ref="scatterChart" class="chart"></div>
                            <div ref="histogramChart" class="chart"></div>
                        </div>
                    </template>

                    <!-- 风险指数统计 -->
                    <template v-if="selectedCalculationType === 'risk'">
                        <div class="description-section">
                            <h4>Description of Risk Index</h4>
                            <div class="image-container" @click="showLargeImage = true">
                                <img :src="riskDescImg" alt="Risk Description" />
                                <span class="zoom-hint">Click to zoom</span>
                            </div>
                        </div>

                        <div class="chart-section">
                            <h4>Risk Level Distribution Over Time</h4>
                            <div ref="lineChart" class="chart"></div>
                            
                            <h4>Risk Level Distribution</h4>
                            <div ref="barChart" class="chart"></div>
                            <el-slider 
                                v-model="timeStep" 
                                :min="0" 
                                :max="24" 
                                :step="1"
                                @change="updateBarChart"
                            />
                            <div class="time-label">Time: {{ timeStep }}:00</div>
                        </div>
                    </template>
                </div>
            </div>
        </div>

        <!-- 图片放大弹窗 -->
        <el-dialog
            v-model="showLargeImage"
            width="80%"
            :show-close="true"
            :modal="true"
        >
            <img 
                :src="selectedCalculationType === 'vulnerability' ? vulnerabilityDescImg : riskDescImg" 
                style="width: 100%"
            />
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElSelect, ElOption, ElSlider, ElDialog } from 'element-plus'
import vulnerabilityDesc from '@/assets/index_3.jpg'
import riskDesc from '@/assets/index_4.jpg'

const props = defineProps({
    analysisType: {
        type: String,
        required: true,
        validator: (value) => ['vulnerability', 'risk'].includes(value)
    }
})

const selectedCalculationType = ref('vulnerability')
const showLargeImage = ref(false)
const timeStep = ref(0)

// 图表引用
const scatterChart = ref(null)
const histogramChart = ref(null)
const lineChart = ref(null)
const barChart = ref(null)

// 在 setup 中定义图片引用
const vulnerabilityDescImg = ref(vulnerabilityDesc)
const riskDescImg = ref(riskDesc)

// 存储图表实例的引用
const charts = ref({})

// // 重置图表大小
// const resizeCharts = () => {
//     Object.values(charts.value).forEach(chart => {
//         if (chart) {
//             chart.resize()
//         }
//     })
// }

// // 清理函数
// const disposeCharts = () => {
//     Object.values(charts.value).forEach(chart => {
//         if (chart) {
//             chart.dispose()
//         }
//     })
// }

// 初始化图表的通用函数
const initChart = (el, options) => {
    if (!el) return null
    const chart = echarts.init(el, null, {
        renderer: 'canvas',
        useDirtyRect: false
    })
    chart.setOption(options)
    return chart
}

// 处理计算类型变化
const handleCalculationTypeChange = async (newType) => {
    // 先清理现有图表
    Object.values(charts.value).forEach(chart => {
        if (chart) {
            chart.dispose()
        }
    })
    charts.value = {}

    // 等待 DOM 更新
    await nextTick()

    // 初始化新的图表
    if (newType === 'vulnerability') {
        await initVulnerabilityCharts()
    } else {
        await initRiskCharts()
    }
}

// 初始化脆弱性分析图表
const initVulnerabilityCharts = async () => {
    await nextTick()
    
    if (scatterChart.value) {
        charts.value.scatter = initChart(scatterChart.value, {
            title: { text: 'Vulnerability Distribution' },
            xAxis: { type: 'value' },
            yAxis: { type: 'value' },
            series: [{
                type: 'scatter',
                data: Array.from({ length: 100 }, () => ([
                    Math.random() * 100,
                    Math.random() * 100
                ]))
            }]
        })
    }

    if (histogramChart.value) {
        charts.value.histogram = initChart(histogramChart.value, {
            title: { text: 'Vulnerability Histogram' },
            xAxis: { type: 'category' },
            yAxis: { type: 'value' },
            series: [{
                type: 'bar',
                data: Array.from({ length: 50 }, () => Math.random() * 100)
            }]
        })
    }
}

// 生成时间数据
const generateTimeLabels = () => {
    const startTime = 7.5 * 60; // 7:30 in minutes
    const endTime = 9 * 60;     // 9:00 in minutes
    const interval = (endTime - startTime) / 100; // 分成100份
    
    return Array.from({ length: 100 }, (_, i) => {
        const minutes = startTime + (i * interval);
        const hours = Math.floor(minutes / 60);
        const mins = Math.floor(minutes % 60);
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    });
}

// 初始化风险分析图表
const initRiskCharts = async () => {
    await nextTick()
    
    if (lineChart.value) {
        const timeLabels = generateTimeLabels();
        charts.value.line = initChart(lineChart.value, {
            title: { 
                text: 'Risk Level Trends',
                left: 'center'
            },
            legend: {
                data: ['Lowest', 'Low', 'High', 'Highest'],
                top: 30
            },
            grid: {
                top: 80,
                left: 50,
                right: 30,
                bottom: 60
            },
            xAxis: {
                type: 'category',
                data: timeLabels,
                axisLabel: {
                    rotate: 45,
                    interval: 9  // 显示每第10个标签
                }
            },
            yAxis: { 
                type: 'value',
                min: 0,
                max: 100
            },
            series: ['Lowest', 'Low', 'High', 'Highest'].map(level => ({
                name: level,
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                data: Array.from({ length: 100 }, () => Math.round(Math.random() * 100))
            }))
        })
    }

    await updateBarChart()
}

// 更新柱状图
const updateBarChart = async () => {
    await nextTick()
    if (!barChart.value) return
    
    const categories = ['Lowest', 'Low', 'High', 'Highest']
    
    if (!charts.value.bar) {
        charts.value.bar = initChart(barChart.value, {
            title: { 
                text: `Risk Distribution at ${timeStep.value}:00`,
                left: 'center'
            },
            grid: {
                top: 60,
                left: 50,
                right: 30,
                bottom: 30
            },
            xAxis: {
                type: 'category',
                data: categories
            },
            yAxis: { 
                type: 'value',
                min: 0,
                max: 100
            },
            series: [{
                type: 'bar',
                data: categories.map(() => Math.round(Math.random() * 100))
            }]
        })
    } else {
        charts.value.bar.setOption({
            title: { text: `Risk Distribution at ${timeStep.value}:00` },
            series: [{
                data: categories.map(() => Math.round(Math.random() * 100))
            }]
        })
    }
}

// 处理窗口大小变化
const handleResize = () => {
    Object.values(charts.value).forEach(chart => {
        if (chart) {
            chart.resize()
        }
    })
}

// 组件挂载时
onMounted(async () => {
    window.addEventListener('resize', handleResize)
    await handleCalculationTypeChange(selectedCalculationType.value)
})

// 组件卸载时
onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    Object.values(charts.value).forEach(chart => {
        if (chart) {
            chart.dispose()
        }
    })
})

// 监听统计类型变化
watch(selectedCalculationType, async (newValue) => {
    if (newValue === 'detailed') {
        await nextTick()
        if (props.analysisType === 'vulnerability') {
            await initVulnerabilityCharts()
        } else {
            await initRiskCharts()
        }
    }
})

defineEmits(['close'])
</script>

<style scoped>
.index-statistics-panel {
    position: fixed;
    right: 20px;
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

.basic-info, .detailed-stats-section {
    margin-bottom: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

h3 {
    margin: 0 0 15px;
    font-size: 18px;
    color: #333;
}

h4 {
    margin: 10px 0;
    font-size: 16px;
    color: #444;
}

.info-item p {
    margin: 5px 0;
    color: #666;
}

.stats-selector {
    margin: 15px 0;
}

.chart-section {
    margin-top: 20px;
}

.chart {
    margin-bottom: 20px;
    padding: 10px;
    background: white;
    border-radius: 6px;
    height: 300px;
}

.description-section {
    background: white;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 20px;
}

.image-container {
    position: relative;
    width: 100%;
}

.image-container img {
    width: 100%;
    border-radius: 4px;
}

.zoom-hint {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

:deep(.el-select) {
    width: 100%;
}

.time-label {
    text-align: center;
    color: #666;
    margin-top: 5px;
}
</style> 