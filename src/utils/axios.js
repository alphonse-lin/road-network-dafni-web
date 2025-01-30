import axios from 'axios'

// 创建 axios 实例并配置基础 URL
const instance = axios.create({
    baseURL: 'http://localhost:5000'  // 指向后端服务器地址
})

export default instance 