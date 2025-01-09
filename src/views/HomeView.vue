<template>
  <div class="home">
    <TopNavigation @layer-toggle="handleLayerToggle" />
    <MapViewer ref="mapViewer" />
  </div>
</template>

<script>
import MapViewer from '@/components/MapViewer.vue'
import TopNavigation from '@/components/TopNavigation.vue'

export default {
  name: 'HomeView',
  components: {
    MapViewer,
    TopNavigation
  },
  methods: {
    handleLayerToggle(layerName) {
      // Handle layer toggling logic here
      console.log(`Toggle layer: ${layerName}`)
    }
  }
}
</script>

<style scoped>
.home {
  width: 100%;
  height: 100%;
  position: relative;
}
</style> 