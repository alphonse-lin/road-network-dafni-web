<template>
  <nav>
    <!-- 导航内容 -->
  </nav>
  <router-view/>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 添加全局样式 */
html, 
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

#app {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
}

/* 确保图标正确显示 */
.fas,
.far,
.fa {
  font-family: 'Font Awesome 5 Free' !important;
}

.far {
  font-weight: 400;
}

.fas {
  font-weight: 900;
}
</style> 