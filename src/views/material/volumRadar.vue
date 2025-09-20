<template>
  <operate-box>
    <el-button type="primary" @click="create">渲染</el-button>
    <el-button type="primary" @click="onClear">清除</el-button>
  </operate-box>
</template>
<script setup>
import * as Cesium from "cesium";
import { onMounted } from "vue";
import TrackMatte from "@/utils/cesiumCtrl/RadarSolidScan.js";
import { destination } from "@turf/turf";

const { viewer } = window;

let trackMatte;
const create = () => {
  // 创建雷达扫描实例
  // const radarScan = new RadarSolidScan({
  //   viewer: viewer,
  //   radius: 1000,
  //   color: Cesium.Color.CYAN.withAlpha(0.5),
  //   speed: 2,
  //   position: [113.9236839, 22.528061, 1],
  // });

  trackMatte = new TrackMatte({
    viewer: viewer,
    id: 1,
    shortwaveRange: 1000.0,
    position: [-80, 35],
  });
  setTimeout(() => {
    viewer.camera.flyTo({
      destination: new Cesium.Cartesian3.fromDegrees(-80, 35, 10000),
    });
  }, 1000);
};

const onClear = () => {
  trackMatte.clear();
};
</script>
<style lang="less"></style>
