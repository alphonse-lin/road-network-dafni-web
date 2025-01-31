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
                    <p>Total Road Segments: {{ statistics.totalSegments }}</p>
                    <p>Calculation Interval: {{ timeInterval }}s</p>
                    <p>Time Period: {{ statistics.timePeriodHours }} hours</p>
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
                            <el-select 
                                v-model="selectedTimeStep" 
                                placeholder="Select Time Step"
                                @change="updateVulnerabilityCharts"
                                style="margin-bottom: 20px; width: 100%;"
                            >
                                <el-option 
                                    v-for="step in timeSteps" 
                                    :key="step"
                                    :label="`Time: ${step}-${step + props.timeInterval}s`"
                                    :value="step"
                                />
                            </el-select>
                            
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
                            <h4>Risk Level Distribution</h4>
                            <el-select 
                                v-model="selectedRiskTimeStep" 
                                placeholder="Select Time Step"
                                @change="updateRiskCharts"
                                style="margin-bottom: 20px; width: 100%;"
                            >
                                <el-option 
                                    v-for="step in timeSteps" 
                                    :key="step"
                                    :label="`Time: ${step}-${step + props.timeInterval}s`"
                                    :value="step"
                                />
                            </el-select>
                            
                            <div ref="pieChart" class="chart"></div>
                            
                            <h4>Risk Level Trends</h4>
                            <div ref="trendChart" class="chart"></div>
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
import { ElSelect, ElOption, ElDialog } from 'element-plus'
import vulnerabilityDesc from '@/assets/index_3.jpg'
import riskDesc from '@/assets/index_4.jpg'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
    projectId: {
        type: String,
        required: true
    },
    timeInterval: {
        type: Number,
        default: 450
    }
})

const selectedCalculationType = ref('vulnerability')
const showLargeImage = ref(false)

// 图表引用
const scatterChart = ref(null)
const histogramChart = ref(null)
const pieChart = ref(null)
const trendChart = ref(null)

// 图片引用
const vulnerabilityDescImg = ref(vulnerabilityDesc)
const riskDescImg = ref(riskDesc)

// 图表实例引用
const charts = ref({})

const statistics = ref({
    totalSegments: 0,
    timePeriodHours: 0
})

// 响应式变量
const selectedTimeStep = ref(0)
const timeSteps = ref([])
const vulnerabilityData = ref([])
const selectedRiskTimeStep = ref(0)

// 重置图表大小
const resizeCharts = () => {
    Object.values(charts.value).forEach(chart => {
        if (chart) {
            chart.resize()
        }
    })
}

// 清理函数
const disposeCharts = () => {
    Object.values(charts.value).forEach(chart => {
        if (chart) {
            chart.dispose()
        }
    })
}

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
    disposeCharts()
    
    await nextTick()
    if (newType === 'vulnerability') {
        await initVulnerabilityCharts()
    } else {
        await initRiskCharts()
    }
}

// 初始化脆弱性分析图表
const initVulnerabilityCharts = async () => {
    await nextTick()
    await updateVulnerabilityCharts(selectedTimeStep.value)
}

// 新增更新脆弱性图表函数
const updateVulnerabilityCharts = async (timeStep) => {
    // 获取当前时间步长的脆弱性数据，并过滤掉0值
    const vulColumn = `vulnerability_${timeStep}`
    const validData = vulnerabilityData.value
        .filter(row => !isNaN(parseFloat(row[vulColumn])))
        .map(row => parseFloat(row[vulColumn]))
        .filter(value => value !== 0)  // 过滤掉0值

    // 更新散点图 - 散点图保持显示所有数据，包括0值
    if (scatterChart.value) {
        const allData = vulnerabilityData.value
            .filter(row => !isNaN(parseFloat(row[vulColumn])))
            .map(row => parseFloat(row[vulColumn]))
        const scatterData = allData.map((value, index) => [index, value])
        
        charts.value.scatter = initChart(scatterChart.value, {
            title: { 
                text: `Vulnerability Distribution`,
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    return `Index: ${params.data[0]}<br/>Value: ${params.data[1].toFixed(4)}`
                }
            },
            grid: {
                top: 60,
                left: 50,
                right: 30,
                bottom: 40
            },
            xAxis: { 
                type: 'value',
                name: 'Road Segment Index'
            },
            yAxis: { 
                type: 'value',
                name: 'Vulnerability Value'
            },
            series: [{
                type: 'scatter',
                data: scatterData,
                symbolSize: 8
            }]
        })
    }

    // 更新直方图
    if (histogramChart.value) {
        const binCount = 20
        const min = Math.min(...validData)
        const max = Math.max(...validData)
        const binWidth = (max - min) / binCount

        const bins = Array(binCount).fill(0)
        validData.forEach(value => {
            const binIndex = Math.min(
                Math.floor((value - min) / binWidth),
                binCount - 1
            )
            bins[binIndex]++
        })

        // 简化标签显示
        const binLabels = Array(binCount).fill(0).map((_, i) => {
            const start = min + i * binWidth
            const end = min + (i + 1) * binWidth
            // 使用toFixed(2)限制小数位数
            // return `${start.toExponential(2)}-${end.toExponential(2)}`
            // 或者使用普通数字格式：
            return `${start.toFixed(2)}-${end.toFixed(2)}`
        })

        charts.value.histogram = initChart(histogramChart.value, {
            title: { 
                text: `Vulnerability Histogram`,
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    const range = params.name.split('-')
                    // 在tooltip中可以显示更精确的值
                    return `Range: ${range[0]} - ${range[1]}<br/>Count: ${params.value}`
                }
            },
            grid: {
                top: 60,
                left: 50,
                right: 30,
                bottom: 80
            },
            xAxis: { 
                type: 'category',
                data: binLabels,
                axisLabel: {
                    rotate: 45,
                    interval: 1,
                    fontSize: 10  // 减小字体大小
                },
                name: 'Vulnerability Range'
            },
            yAxis: { 
                type: 'value',
                name: 'Count'
            },
            series: [{
                type: 'bar',
                data: bins,
                itemStyle: {
                    color: '#5470c6'
                }
            }]
        })
    }
}

// 生成时间数据
// const generateTimeLabels = () => {
//     const startTime = 7.5 * 60; // 7:30 in minutes
//     const endTime = 9 * 60;     // 9:00 in minutes
//     const interval = (endTime - startTime) / 100; // 分成100份
    
//     return Array.from({ length: 100 }, (_, i) => {
//         const minutes = startTime + (i * interval);
//         const hours = Math.floor(minutes / 60);
//         const mins = Math.floor(minutes % 60);
//         return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
//     });
// }

// 更新风险图表
const updateRiskCharts = async (timeStep) => {
    // 先清理现有图表
    if (charts.value.pie) {
        charts.value.pie.dispose()
    }
    if (charts.value.trend) {
        charts.value.trend.dispose()
    }
    
    const riskColumn = `risk_level_${timeStep}`
    
    // 只保留需要的风险等级
    const riskLevelMap = {
        'lowest': 'Lowest Risk',
        'low_risk': 'Low Risk',
        'high_risk': 'High Risk',
        'highest_risk': 'Highest Risk'
    }
    
    // 确保数据已加载
    if (!vulnerabilityData.value || vulnerabilityData.value.length === 0) {
        console.warn('No vulnerability data available')
        return
    }

    // 统计风险等级数量（排除 flooded 和 unknown）
    const riskCounts = {}
    vulnerabilityData.value.forEach(row => {
        const riskLevel = row[riskColumn]
        if (riskLevel && riskLevelMap[riskLevel]) {
            riskCounts[riskLevel] = (riskCounts[riskLevel] || 0) + 1
        }
    })

    // 转换为饼图数据格式
    const pieData = Object.entries(riskCounts).map(([level, count]) => ({
        name: riskLevelMap[level],
        value: count
    }))

    // 设置饼图颜色
    const colorMap = {
        'Lowest Risk': '#008100',  // 深绿色
        'Low Risk': '#BDE101',     // 浅绿色
        'High Risk': '#FFBE00',    // 橙色
        'Highest Risk': '#F80203'  // 红色
    }

    // 初始化饼图
    if (pieChart.value) {
        const pieOption = {
            title: {
                text: `Risk Level Distribution`,
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                orient: 'horizontal',  // 改为水平排列
                bottom: '0',          // 放到底部
                left: 'center',       // 居中对齐
                data: Object.values(riskLevelMap),
                selected: {
                    'Lowest Risk': false,
                    'Low Risk': true,
                    'High Risk': true,
                    'Highest Risk': true
                }
            },
            grid: {
                bottom: '15%'  // 为底部图例留出空间
            },
            series: [{
                type: 'pie',
                radius: '50%',
                data: pieData,
                itemStyle: {
                    color: (params) => colorMap[params.name]
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        }
        
        charts.value.pie = initChart(pieChart.value, pieOption)
    }

    // 更新趋势图
    if (trendChart.value) {
        // 计算每个时间点的分布
        const trendData = {}
        Object.keys(riskLevelMap).forEach(level => {
            trendData[level] = []
        })

        // 遍历每个时间点
        timeSteps.value.forEach(step => {
            const stepColumn = `risk_level_${step}`
            Object.keys(riskLevelMap).forEach(level => {
                const count = vulnerabilityData.value.filter(row => {
                    const risk = row[stepColumn]
                    return risk === level
                }).length
                trendData[level].push(count)
            })
        })

        charts.value.trend = initChart(trendChart.value, {
            title: {
                text: 'Risk Level Trends Over Time',
                left: 'center'
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    let result = `Time: ${params[0].axisValue}<br/>`;
                    params.forEach(param => {
                        result += `${param.seriesName}: ${param.value}<br/>`;
                    });
                    return result;
                }
            },
            legend: {
                data: Object.values(riskLevelMap),
                bottom: '0',
                left: 'center',
                selected: {
                    'Lowest Risk': false,  // 默认不显示 lowest
                    'Low Risk': true,
                    'High Risk': true,
                    'Highest Risk': true
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: timeSteps.value.map(step => `${step}s`),
                axisLabel: {
                    rotate: 45
                },
                name: 'Time (s)'
            },
            yAxis: {
                type: 'value',
                name: 'Count'
            },
            series: Object.entries(trendData).map(([level, data]) => ({
                name: riskLevelMap[level],
                type: 'line',
                data: data,
                smooth: true,
                lineStyle: {
                    width: 2
                },
                symbol: 'circle',
                symbolSize: 8,
                itemStyle: {
                    color: colorMap[riskLevelMap[level]]
                }
            }))
        })
    }
}

// 初始化风险图表
const initRiskCharts = async () => {
    await nextTick()
    await updateRiskCharts(selectedRiskTimeStep.value)
}

const loadStatistics = async () => {
    try {
        const response = await axios.get(`http://localhost:5000/api/vulnerability/statistics`, {
            params: {
                project_id: props.projectId
            }
        })
        
        if (response.data.status === 'success' && response.data.data.vulnerabilityData) {
            statistics.value = response.data.data
            vulnerabilityData.value = response.data.data.vulnerabilityData
            
            // 提取时间步长
            const timeColumns = Object.keys(vulnerabilityData.value[0])
                .filter(key => key.startsWith('risk_level_'))
                .map(key => parseInt(key.split('_')[2]))
                .sort((a, b) => a - b)
            
            timeSteps.value = timeColumns.filter(step => step % props.timeInterval === 0)
            selectedTimeStep.value = timeSteps.value[0]  // 设置初始时间步长
            selectedRiskTimeStep.value = timeSteps.value[0]
            
            // 确保数据加载后初始化对应的图表
            if (selectedCalculationType.value === 'vulnerability') {
                await nextTick()
                await updateVulnerabilityCharts(selectedTimeStep.value)  // 立即更新脆弱性图表
            } else {
                await nextTick()
                await initRiskCharts()
            }
        } else {
            console.error('Invalid data format received:', response.data)
            ElMessage.error('Failed to load statistics: Invalid data format')
        }
    } catch (error) {
        console.error('Error loading statistics:', error)
        ElMessage.error('Failed to load statistics')
    }
}

// 组件挂载时
onMounted(async () => {
    window.addEventListener('resize', resizeCharts)
    await loadStatistics()
})

// 组件卸载时
onUnmounted(() => {
    window.removeEventListener('resize', resizeCharts)
    disposeCharts()
})

// 监听统计类型变化
watch(selectedCalculationType, async (newValue) => {
    // 先清理现有图表
    disposeCharts()
    
    await nextTick()
    if (newValue === 'risk') {
        await initRiskCharts()
    } else {
        await initVulnerabilityCharts()
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