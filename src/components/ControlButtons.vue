<template>
    <div class="control-buttons">
        <div class="button-container">
            <el-tooltip
                content="Start Computation"
                placement="top"
                effect="light"
            >
                <el-button 
                    type="primary"
                    :round="true"
                    @click="handleCompute"
                    :disabled="!isMarkerClicked || isComputed"
                    size="large"
                >
                    <el-icon size="20"><VideoPlay /></el-icon>
                </el-button>
            </el-tooltip>
            
            <el-tooltip
                content="Topology Calculation"
                placement="top"
                effect="light"
            >
                <el-button 
                    type="primary"
                    :round="true"
                    @click="handleTopology"
                    :disabled="!isComputed"
                    size="large"
                >
                    <el-icon size="20"><Share /></el-icon>
                </el-button>
            </el-tooltip>
            
            <el-tooltip
                content="Transportation Calculation"
                placement="top"
                effect="light"
            >
                <el-button 
                    type="primary"
                    :round="true"
                    @click="handleTransportation"
                    :disabled="!isComputed"
                    size="large"
                >
                    <el-icon size="20"><Van /></el-icon>
                </el-button>
            </el-tooltip>
            
            <el-tooltip
                content="Index Calculation"
                placement="top"
                effect="light"
            >
                <el-button 
                    type="primary"
                    :round="true"
                    @click="handleIndex"
                    :disabled="!isComputed"
                    size="large"
                >
                    <el-icon size="20"><DataLine /></el-icon>
                </el-button>
            </el-tooltip>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElButton, ElTooltip } from 'element-plus'
import { VideoPlay, Share, Van, DataLine } from '@element-plus/icons-vue'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/tooltip/style/css'

const emit = defineEmits(['compute', 'topology', 'transportation', 'index'])
const isComputed = ref(false)

const handleCompute = () => {
    isComputed.value = true
    emit('compute')
}

const handleTopology = () => {
    emit('topology')
}

const handleTransportation = () => {
    emit('transportation')
}

const handleIndex = () => {
    emit('index')
}

defineProps({
    isMarkerClicked: {
        type: Boolean,
        default: false
    },
    isComputed: {
        type: Boolean,
        default: false
    }
})
</script>

<style scoped>
.control-buttons {
    position: fixed;
    left: 50%;
    bottom: 30px;
    transform: translateX(-50%);
    z-index: 1000;
    padding: 15px 20px;
}

.button-container {
    display: flex;
    gap: 20px;
    align-items: center;
}
</style>