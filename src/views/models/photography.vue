<template>
  <operate-box>
    <el-button type="primary" @click="create">渲染</el-button>
    <el-button type="primary" @click="onClear">清除</el-button>
  </operate-box>
</template>
<script setup>
import { ref, onUnmounted } from "vue";
import * as Cesium from "cesium";
import TrackMatte from "@/utils/cesiumCtrl/RadarSolidScan.js";

const { viewer } = window;
let photography;
const create = async () => {
  const tileset = await Cesium.Cesium3DTileset.fromIonAssetId(354759);
  photography = viewer.scene.primitives.add(tileset);
  viewer.zoomTo(tileset);
};

const onClear = () => {
  if (photography) {
    viewer.scene.primitives.remove(photography);
    photography = null;
  }
};

onUnmounted(() => {
  onClear();
});
</script>
<style lang="less" scoped></style>
