<template>
  <div class="top-nav">
    <!-- Logo and Icons Container -->
    <div class="left-section">
      <!-- Logo -->
      <div class="logo-container">
        <div class="logo">
          DAFNI-IMPACT
        </div>
      </div>
      
      <!-- Navigation Icons -->
      <div class="nav-icons">
        <button class="icon-btn" title="Search">
          <i class="fa-solid fa-magnifying-glass"></i>
        </button>
        <button class="icon-btn" title="Home View">
          <i class="fa-solid fa-house"></i>
        </button>
        <button class="icon-btn" title="Calendar">
          <i class="fa-regular fa-calendar"></i>
        </button>
        <button class="icon-btn" title="Location">
          <i class="fa-solid fa-location-dot"></i>
        </button>
        <button class="icon-btn" title="Layers">
          <i class="fa-solid fa-layer-group"></i>
        </button>
        <button class="icon-btn" title="Advanced Search">
          <i class="fa-solid fa-magnifying-glass-plus"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopNavigation'
}
</script>

<style scoped>
.top-nav {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 9999;
  pointer-events: auto;
  background: transparent;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
}

.logo-container {
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logo {
  font-size: 16px;
  font-weight: bold;
  color: #2a71cd;
  font-family: 'Times New Roman', Times, serif;
}

.nav-icons {
  display: flex;
  gap: 5px;
  background: rgba(255, 255, 255, 0.3);
  /* padding: 4px; */
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  padding: 0;
  color: #5d99e8;
}

.icon-btn:hover {
  background: rgba(26, 75, 140, 0.1);
}

.icon-btn i {
  font-size: 16px;
  color: #40697a;
}
</style> 