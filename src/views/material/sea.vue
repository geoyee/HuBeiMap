<template>
  <div></div>
</template>
<script setup>
import * as Cesium from "cesium";
import { destination } from "turf";

const { viewer } = window;

viewer.terrainProvider = await Cesium.createWorldTerrainAsync({
  requestVertexNormals: true, // 请求法线，用于地形光照
  requestWaterMask: true, // 动态海洋水效果
});
viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(120.338235, 35.350744, 56283),
  orientation: {
    heading: 0.037605902323875284, // 正东，默认北
    pitch: -0.6395756804359709, // 向正下方看
    roll: 6.283184759051674, // 左右
  },
});
</script>

<style scoped lang="less"></style>
