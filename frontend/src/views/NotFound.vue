<script setup lang="ts">
import Container from "@/components/Container.vue";
</script>

<template>
  <Container>
    <div class="stars"></div>
    <div class="flex flex-col items-center justify-center h-full">
      <h1 class="text-7xl font-bold text-blue-500">404</h1>
      <p class="text-lg text-gray-300 mb-8">You're lost in space</p>

      <div class="rocket-container">
        <div class="rocket">
          <!-- Rocket body -->
          <div class="rocket-body">
            <div class="window"></div>
          </div>
          <!-- Rocket wings -->
          <div class="rocket-wing left-wing"></div>
          <div class="rocket-wing right-wing"></div>
          <!-- Rocket bottom -->
          <div class="rocket-bottom"></div>
          <!-- Rocket door -->
          <div class="rocket-door"></div>
          <!-- Flames -->
          <div class="flames">
            <div class="flame flame1"></div>
            <div class="flame flame2"></div>
            <div class="flame flame3"></div>
          </div>
        </div>
      </div>
    </div>
  </Container>
</template>

<style scoped>
.stars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  overflow: hidden;
}

.stars:before,
.stars:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 200%;
  animation: twinkle 7s linear infinite, stars-move 20s linear infinite;
}

.stars:before {
  background-image: radial-gradient(1px 1px at 25% 5%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 50% 15%, white, rgba(255, 255, 255, 0)),
    radial-gradient(2px 2px at 15% 25%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 35% 30%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 65% 10%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1.5px 1.5px at 85% 20%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 10% 40%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1.5px 1.5px at 44% 42%, white, rgba(255, 255, 255, 0)),
    radial-gradient(2px 2px at 70% 55%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 90% 65%, white, rgba(255, 255, 255, 0));
  background-repeat: repeat;
  background-size: 200px 200px;
}

.stars:after {
  background-image: radial-gradient(1px 1px at 10% 10%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1.5px 1.5px at 30% 22%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 60% 15%, white, rgba(255, 255, 255, 0)),
    radial-gradient(2px 2px at 75% 5%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 95% 28%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1.5px 1.5px at 22% 53%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1px 1px at 45% 70%, white, rgba(255, 255, 255, 0)),
    radial-gradient(2px 2px at 65% 80%, white, rgba(255, 255, 255, 0)),
    radial-gradient(1.5px 1.5px at 80% 95%, white, rgba(255, 255, 255, 0));
  background-repeat: repeat;
  background-size: 300px 300px;
  animation-delay: 1s;
  animation: twinkle 7s linear infinite, stars-move 25s linear infinite;
}

@keyframes stars-move {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-50%);
  }
}

@keyframes twinkle {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.7;
  }
}

.rocket-container {
  position: relative;
  width: 100px;
  height: 135px;
  margin: 0 auto;
}

.rocket {
  position: relative;
  width: 100%;
  height: 100%;
}

.rocket-body {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 120px;
  background: linear-gradient(to bottom, #ff7b00, #ff5500);
  border-radius: 50% 50% 15% 15%;
  z-index: 2;
  border: 1px solid #ff6347;
}

.window {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 25px;
  height: 25px;
  background: linear-gradient(135deg, #3ad6ff, #057a9f);
  border-radius: 50%;
  border: 3px solid #a0a0a0;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.5);
}

.rocket-wing {
  position: absolute;
  bottom: 10px;
  width: 30px;
  height: 50px;
  background: linear-gradient(to bottom, #ff5500, #ff2200);
  z-index: 1;
  border: 1px solid #ff6347;
}

.left-wing {
  left: 0;
  transform: skewY(-30deg);
  border-radius: 20px 0 0 10px;
}

.right-wing {
  right: 0;
  transform: skewY(30deg);
  border-radius: 0 20px 10px 0;
}

.rocket-bottom {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 15px;
  background-color: #a0a0a0;
  border-radius: 0 0 15px 15px;
  z-index: 2;
  border: 1px solid #8a8a8a;
}

.rocket-door {
  position: absolute;
  top: 50px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 30px;
  background-color: #ff9900;
  border-radius: 5px;
  z-index: 3;
  border: 1px solid #ff6347;
}

.flames {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  z-index: 1;
}

.flame {
  position: absolute;
  bottom: 0;
  border-radius: 50% 50% 50% 50%;
  box-shadow: 0 0 10px 5px rgba(255, 100, 20, 0.5);
}

.flame1 {
  width: 30px;
  height: 30px;
  left: 5px;
  background: radial-gradient(circle, #ffdd00, #ff5500);
  animation: flicker 0.2s ease-in infinite alternate;
}

.flame2 {
  width: 25px;
  height: 25px;
  left: 8px;
  background: radial-gradient(circle, #ffff00, #ffaa00);
  animation: flicker 0.15s ease-in infinite alternate;
}

.flame3 {
  width: 20px;
  height: 20px;
  left: 10px;
  background: radial-gradient(circle, #ffffff, #ffdd00);
  animation: flicker 0.1s ease-in infinite alternate;
}

@keyframes flicker {
  0% {
    transform: scale(0.8);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.2);
    opacity: 1;
  }
}
</style>
