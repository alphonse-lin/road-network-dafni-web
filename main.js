import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'cesium/Build/Cesium/Widgets/widgets.css'
import '@fortawesome/fontawesome-free/css/all.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 这行很重要！

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')