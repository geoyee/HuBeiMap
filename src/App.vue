<script setup>
import { onMounted } from "vue";
import * as Cesium from "cesium";
import CesiumTerrainProviderEdit from "./utils/cesiumCtrl/flat/CesiumTerrainProviderEdit.js";
import { getcameraInfo } from "@/utils/cesiumCtrl/getCameraInfo.js";

Cesium.Ion.defaultAccessToken =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI1MTg4ZDQ3NS1jZjgyLTRkNDUtODc1Ni1jYjY3YzM5YWJlYjUiLCJpZCI6MjU5NjEyLCJpYXQiOjE3MzMyMDQzMjZ9.WkUOmgdA5uGbbGJsyNIEuxfHkY553ZsNUdAj-_V3kRA";

onMounted(() => {
  init();
});
const init = () => {
  const viewer = new Cesium.Viewer("cesiumContainer", {
    infoBox: false,
    // timeline: false, // 是否显示时间线控件
    // imageryProvider: new Cesium.ArcGisMapServerImageryProvider({
    //   url: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
    // }),
    // 此处使用CesiumTerrainProviderEdit替换原来的CesiumTerrainProvider类，实现指定区域地形压平处理
    // terrainProvider: new CesiumTerrainProviderEdit({
    //   url: "http://data.marsgis.cn/terrain",
    // }),
    // terrain: Cesium.Terrain.fromWorldTerrain({
    //   requestVertexNormals: true, //Needed to visualize slope
    // }),
    // 指定上下文
    // contextOptions: {
    //   requestWebgl1: true,
    // },
    // animation: false,
    // baseLayerPicker: false,
    fullscreenButton: false,
    geocoder: false,
    infoBox: false,
    sceneModePicker: false,
    selectionIndicator: false,
    timeline: false,
    navigationHelpButton: false,
    animation: false,
    baseLayerPicker: false,
    homeButton: false,
    location: false, // 位置信息展示
    navigation: false, // toolbar
    copyrightLogo: false,
    sceneMode: Cesium.SceneMode.SCENE2D, // 2d
    // scene3DOnly: true,
    // orderIndependentTranslucency: false,
    // baseLayer: Cesium.ImageryLayer.fromProviderAsync(
    //   Cesium.ArcGisMapServerImageryProvider.fromBasemapType(
    //     Cesium.ArcGisBaseMapType.SATELLITE
    //   )
    // ),
  });
  // 分辨率
  viewer.resolutionScale = window.devicePixelRatio || 1;
  // 不显示底图
  viewer.imageryLayers.get(0).show = false;
  // 去除logo
  viewer.cesiumWidget.creditContainer.style.display = "none";
  // 抗锯齿
  viewer.scene.fxaa = true;
  viewer.scene.postProcessStages.fxaa.enabled = true;
  // 深度检测
  viewer.scene.globe.depthTestAgainstTerrain = true;
  // 外天空盒
  viewer.scene.skyBox = new Cesium.SkyBox({
    sources: {
      positiveX: "/images/Standard-Cube-Map/px1.png",
      negativeX: "/images/Standard-Cube-Map/nx1.png",
      positiveY: "/images/Standard-Cube-Map/pz.png",
      negativeY: "/images/Standard-Cube-Map/nz1.png",
      positiveZ: "/images/Standard-Cube-Map/py.png",
      negativeZ: "/images/Standard-Cube-Map/ny1.png",
    },
  });

  // 调试使用
  window.viewer = viewer;
  // 监听点击事件，拾取坐标
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((e) => {
    const clickPosition = viewer.scene.camera.pickEllipsoid(e.position);
    const randiansPos = Cesium.Cartographic.fromCartesian(clickPosition);
    console.log(
      "经度：" +
        Cesium.Math.toDegrees(randiansPos.longitude) +
        ", 纬度：" +
        Cesium.Math.toDegrees(randiansPos.latitude)
    );
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

  window.__getCameraInfo = () => getcameraInfo(viewer);
  viewer.camera.setView({
    // Cesium的坐标是以地心为原点，一向指向南美洲，一向指向亚洲，一向指向北极州
    // fromDegrees()方法，将经纬度和高程转换为世界坐标
    destination: Cesium.Cartesian3.fromDegrees(
      112.201427213312257,
      31.14038434152244,
      1000000
    ),
    orientation: {
      // 指向
      heading: 6.283185307179581,
      // 视角
      pitch: -1.5688168484696687,
      roll: 0.0,
    },
  });
};
</script>

<template>
  <el-container>
    <!--  <el-aside>
      <Menu></Menu>
    </el-aside> -->
    <el-container>
      <el-main>
        <div id="cesiumContainer"></div>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
#cesiumContainer {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}

.el-header {
  height: 30px;
}

.el-container {
  height: 100vh;
}

.el-main {
  padding: 0 !important;
  position: relative;
}

.el-aside {
  width: auto;
}
</style>
