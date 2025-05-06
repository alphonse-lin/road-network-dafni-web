import axios from 'axios'

// 创建 axios 实例并配置基础 URL
const instance = axios.create({
    // 优先使用环境变量中的API URL，如果不存在则使用localhost
    baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5000'
})

export default instance 