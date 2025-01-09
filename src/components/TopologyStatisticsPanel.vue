<template>
    <div class="statistics-panel">
        <div class="panel-header">
            <h2>Topology Calculation Report</h2>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <!-- 基础信息部分 -->
            <div class="basic-info">
                <h3>Basic Information</h3>
                <div class="parameters">
                    <h4>Parameters:</h4>
                    <p>Network interpolation directed</p>
                </div>

                <div class="results">
                    <h4>Results:</h4>
                    <p>Diameter: {{ basicStats.diameter }}</p>
                    <p>Radius: {{ basicStats.radius }}</p>
                    <p>Average Path length: {{ basicStats.avgPathLength }}</p>
                </div>
            </div>

            <!-- 特定统计信息部分 -->
            <div class="specific-stats">
                <div class="stats-header">
                    <h3>Detailed Statistics</h3>
                    <select v-model="selectedStatsType" class="stats-selector">
                        <option value="static">Static Analysis</option>
                        <option v-if="hasDynamicData" value="dynamic">Dynamic Analysis</option>
                    </select>
                </div>

                <div class="charts">
                    <div class="chart-container">
                        <h4>Betweenness Centrality Distribution</h4>
                        <div ref="betweennessChart" style="height: 200px;"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h4>Closeness Centrality Distribution</h4>
                        <div ref="closenessChart" style="height: 200px;"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h4>Harmonic Closeness Centrality Distribution</h4>
                        <div ref="harmonicChart" style="height: 200px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const betweennessChart = ref(null)
const closenessChart = ref(null)
const harmonicChart = ref(null)

// 接收初始类型作为prop
const props = defineProps({
    type: {
        type: String,
        required: true
    },
    hasDynamicData: {
        type: Boolean,
        default: false
    }
})

defineEmits(['close'])

// 选择的统计类型（用于下拉框）
const selectedStatsType = ref(props.type)

// 生成基础信息的随机数据
const basicStats = ref({
    diameter: (Math.random() * 10).toFixed(2),
    radius: (Math.random() * 5).toFixed(2),
    avgPathLength: (Math.random() * 15).toFixed(2),
})

// 生成特定统计信息的随机数据
const generateRandomData = (type) => {
    console.log(type)
    return {
        betweenness: Array.from({ length: 50 }, () => Math.random() * 75),
        closeness: Array.from({ length: 50 }, () => Math.random() * 2),
        harmonic: Array.from({ length: 50 }, () => Math.random() * 2)
    }
}

const initChart = (el, data, xAxisMax) => {
    if (!el) return
    const chart = echarts.init(el)
    
    // 根据选择的类型设置不同的颜色
    const color = selectedStatsType.value === 'static' ? '#E01F54' : '#5470C6'
    
    chart.setOption({
        grid: {
            top: 30,
            right: 20,
            bottom: 30,
            left: 50
        },
        xAxis: {
            type: 'value',
            max: xAxisMax
        },
        yAxis: {
            type: 'value',
            name: 'Count'
        },
        series: [{
            data: data,
            type: 'scatter',
            symbolSize: 5,
            itemStyle: {
                color: color
            }
        }]
    })
}

const updateCharts = () => {
    const data = generateRandomData(selectedStatsType.value)
    initChart(betweennessChart.value, data.betweenness, 75)
    initChart(closenessChart.value, data.closeness, 2)
    initChart(harmonicChart.value, data.harmonic, 2)
}

// 监听类型变化，更新图表
watch(selectedStatsType, () => {
    updateCharts()
})

// 监听类型变化，确保当没有dynamic数据时不会选中dynamic选项
watch(() => props.hasDynamicData, (newValue) => {
    if (!newValue && selectedStatsType.value === 'dynamic') {
        selectedStatsType.value = 'static'
    }
})

// 监听type prop的变化
watch(() => props.type, (newType) => {
    selectedStatsType.value = newType
})

onMounted(() => {
    updateCharts()
})
</script>

<style scoped>
.statistics-panel {
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

.basic-info, .specific-stats {
    margin-bottom: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.stats-selector {
    padding: 5px 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
    font-size: 14px;
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

p {
    margin: 5px 0;
    color: #666;
}

.chart-container {
    margin-bottom: 20px;
    padding: 10px;
    background: white;
    border-radius: 6px;
}
</style> 