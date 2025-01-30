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
                    <p>Total Buildings: {{ basicStats.totalBuildings }}</p>
                    <!-- <p>Road Network Length: 156.7 km</p> -->
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
                    <p>Duration: {{ simulationStats.duration }}</p>
                </div>

                <div class="chart-container">
                    <h3>Convergence Analysis</h3>
                    <div ref="convergenceChart" style="height: 250px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Trip Patterns Distribution</h3>
                    <div ref="legDurationChart" style="height: 300px;"></div>
                </div>

                <div class="chart-container">
                    <h3>Traffic Flow</h3>
                    <div ref="normalTrafficChart" style="height: 250px;"></div>
                    
                    <!-- 添加模拟按钮和播放控制器 -->
                    <div class="simulation-controls">
                        <el-button 
                            type="default" 
                            @click="handleCalculation"
                            :loading="loading"
                            class="calculation-btn"
                        >
                            Start Simulation
                        </el-button>
                        
                        <div v-if="showTrafficPlayer" class="traffic-player">
                            <div class="player-controls">
                                <el-button 
                                    @click="togglePlay"
                                    :type="isPlaying ? 'warning' : 'default'"
                                >
                                    {{ isPlaying ? 'Pause' : 'Play' }}
                                </el-button>
                                <span class="time-display">{{ formatTime(currentTimeIndex) }}</span>
                            </div>
                            <el-slider
                                v-if="timePoints.length > 1"
                                v-model="currentTimeIndex"
                                :min="0"
                                :max="timePoints.length - 1"
                                :format-tooltip="formatTime"
                                @change="handleTimeChange"
                            />
                            <div v-else class="no-data-message">
                                No time series data available
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import axios from '@/utils/axios'
import { useMapStore } from '@/stores/map'
import { ElMessage } from 'element-plus'

const props = defineProps({
    projectId: {
        type: String,
        required: true
    }
})

const selectedStatsType = ref('basic')

// 图表引用
const landUseChart = ref(null)
const vehicleChart = ref(null)
const ageChart = ref(null)
const convergenceChart = ref(null)
const normalTrafficChart = ref(null)
const legDurationChart = ref(null)

// 添加基础统计数据
const basicStats = ref({
    totalBuildings: 0,
    landUseDistribution: [],
    vehicleTypeDistribution: [],
    ageStructure: []
})

// 添加模拟统计数据
const simulationStats = ref({
    duration: '24 hours',
    iterationScores: [],
    legDurations: [],
    trafficFlow: []
})

const mapStore = useMapStore()
const showTrafficPlayer = ref(false)
const isPlaying = ref(false)
const currentTimeIndex = ref(0)
const playInterval = ref(null)
const timePoints = ref([])
const loading = ref(false)

// 加载基础统计数据
const loadBasicStats = async () => {
    try {
        console.log('Loading basic stats for project:', props.projectId)
        const response = await axios.get('/api/transportation/basic-stats', {
            params: { project_id: props.projectId }
        })
        
        if (response.data.status === 'success') {
            basicStats.value = response.data.data
            await initCharts()
        }
    } catch (error) {
        console.error('Error loading basic stats:', error)
    }
}

// 加载模拟统计数据
const loadSimulationStats = async () => {
    try {
        const response = await axios.get('/api/transportation/simulation-stats', {
            params: { project_id: props.projectId }
        })
        
        if (response.data.status === 'success') {
            simulationStats.value = response.data.data
            await initCharts()
        }
    } catch (error) {
        console.error('Error loading simulation stats:', error)
    }
}

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

// 修改收敛分析图表的初始化函数
const initConvergenceChart = (chartRef, data) => {
    const chart = echarts.init(chartRef)
    chart.setOption({
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: data.map(item => `Iteration ${item.iteration}`),
            name: 'Iteration'
        },
        yAxis: {
            type: 'value',
            name: 'Score'
        },
        series: [
            {
                name: 'Executed',
                data: data.map(item => item.executed),
                type: 'line',
                smooth: true
            },
            {
                name: 'Average',
                data: data.map(item => item.avg),
                type: 'line',
                smooth: true
            },
            {
                name: 'Best',
                data: data.map(item => item.best),
                type: 'line',
                smooth: true
            }
        ]
    })
}

// 修改交通流量图表的初始化函数
const initTrafficChart = (chartRef, data) => {
    const chart = echarts.init(chartRef)
    const timeData = data.map(item => {
        const hours = Math.floor(item.time / 3600)
        const minutes = Math.floor((item.time % 3600) / 60)
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
    })
    
    chart.setOption({
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['departures', 'arrivals', 'en-route'],
            bottom: 0,
            selectedMode: true,
            textStyle: {
                color: '#666'
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
            data: timeData,
            name: 'Time',
            axisLabel: {
                formatter: value => value
            }
        },
        yAxis: {
            type: 'value',
            name: 'Number of People'
        },
        series: [
            {
                name: 'departures',
                type: 'line',
                data: data.map(item => item.departures),
                itemStyle: { color: '#FF4D4F' },
                smooth: true
            },
            {
                name: 'arrivals',
                type: 'line',
                data: data.map(item => item.arrivals),
                itemStyle: { color: '#4096FF' },
                smooth: true
            },
            {
                name: 'en-route',
                type: 'line',
                data: data.map(item => item.enRoute),
                itemStyle: { color: '#52C41A' },
                smooth: true
            }
        ]
    })
}

// 添加 Leg Duration 图表初始化函数
const initLegDurationChart = (chartRef, data) => {
    const chart = echarts.init(chartRef)
    
    // 获取前10个最常见的出行模式
    const patterns = data
        .sort((a, b) => {
            const sumA = Object.values(a.durations).reduce((acc, curr) => acc + curr, 0)
            const sumB = Object.values(b.durations).reduce((acc, curr) => acc + curr, 0)
            return sumB - sumA
        })
        .slice(0, 10)
    
    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['0-5 min', '5-10 min', '10-15 min'],
            bottom: 0
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: patterns.map(item => item.pattern),
            axisLabel: {
                interval: 0,
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: 'Number of Trips'
        },
        series: [
            {
                name: '0-5 min',
                type: 'bar',
                stack: 'total',
                data: patterns.map(item => item.durations['0+']),
                itemStyle: { color: '#8884d8' }
            },
            {
                name: '5-10 min',
                type: 'bar',
                stack: 'total',
                data: patterns.map(item => item.durations['5+']),
                itemStyle: { color: '#82ca9d' }
            },
            {
                name: '10-15 min',
                type: 'bar',
                stack: 'total',
                data: patterns.map(item => item.durations['10+']),
                itemStyle: { color: '#ffc658' }
            }
        ]
    }
    
    chart.setOption(option)
}

// 修改初始化图表的函数
const initCharts = async () => {
    await nextTick()
    
    if (selectedStatsType.value === 'basic') {
        if (landUseChart.value) {
            initPieChart(landUseChart.value, basicStats.value.landUseDistribution)
        }
        
        if (vehicleChart.value) {
            initPieChart(vehicleChart.value, basicStats.value.vehicleTypeDistribution)
        }
        
        if (ageChart.value) {
            initPieChart(ageChart.value, basicStats.value.ageStructure)
        }
    } else {
        if (convergenceChart.value) {
            initConvergenceChart(convergenceChart.value, simulationStats.value.iterationScores)
        }
        if (normalTrafficChart.value) {
            initTrafficChart(normalTrafficChart.value, simulationStats.value.trafficFlow)
        }
        if (legDurationChart.value) {
            initLegDurationChart(legDurationChart.value, simulationStats.value.legDurations)
        }
    }
}

// 修改 watch
watch(selectedStatsType, async () => {
    if (selectedStatsType.value === 'basic') {
        await loadBasicStats()
    } else {
        await loadSimulationStats()
    }
    await initCharts()
})

// 修改 onMounted
onMounted(async () => {
    if (selectedStatsType.value === 'basic') {
        await loadBasicStats()
    } else {
        await loadSimulationStats()
    }
    await initCharts()
    window.addEventListener('resize', handleResize)
})

// 清理事件监听
onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (playInterval.value) {
        clearInterval(playInterval.value)
    }
    if (mapStore.mapInstance?.clearTrafficVisualization) {
        mapStore.mapInstance.clearTrafficVisualization()
    }
    mapStore.showTrafficLegend(false)
})

// 处理窗口大小变化
const handleResize = () => {
    const charts = [
        landUseChart.value, 
        vehicleChart.value, 
        ageChart.value,
        convergenceChart.value,
        normalTrafficChart.value,
        legDurationChart.value
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

// 修改加载交通模拟数据的方法
const loadTrafficSimulation = async () => {
    try {
        loading.value = true;
        console.log('Requesting traffic data...');
        
        // 在加载新数据之前，先清除现有的可视化
        if (mapStore.mapInstance?.clearAllDataSources) {
            await mapStore.mapInstance.clearAllDataSources();
            console.log('Cleared existing visualizations');
        }
        
        const response = await axios.get('/api/transportation/road-traffic', {
            params: { project_id: props.projectId }
        });
        
        if (response.data.status === 'success') {
            const { roadNetwork, trafficData } = response.data.data;
            console.log('Received data:', { 
                networkSize: roadNetwork.features.length,
                trafficDataSize: Object.keys(trafficData).length 
            });
            
            // 验证数据
            if (!trafficData || Object.keys(trafficData).length === 0) {
                ElMessage.warning('No traffic data available');
                return;
            }

            // 从交通数据中提取时间点
            const sampleRoadId = Object.keys(trafficData)[0];
            timePoints.value = Object.keys(trafficData[sampleRoadId])
                .filter(key => key.startsWith('traffic_'))
                .sort((a, b) => {
                    const timeA = parseInt(a.split('_')[1]);
                    const timeB = parseInt(b.split('_')[1]);
                    return timeA - timeB;
                });
            
            console.log('Time points:', timePoints.value.length);
            
            if (timePoints.value.length === 0) {
                ElMessage.warning('No time series data available');
                return;
            }

            // 先设置数据
            await mapStore.setTrafficData(trafficData);
            await mapStore.setRoadNetwork(roadNetwork);
            
            // 等待数据设置完成
            await nextTick();
            
            // 初始化可视化
            await mapStore.initializeTrafficVisualization();
            
            // 重置播放器状态
            currentTimeIndex.value = 0;
            isPlaying.value = false;
            if (playInterval.value) {
                cancelAnimationFrame(playInterval.value);
                playInterval.value = null;
            }
            
            // 显示播放控制器
            showTrafficPlayer.value = true;
            
            // 显示第一帧
            await updateMapTraffic(0);
            
            // 显示图例
            mapStore.showTrafficLegend(true);
            
            console.log('Traffic simulation loaded successfully');
        }
    } catch (error) {
        console.error('Error loading traffic simulation:', error);
        ElMessage.error('Failed to load traffic simulation');
    } finally {
        loading.value = false;
    }
};

// 格式化时间显示
const formatTime = (index) => {
    if (!timePoints.value[index]) return '00:00'
    const seconds = parseInt(timePoints.value[index].split('_')[1])
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
}

// 修改播放控制逻辑
const togglePlay = async () => {
    if (timePoints.value.length <= 1) {
        ElMessage.warning('Not enough time series data for playback');
        return;
    }
    
    if (isPlaying.value) {
        // 如果正在播放，调用暂停方法
        await handlePause();
    } else {
        // 开始播放
        mapStore.showTrafficLegend(true);
        let lastTime = 0;
        const frameRate = 1000;

        const animate = async (currentTime) => {
            if (!isPlaying.value) return;

            const deltaTime = currentTime - lastTime;
            if (deltaTime >= frameRate) {
                currentTimeIndex.value = (currentTimeIndex.value + 1) % timePoints.value.length;
                await updateMapTraffic(currentTimeIndex.value);
                lastTime = currentTime;
            }

            playInterval.value = requestAnimationFrame(animate);
        };

        isPlaying.value = true;
        playInterval.value = requestAnimationFrame(animate);
    }
};

// 修改更新地图交通流量的方法
const updateMapTraffic = async (index) => {
    try {
        const timePoint = timePoints.value[index];
        if (!timePoint) return;

        // 更新当前时间点
        mapStore.setCurrentTimePoint(timePoint);
        
        // 确保视图更新
        await nextTick();
        
        // 更新地图可视化
        if (mapStore.mapInstance) {
            await mapStore.mapInstance.updateTrafficVisualization();
        }
    } catch (error) {
        console.error('Error updating traffic:', error);
    }
};

// 时间改变处理
const handleTimeChange = (index) => {
    if (timePoints.value.length > index) {
        updateMapTraffic(index);
    }
};

// 修改组件卸载时的清理逻辑
onBeforeUnmount(() => {
    isPlaying.value = false;
    if (playInterval.value) {
        cancelAnimationFrame(playInterval.value);
        playInterval.value = null;
    }
});

// 添加暂停时的处理
const handlePause = async () => {
    isPlaying.value = false;
    if (playInterval.value) {
        cancelAnimationFrame(playInterval.value);
        playInterval.value = null;
    }
    // 确保最后一帧正确显示
    await updateMapTraffic(currentTimeIndex.value);
};

// 添加计算按钮的处理方法
const handleCalculation = async () => {
    try {
        // 在开始新的计算之前清除现有的可视化
        if (mapStore.mapInstance?.clearAllDataSources) {
            await mapStore.mapInstance.clearAllDataSources();
            console.log('Cleared existing visualizations before calculation');
        }
        
        // 执行计算逻辑
        await loadTrafficSimulation();
        
    } catch (error) {
        console.error('Error in calculation:', error);
        ElMessage.error('Calculation failed');
    }
};

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

.simulation-controls {
    margin-top: 15px;
    text-align: center;
}

.traffic-player {
    margin-top: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
}

.player-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.time-display {
    font-family: monospace;
    font-size: 14px;
    color: #666;
}

.no-data-message {
    color: #909399;
    text-align: center;
    padding: 10px;
    font-size: 14px;
}

.calculation-btn {
    margin-bottom: 10px;
}
</style> 