<template>
    <div class="index-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King'sCross to Farringdon(25km²)</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <div class="file-preview">
                <h4>File Preview</h4>
                <button @click="handleCheckFiles" class="check-btn">
                    Check Files
                </button>
                
                <div class="checkbox-group">
                    <el-checkbox v-model="topologyCalculation" disabled>
                        Topology Calculation
                        <el-tooltip
                            content="Topology calculation based on network structure"
                            placement="right"
                        >
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </el-checkbox>
                    
                    <el-checkbox v-model="transportationSimulation" disabled>
                        Transportation Simulation
                        <el-tooltip
                            content="Transportation demand based on simulation"
                            placement="right"
                        >
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </el-checkbox>
                </div>
            </div>

            <div class="index-calculation">
                <h4>Index Calculation</h4>
                <div class="slider-container">
                        <div class="slider-label">
                            <span>Time Step</span>
                            <span class="slider-value">{{ vulnerabilityTimeStep }}</span>
                        </div>
                        <el-slider 
                            v-model="vulnerabilityTimeStep" 
                            :min="100" 
                            :max="10000" 
                            :default-value="450"
                        />
                        <p class="description">Description</p>
                </div>
                
                <div class="vulnerability-section">
                    <h5>• Vulnerability Calculation</h5>
                    <div class="image-grid">
                        <img src="@/assets/index_1.jpg" alt="Vulnerability 1" />
                    </div>
                    
                </div>

                <div class="risk-section">
                    <h5>• Risk Index Calculation</h5>
                    <div class="image-grid">
                        <img src="@/assets/index_2.jpg" alt="Risk 1" />
                    </div>
                    
                    <!-- <div class="slider-container">
                        <div class="slider-label">
                            <span>Time Step</span>
                            <span class="slider-value">{{ riskTimeStep }}</span>
                        </div>
                        <el-slider 
                            v-model="riskTimeStep" 
                            :min="100" 
                            :max="10000" 
                            :default-value="450"
                        />
                        <p class="description">Description</p>
                    </div> -->

                    <div class="button-group">
                        <el-button 
                            class="calculation-btn" 
                            type="primary"
                            @click="handleVulnerabilityCalculation"
                            :disabled="!calculationEnabled"
                        >
                            Calculation
                        </el-button>

                    </div>

                    <div>
                        <el-button 
                            class="view-result-btn" 
                            type="default"
                            @click="handleRiskCalculation"
                            :disabled="!calculationEnabled"
                        >
                            View Result
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <CalculationProgress
        v-model:visible="showProgress"
        :project-id="props.projectId"
        mode="vulnerability"
        title="Vulnerability Calculation Progress"
        @calculation-complete="handleCalculationComplete"
    />
</template>

<script setup>
import { ref } from 'vue'
import { ElCheckbox, ElSlider, ElButton, ElMessage, ElTooltip } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import CalculationProgress from './CalculationProgress.vue'
import axios from 'axios'

const props = defineProps({
    projectId: {
        type: String,
        required: true
    }
})

const topologyCalculation = ref(false)
const transportationSimulation = ref(false)
const vulnerabilityTimeStep = ref(450)
// const riskTimeStep = ref(450)
const showProgress = ref(false)
const calculationEnabled = ref(false)

const emit = defineEmits(['close', 'vulnerabilityCalculation', 'riskCalculation'])

const handleCheckFiles = async () => {
    try {
        console.log('Checking files for project:', props.projectId)
        const response = await axios.get(`http://localhost:5000/api/check-files-2/${props.projectId}`)
        const { hasTopologyCalculation, hasMatsimCalculation, hasMergedData } = response.data
        
        if (hasTopologyCalculation && hasMatsimCalculation && hasMergedData) {
            calculationEnabled.value = true
            topologyCalculation.value = true
            transportationSimulation.value = true
            ElMessage.success('Previous calculations completed')
        } else {
            ElMessage.warning('Please complete previous calculations first')
        }
    } catch (error) {
        console.error('Error checking files:', error)
        ElMessage.error('Failed to check files')
    }
}

const handleVulnerabilityCalculation = () => {
    showProgress.value = true
}

const handleRiskCalculation = () => {
    console.log('Emitting risk calculation event')
    emit('riskCalculation')
}

const handleCalculationComplete = () => {
    ElMessage.success('Calculation completed')
    emit('vulnerabilityCalculation')
}
</script>

<style scoped>
.index-panel {
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
    text-align: left;
}

.panel-header h3 {
    margin: 5px 0 0;
    font-size: 16px;
    color: #666;
    font-weight: normal;
    text-align: left;
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

h4 {
    margin: 15px 0;
    color: #333;
}

h5 {
    margin: 10px 0;
    color: #666;
    font-style: italic;
}

.check-btn {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 10px 0;
}

.checkbox-group {
    margin: 15px 0;
}

.settings-icon {
    margin-left: 8px;
    cursor: pointer;
}

.image-grid img {
    width: 100%;
    height: auto;
    border-radius: 4px;
}

/* .risk-section .image-grid {
    grid-template-columns: repeat(5, 1fr);
} */

.slider-container {
    margin: 15px 0;
}

.slider-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    color: #666;
}

.description {
    color: #999;
    font-style: italic;
    margin: 5px 0;
}

.button-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 20px;
    margin-bottom: 20px;
}

.calculation-btn
{
    width: 100%;
    margin: 20px 0 10px;
}

.view-result-btn {
    width: 100%;
    margin: 20px 0 10px;
}


.info-icon {
    margin-left: 8px;
    color: #909399;
    cursor: help;
}

:deep(.el-checkbox) {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

:deep(.el-checkbox__label) {
    display: flex;
    align-items: center;
}

:deep(.el-button) {
    margin: 0;
}
</style> 