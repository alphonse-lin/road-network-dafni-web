<template>
    <el-dialog
        :model-value="visible"
        @update:model-value="$emit('update:visible', $event)"
        :title="title"
        width="500px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :show-close="true"
    >
        <div class="progress-container">
            <!-- 步骤展示 -->
            <div class="steps-wrapper">
                <div class="steps" :class="{ 'single-step': calculationSteps.length === 1 }">
                    <template v-for="(step, index) in calculationSteps" :key="index">
                        <!-- Step -->
                        <div class="step">
                            <div :class="['circle', { completed: steps[step.key] }]"></div>
                            <div class="step-content">
                                <span class="step-title">{{ step.title }}</span>
                            </div>
                        </div>
                        <!-- 连接箭头 (除了最后一个步骤) -->
                        <div v-if="index < calculationSteps.length - 1" class="arrow">→</div>
                    </template>
                </div>
            </div>

            <!-- 状态信息 -->
            <div class="status-message">
                {{ statusMessage }}
                <span v-if="isCalculating" class="loading-dots">...</span>
            </div>

            <!-- 错误信息 -->
            <div v-if="error" class="error-message">
                {{ error }}
            </div>

            <!-- 添加底部按钮 -->
            <div class="dialog-footer" v-if="error">
                <el-button @click="$emit('update:visible', false)">Close</el-button>
            </div>
        </div>
    </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch, computed, onBeforeUnmount, provide } from 'vue'
import { ElDialog, ElMessage } from 'element-plus'
import axios from 'axios'
import { useTopologyStore } from '@/stores/topology'

const props = defineProps({
    visible: {
        type: Boolean,
        required: true
    },
    projectId: {
        type: String,
        required: true
    },
    mode: {
        type: String,
        required: true,
        validator: (value) => ['single', 'sequence', 'transportation', 'vulnerability'].includes(value)
    },
    title: {
        type: String,
        default: 'Calculation Progress'
    }
})

const emit = defineEmits(['update:visible', 'calculation-complete'])

// 定义不同模式下的计算步骤
const CALCULATION_MODES = {
    single: [
        { key: 'spaceSyntax', title: 'Calculate Space Syntax', endpoint: '/api/calculate-space-syntax-single' }
    ],
    sequence: [
        { key: 'inundateMap', title: 'Create Inundate Map', endpoint: '/api/create-inundate-map' },
        { key: 'sequenceGeojson', title: 'Create Sequence GeoJSON', endpoint: '/api/create-sequence-geojson' },
        { key: 'spaceSyntax', title: 'Calculate Space Syntax', endpoint: '/api/calculate-space-syntax' }
    ],
    transportation: [
        { key: 'activityChain', title: 'Generate Activity Chain', endpoint: '/api/generate-activity-chain' },
        { key: 'matsim', title: 'Run MATSim', endpoint: '/api/run-matsim' },
        { key: 'convertOutput', title: 'Convert Output', endpoint: '/api/convert-matsim-output' }
    ],
    vulnerability: [
        { key: 'mergeData', title: 'Merge Data', endpoint: '/api/merge-data' },
        { key: 'dtwMatching', title: 'DTW Matching', endpoint: '/api/dtw-matching' },
        { key: 'vulnerability', title: 'Calculate Vulnerability', endpoint: '/api/calculate-vulnerability' }
    ]
}

const steps = ref({})
const statusMessage = ref('Starting calculation...')
const error = ref(null)
const isCalculating = ref(false)
let dotsInterval = null
const currentRadii = ref('100')  // 添加一个 ref 来存储当前使用的半径

// 根据mode获取当前的计算步骤
const calculationSteps = computed(() => CALCULATION_MODES[props.mode])

// 重置状态
const resetState = () => {
    steps.value = calculationSteps.value.reduce((acc, step) => {
        acc[step.key] = false
        return acc
    }, {})
    statusMessage.value = 'Starting calculation...'
    error.value = null
}

// 动画效果的控制函数
const startLoadingAnimation = () => {
    isCalculating.value = true
}

const stopLoadingAnimation = () => {
    isCalculating.value = false
}

// 在组件卸载时清理定时器
onBeforeUnmount(() => {
    if (dotsInterval) {
        clearInterval(dotsInterval)
    }
})

// 提供这个值
provide('calculationRadius', currentRadii)

const topologyStore = useTopologyStore()

// 执行计算
const executeCalculation = async () => {
    try {
        resetState()
        startLoadingAnimation()

        for (const step of calculationSteps.value) {
            statusMessage.value = `Processing ${step.title.toLowerCase()}`
            const response = await axios.post(`http://localhost:5000${step.endpoint}`, {
                task_id: props.projectId,
                radii: props.radius?.toString() || '100'
            })
            
            if (response.data.status === 'error') {
                throw new Error(response.data.message)
            }
            
            // 保存返回的半径值
            if (response.data.radii) {
                topologyStore.setRadius(response.data.radii)
                console.log('CalculationProgress: Set radius to:', response.data.radii)
            }
            
            steps.value[step.key] = true
        }

        stopLoadingAnimation()
        statusMessage.value = 'Calculation completed successfully!'
        ElMessage.success('Calculation completed')
        
        console.log('Emitting calculation-complete with radius:', currentRadii.value)  // 调试日志
        emit('calculation-complete', currentRadii.value)  // 确保这行代码执行
        
        setTimeout(() => {
            emit('update:visible', false)
        }, 2000)

    } catch (err) {
        console.error('Calculation error:', err)
        stopLoadingAnimation()
        error.value = `Calculation failed: ${err.message}`
        ElMessage.error('Calculation failed')
    }
}

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
    if (newVal) {
        executeCalculation()
    }
})
</script>

<style scoped>
.progress-container {
    padding: 20px;
}

.steps-wrapper {
    display: flex;
    justify-content: center;
    width: 100%;
}

.steps {
    display: flex;
    align-items: center;
    margin-bottom: 30px;
}

/* 当只有一个步骤时的样式 */
.steps.single-step {
    justify-content: center;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 2px solid #409EFF;
    background-color: white;
    transition: background-color 0.3s ease;
}

.circle.completed {
    background-color: #409EFF;
}

.arrow {
    color: #409EFF;
    font-size: 24px;
    margin: 0 20px;
}

.step-content {
    text-align: center;
}

.step-title {
    font-size: 14px;
    color: #606266;
}

.loading-dots {
    display: inline-block;
    width: 20px;
    animation: loadingDots 1.5s infinite;
    text-align: left;
}

@keyframes loadingDots {
    0% { content: '.'; }
    33% { content: '..'; }
    66% { content: '...'; }
    100% { content: '.'; }
}

.status-message {
    text-align: center;
    margin-top: 20px;
    color: #409EFF;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
}

.error-message {
    text-align: center;
    margin-top: 20px;
    color: #F56C6C;
}

.dialog-footer {
    margin-top: 20px;
    text-align: center;
}
</style> 