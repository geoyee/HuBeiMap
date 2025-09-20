<!--
 * @Author: WangTao borderpanda@163.com
 * @Date: 2025-09-19 17:42:34
 * @LastEditors: WangTao borderpanda@163.com
 * @LastEditTime: 2025-09-19 18:39:01
 * @Description: 
-->
<script setup>
import * as Cesium from "cesium";
import { onMounted, onUnmounted, ref } from "vue";
import { getGeojson } from "@/common/api/api.js";
import modifyMap from "@/utils/cesiumCtrl/modifyMap.js";
import OperateBox from "@/components/OperateBox.vue";

const { viewer } = window;
// viewer.scene.terrainProvider = Cesium.createWorldTerrain(); // 提供地形
const getImgSrc = (name) => {
  return new URL(`/images/${name}`, import.meta.url)
    .href;
};



const onStart = async () => {
  const { res } = await getGeojson("/json/Hubei.geojson");
  const { features } = res;

  // 处理所有features
  const allHoles = [];
  const allLines = [];

  features.forEach((feature, index) => {
    const maskpointArray = [];
    const coordinates = feature.geometry.coordinates;

    // 处理不同的几何类型
    let coordArray;
    if (feature.geometry.type === "Polygon") {
      coordArray = coordinates[0]; // Polygon的第一个环
    } else if (feature.geometry.type === "MultiPolygon") {
      coordArray = coordinates[0][0]; // MultiPolygon的第一个多边形的第一个环
    } else {
      coordArray = coordinates[0][0]; // 默认处理方式
    }

    for (let i = 0, l = coordArray.length; i < l; i++) {
      maskpointArray.push(coordArray[i][0]);
      maskpointArray.push(coordArray[i][1]);
    }

    var maskspoint = Cesium.Cartesian3.fromDegreesArray(maskpointArray);

    // 添加到孔洞数组
    allHoles.push({
      positions: maskspoint,
    });

    // 创建每个feature的边界线
    const line = new Cesium.Entity({
      id: `line_${index}`,
      polyline: {
        positions: maskspoint,
        width: 2, //边界线宽
        material: Cesium.Color.fromCssColorString("#fff"), //边界线颜色
        clampToGround: true, // 贴地
      },
    });
    allLines.push(line);
  });

  // 创建包含所有孔洞的区域
  const area = new Cesium.Entity({
    id: "combined_area",
    polygon: {
      hierarchy: {
        // 定义多边形的环区域
        positions: Cesium.Cartesian3.fromDegreesArray([
          100, 0, 100, 89, 160, 89, 160, 0,
        ]),
        // 定义多边形的孔洞 - 包含所有features
        holes: allHoles,
      },
      material: Cesium.Color.BLACK.withAlpha(0.9),
    },
  });

  createMask(res);
  // viewer.entities.add(area);

  // 添加所有边界线
  allLines.forEach((line) => {
    viewer.entities.add(line);
  });

  // 飞行到第一条线（或者可以计算所有线的边界）
  // if (allLines.length > 0) {
  //   viewer.flyTo(allLines[0], { duration: 1 });
  // }

  // dealEntity();
  getJson()
  drawRegionBillboards()
  drawBuildBillboards()
};

const createMask = (data) => {
  let features = data.features;
  let allHoles = [];

  // 处理所有features创建遮罩孔洞
  features.forEach((feature, index) => {
    let positionArray = [];
    const coordinates = feature.geometry.coordinates;

    // 处理不同的几何类型
    let coordArray;
    if (feature.geometry.type === "Polygon") {
      coordArray = coordinates[0]; // Polygon的第一个环
    } else if (feature.geometry.type === "MultiPolygon") {
      coordArray = coordinates[0][0]; // MultiPolygon的第一个多边形的第一个环
    } else {
      coordArray = coordinates[0][0]; // 默认处理方式
    }

    // 获取区域的经纬度坐标
    for (let i = 0; i < coordArray.length; i++) {
      let coor = coordArray[i];
      positionArray.push(coor[0]);
      positionArray.push(coor[1]);
    }

    // 添加到孔洞数组
    allHoles.push({
      positions: Cesium.Cartesian3.fromDegreesArray(positionArray),
    });

    // 为每个feature创建立体墙 - 创建多个Wall来模拟厚度
    const positions3D = Cesium.Cartesian3.fromDegreesArray(positionArray);

    // 主墙体
    /*    const entity3 = new Cesium.Entity({
         name: `动态立体墙_${index}`,
         wall: {
           positions: positions3D,
           maximumHeights: positions3D.map(() => 200),
           minimumHeights: positions3D.map(() => -200),
           material: Cesium.Color.fromCssColorString("#fb0d06").withAlpha(0.8),
         },
       }); */

    // 外层轮廓墙 - 稍微偏移来创建厚度效果
    const entity3Outline = new Cesium.Entity({
      name: `动态立体墙轮廓_${index}`,
      polyline: {
        positions: positions3D,
        width: 2.0, // 可调节的宽度
        material: Cesium.Color.fromCssColorString("#fb0d06"),
        clampToGround: true,
      },
    });

    viewer.entities.add(entity3Outline); // 先添加轮廓
    // 墙
    // viewer.entities.add(entity3);
  });

  // 创建包含所有孔洞的遮罩
  let polygonEntity = new Cesium.Entity({
    polygon: {
      hierarchy: {
        // 添加外部区域为1/4半圆，设置为180会报错
        positions: Cesium.Cartesian3.fromDegreesArray([
          0, 0, 0, 90, 179, 90, 179, 0,
        ]),
        // 中心挖空的"洞" - 包含所有features
        holes: allHoles,
      },
      material: Cesium.Color.fromCssColorString("#0C1F34"),
    },
  });
  // viewer.entities.add(polygonEntity);
};

// 获取城市建筑数量映射
const getCityBuildingCounts = async () => {
  try {
    const { res } = await getGeojson("/json/red.geojson");
    const { features } = res;

    const cityCount = {};
    features.forEach(feature => {
      const region = feature.properties.region;
      cityCount[region] = (cityCount[region] || 0) + 1;
    });

    return cityCount;
  } catch (error) {
    console.error("获取建筑数量失败:", error);
    return {};
  }
};

// 新增方法：绘制json/region.json的billboard点
const drawRegionBillboards = async () => {
  // 读取json/region.json文件
  const { res } = await getGeojson("/json/region.json");
  const { features } = res;

  // 获取城市建筑数量映射
  const cityBuildingCounts = await getCityBuildingCounts();


  // 创建billboard点
  features.forEach((feature, index) => {
    const { coordinates } = feature.geometry;
    const { NAME, QUHUADAIMA } = feature.properties;

    // 获取当前城市的建筑数量
    const buildingCount = cityBuildingCounts[NAME] || 0;

    // 创建城市名称标签实体
    const cityNameEntity = new Cesium.Entity({
      id: `region_name_${QUHUADAIMA}_${index}`,
      position: Cesium.Cartesian3.fromDegrees(coordinates[0], coordinates[1]),
      label: {
        text: NAME,
        font: '18px sans-serif',
        scale: 0.7,
        // style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        fillColor: Cesium.Color.fromCssColorString("#000"), // 城市名称为白色
        verticalOrigin: Cesium.VerticalOrigin.TOP,
        pixelOffset: new Cesium.Cartesian2(0, 0), // 城市名称在上方
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        style: Cesium.LabelStyle.FILL,
        backgroundPadding: new Cesium.Cartesian2(8, 4),
        showBackground: true,
        backgroundColor: Cesium.Color.PINK, 
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(
          80000,
          3000000
        ),
        scaleByDistance: new Cesium.NearFarScalar(1.5e2, 2.0, 1.5e7, 0.5),
      },
      // 添加自定义属性用于交互
      properties: {
        name: NAME,
        code: QUHUADAIMA,
        data: feature.properties,
        type: 'region_billboard'
      }
    });

    viewer.entities.add(cityNameEntity);

    // 如果有建筑数量，创建单独的数量标签
    if (buildingCount > 0) {
      const countEntity = new Cesium.Entity({
        id: `region_count_${QUHUADAIMA}_${index}`,
        position: Cesium.Cartesian3.fromDegrees(coordinates[0], coordinates[1]),
        label: {
          text: `（${buildingCount}）`,
          font: '18px sans-serif',
          scale: 0.7,
          style: Cesium.LabelStyle.FILL,
          fillColor: Cesium.Color.fromCssColorString("#f00"), // 建筑数量为红色
          outlineColor: Cesium.Color.fromCssColorString("#fff"),
          outlineWidth: 1,
          verticalOrigin: Cesium.VerticalOrigin.TOP,
          pixelOffset: new Cesium.Cartesian2(0, 30), // 数量显示在城市名称下方
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          backgroundColor: Cesium.Color.WHITE.withAlpha(0.8),
          backgroundPadding: new Cesium.Cartesian2(6, 3),
          distanceDisplayCondition: new Cesium.DistanceDisplayCondition(
            80000,
            3000000
          ),
          scaleByDistance: new Cesium.NearFarScalar(1.5e2, 1.8, 1.5e7, 0.4),
        },
        // 添加自定义属性
        properties: {
          name: NAME,
          code: QUHUADAIMA,
          count: buildingCount,
          type: 'region_count'
        }
      });

      viewer.entities.add(countEntity);
    }
  });

  // 添加点击事件处理
  addRegionClickHandler();
};

const drawBuildBillboards = async () => {
  // 读取json/region.json文件
  const { res } = await getGeojson("/json/red.geojson");
  const { features } = res;

  // 创建billboard点
  features.forEach((feature, index) => {
    const { coordinates } = feature.geometry;
    const { region, landmarkName } = feature.properties;

    // 创建billboard实体
    const billboardEntity = new Cesium.Entity({
      id: `build_billboard_${region}_${index}`,
      position: Cesium.Cartesian3.fromDegrees(coordinates[0], coordinates[1]),
      label: {
        text: landmarkName,
        font: '22px sans-serif',
        scale: 1, // 标签的大小的放大倍数
        // horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
        // verticalOrigin: Cesium.VerticalOrigin.BOTTOM
        style: Cesium.LabelStyle.FILL_AND_OUTLINE, // 字体样式
        fillColor: Cesium.Color.fromCssColorString("#f00"), // 字体填充色
        outlineWidth: 1, // 字体外圈线宽度（同样也有颜色可设置）
        outlineColor: Cesium.Color.fromCssColorString("#666"),
        verticalOrigin: Cesium.VerticalOrigin.TOP, // 垂直位置
        pixelOffset: new Cesium.Cartesian2(0, -75), // 中心位置
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        showBackground: true,
        backgroundColor: Cesium.Color.fromCssColorString("#666").withAlpha(0.2), 
        backgroundPadding: new Cesium.Cartesian2(10, 6),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(
          50,
          80000
        ),
      },
      billboard: {
        image: '/images/dj.png', // 使用标记图标
        scale: 0.8,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        disableDepthTestDistance: Number.POSITIVE_INFINITY, // 始终显示在最前面
        width: 50,
        height: 50,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(
          50,
          80000
        ),
      },

      // 添加自定义属性用于交互
      properties: {
        data: feature.properties,
        type: 'build_billboard'
      }
    });

    viewer.entities.add(billboardEntity);
  });

};

const getCartesian = (
  position,
  viewer
) => {
  const mapScene = viewer.scene;
  let cartesian;
  // 在模型上获取点击对象
  const pickedObject = mapScene.pick(position);
  if (Cesium.defined(pickedObject) && mapScene.pickPositionSupported) {
    // 取得点击的空间坐标
    cartesian = mapScene.pickPosition(position);

    if (cartesian) {
      // 根据坐标系标准，将笛卡尔坐标转换为地理坐标,cartographic单位:弧度
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
      if (cartographic.height < 0) {
        const ray = viewer.camera.getPickRay(position);
        // 在地形上重新获取坐标
        cartesian = mapScene.globe.pick(ray, mapScene);
      }
    }
  }
  // 在地形上
  if (!Cesium.defined(cartesian)) {
    const ray = viewer.camera.getPickRay(position);
    cartesian = mapScene.globe.pick(ray, mapScene);
  }

  // 在椭球体上
  if (!Cesium.defined(cartesian)) {
    cartesian = mapScene.camera.pickEllipsoid(
      position,
      mapScene.globe.ellipsoid
    );
  }
  return cartesian;
};

// 专门为region billboard添加点击事件处理
const addRegionClickHandler = () => {
  viewer.cesiumWidget.screenSpaceEventHandler.setInputAction((event) => {
    const pickedObject = viewer.scene.pick(event.position);

    if (Cesium.defined(pickedObject) && Cesium.defined(pickedObject.id)) {
      const entity = pickedObject.id;

      // 检查是否是region billboard点或count点
      if (entity.properties && entity.properties.type &&
        (entity.properties.type.getValue() === 'region_billboard' ||
          entity.properties.type.getValue() === 'region_count')) {
        const name = entity.properties.name.getValue();
        const code = entity.properties.code.getValue();

        console.log(`点击了地区: ${name} (${code})`);
        // 根据城市类型设置不同的飞行高度
        const getCityFlyHeight = (cityName) => {
          // 主要城市使用较低高度以便更好查看
          const majorCities = ['武汉市', '宜昌市', '襄阳市', '荆州市', '黄冈市'];
          if (majorCities.includes(cityName)) {
            return 100000; 
          }
          // 其他城市使用标准高度
          return 140000; 
        };
        const flyHeight = getCityFlyHeight(name);

        // 将世界坐标转换为经纬度
        const cartesian = getCartesian(event.position, viewer)
        if (cartesian) {
          const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
          // 经度
          const longitude = +Cesium.Math.toDegrees(cartographic.longitude).toFixed(8);
          // 纬度
          const latitude = +Cesium.Math.toDegrees(cartographic.latitude).toFixed(8);
          // 相机飞行到该地区
          viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(longitude, latitude, flyHeight),
            orientation: {
              heading: Cesium.Math.toRadians(0.0),
              pitch: Cesium.Math.toRadians(-45.0), // 45度俯视角
              roll: 0.0
            },
            duration: 1.0 // 飞行时间1秒
          });
        }




      }
      // 检查是否是build billboard点
      if (entity.properties && entity.properties.type && entity.properties.type.getValue() === 'build_billboard') {
        const data = entity.properties.data.getValue();
        console.log(`点击了建筑:--${JSON.stringify(data)} `);
        buildInfo.value = data;
        dialogVisible.value = true;
        // 显示详细信息
        // alert(`您点击了: ${name}\n区划代码: ${code}`);
      }
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
};



const onClear = () => {
  viewer.scene.primitives.removeAll();
  viewer.entities.removeAll();
  // 清除事件处理器
  viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_CLICK);
};

const getJson = async () => {
  const { res } = await getGeojson("/json/Hubei.geojson");
  addDataToGlobe(res.features,);
};

const addDataToGlobe = (features,) => {
  let instances = [];
  for (let i = 0; i < features.length; i++) {
    const curFeatures = features[i];
    for (let j = 0; j < curFeatures.geometry.coordinates.length; j++) {
      const polygonArray = curFeatures.geometry.coordinates[j]
        .toString()
        .split(",")
        .map(Number);
      if (!polygonArray) continue;
      const polygon = new Cesium.PolygonGeometry({
        polygonHierarchy: new Cesium.PolygonHierarchy(
          Cesium.Cartesian3.fromDegreesArray(polygonArray)
        ),
        vertexFormat: Cesium.PerInstanceColorAppearance.VERTEX_FORMAT,
        // 设置面的拉伸高度
        extrudedHeight: 2000,
        // height: 100, // 多边形和椭球表面之间的距离（以米为单位）。
      });
      // console.log('---', polygon)
      // const polygonPositions = polygon.polygonHierarchy.getValue
      const geometry = Cesium.PolygonGeometry.createGeometry(polygon);
      instances.push(
        new Cesium.GeometryInstance({
          id: curFeatures.properties,
          geometry: geometry,
          attributes: {
            color: Cesium.ColorGeometryInstanceAttribute.fromColor(
              Cesium.Color.fromCssColorString(
                "rgba(206, 37, 49, 0.1)"
              )
            ),
            show: new Cesium.ShowGeometryInstanceAttribute(true),
            // color: Cesium.ColorGeometryInstanceAttribute.fromColor(Cesium.Color.fromRandom({ alpha: 0.7 })),
          },
        })
      );
    }


  }

  // 合并单个geometry,提高渲染效率
  const primitive = new Cesium.Primitive({
    releaseGeometryInstances: false,
    geometryInstances: instances,
    appearance: new Cesium.PerInstanceColorAppearance({
      translucent: true, // 当 true 时，几何体应该是半透明的，因此 PerInstanceColorAppearance#renderState 启用了 alpha 混合。
      closed: false, // 当 true 时，几何体应该是关闭的，因此 PerInstanceColorAppearance#renderState 启用了背面剔除。
    }),
    asynchronous: false,
  });
  viewer.scene.primitives.add(primitive);
};


// const scene = viewer.scene;
// const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);
// handler.setInputAction((e) => {
//   // 获取实体
//   const pick = scene.pick(e.position);
//   if (Cesium.defined(pick) && pick.id?.CITYCODE) {
//     console.log("xxx", pick.id, pick);

//     // 单击变色(TODO:遇到多个相同id的instance会失效)
//     // const attributes = pick.primitive.getGeometryInstanceAttributes(pick.id)
//     // console.log("----attributes---", attributes)
//     // attributes.color = Cesium.ColorGeometryInstanceAttribute.toValue(Cesium.Color.WHITE);

//     // viewer.camera.flyTo({
//     //   // 从以度为单位的经度和纬度值返回笛卡尔3位置。
//     //   destination: Cesium.Cartesian3.fromDegrees(...areaPointCenter[id], 40000),
//     //   orientation: {
//     //     // heading：默认方向为正北，正角度为向东旋转，即水平旋转，也叫偏航角。
//     //     // pitch：默认角度为-90，即朝向地面，正角度在平面之上，负角度为平面下，即上下旋转，也叫俯仰角。
//     //     // roll：默认旋转角度为0，左右旋转，正角度向右，负角度向左，也叫翻滚角
//     //     heading: Cesium.Math.toRadians(0.0), // 正东，默认北
//     //     pitch: Cesium.Math.toRadians(-90), // 向正下方看
//     //     roll: 0.0, // 左右
//     //   },
//     //   duration: 2, // 飞行时间（s）
//     // });
//   }
// }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
onMounted(async () => {
  modifyMap({
    viewer,
    style: "normal",
    changeColor: false,
  });
  onStart();
  
  // 初始化级联选择器数据
  options.value = await generateCascaderOptions();
});


onUnmounted(() => {
  onClear();
});

// 生成级联选择器的数据结构
const generateCascaderOptions = async () => {
  try {
    // 读取json/region.json和json/red.geojson数据
    const [regionResult, redResult] = await Promise.all([
      getGeojson("/json/region.json"),
      getGeojson("/json/red.geojson")
    ]);

    const regionFeatures = regionResult.res.features;
    const redFeatures = redResult.res.features;

    // 按城市分组红色建筑数据
    const buildingsByCity = {};
    redFeatures.forEach(building => {
      const cityName = building.properties.region;
      if (!buildingsByCity[cityName]) {
        buildingsByCity[cityName] = [];
      }
      buildingsByCity[cityName].push({
        value: building.properties.landmarkName,
        label: building.properties.landmarkName,
        data: {
          coordinates: building.geometry.coordinates,
          properties: building.properties
        }
      });
    });

    // 创建级联选择器选项
    const cascaderOptions = regionFeatures.map(region => {
      const cityName = region.properties.NAME;
      const cityBuildings = buildingsByCity[cityName] || [];
      
      return {
        value: cityName,
        label: `${cityName} (${cityBuildings.length})`,
        data: {
          coordinates: region.geometry.coordinates,
          properties: region.properties
        },
        children: cityBuildings
      };
    });

    return cascaderOptions;
  } catch (error) {
    console.error("生成级联选择器数据失败:", error);
    return [];
  }
};

const props1 = {
  checkStrictly: true,
}

// 初始化级联选择器数据
const options = ref([]);

// 级联选择器选中值
const cascaderValue = ref([]);

// 处理级联选择器变化
const handleCascaderChange = (value) => {
  if (!value || value.length === 0) return;
  
  // 获取选中的选项数据
  const findOptionData = (options, valuePath) => {
    let current = options;
    let data = null;
    
    for (let i = 0; i < valuePath.length; i++) {
      const item = current.find(option => option.value === valuePath[i]);
      if (item) {
        data = item.data;
        if (i < valuePath.length - 1 && item.children) {
          current = item.children;
        }
      }
    }
    return data;
  };
  
  const selectedData = findOptionData(options.value, value);
  
  if (selectedData && selectedData.coordinates) {
    const coordinates = selectedData.coordinates;
    let longitude, latitude;
    
    // 处理不同的坐标格式
    if (Array.isArray(coordinates) && coordinates.length >= 2) {
      if (typeof coordinates[0] === 'number') {
        // 点坐标格式 [longitude, latitude]
        [longitude, latitude] = coordinates;
      } else if (Array.isArray(coordinates[0])) {
        // 可能是多边形或其他复杂格式，取第一个点
        [longitude, latitude] = coordinates[0];
      }
    }
    
    if (longitude !== undefined && latitude !== undefined) {
      // 根据选择类型设置不同的飞行高度
      const flyHeight = value.length === 1 ? 200000 : 100000; // 城市或建筑
      
      // 相机飞行到选中位置
      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(longitude, latitude, flyHeight),
        orientation: {
          heading: Cesium.Math.toRadians(0.0),
          pitch: Cesium.Math.toRadians(-45.0),
          roll: 0.0
        },
        duration: 2.0
      });
      
      console.log(`飞行到: ${value.join(' -> ')} (${longitude.toFixed(4)}, ${latitude.toFixed(4)})`);
      
      // 如果选择的是建筑（二级菜单），显示详细信息
      if (value.length === 2 && selectedData.properties) {
        buildInfo.value = selectedData.properties;
        // dialogVisible.value = true;
      }
    }
  }
};

const dialogVisible = ref(false)
const buildInfo = ref({
  region: "武汉市",
  landmarkName: "八路军武汉办事处旧址",
  landmarkIntroduction: "八路军武汉办事处旧址位于武汉市江岸区长春街57号。1937年12月-1938年10月期间，这里是八路军在武汉的办事机构。旧址为一幢四层楼房，复原了当年的办公室、会议室、宿舍等场景，展示了八路军武汉办事处在宣传抗日、输送人员和物资、开展统一战线等方面的重要工作。",
  reflectedSpirit: "抗日统战精神",
  spiritConnotation: "积极倡导和推动抗日民族统一战线的团结协作精神；艰苦奋斗、无私奉献的工作作风。",
  historicalPeriod: "新民主主义革命时期",
  eventYear: "1937-1938年"
})
</script>
<template>
  <operate-box>
    <el-cascader 
      v-model="cascaderValue"
      :options="options" 
      :props="props1" 
      clearable 
      filterable
      @change="handleCascaderChange"
      placeholder="选择城市或建筑"
      style="width: 300px; margin: 10px 40px;"
    />
    <el-dialog v-model="dialogVisible" width="50%" :show-close="false">
      <template #header>
        <div class="dialog-title">
          <span class="intro">
            <img class="icon" src="/images/jingqu.png" />
            <span class="landmarkName">{{ buildInfo.landmarkName }}</span>
          </span>
          <div class="location">{{ buildInfo.region }}</div>
          <div class="close" @click="dialogVisible = false">——</div>
        </div>
      </template>
      <div class="dialog-content">
        <div class="dialog-content-item">
          <div class="label">地标简介</div>
          <span class="value">{{ buildInfo.landmarkIntroduction }}</span>
        </div>

        <div class="dialog-content-item js">
          <div class="label">{{ buildInfo.reflectedSpirit }}</div>
          <span class="value">{{ buildInfo.spiritConnotation }}</span>
        </div>

        <div class="dialog-content-item time-item">
          <div class="time">
            {{ buildInfo.historicalPeriod }}
          </div>
          <div class="activity">
            {{ buildInfo.eventYear }}

          </div>
        </div>

      </div>
    </el-dialog>
  </operate-box>
</template>
<style scoped lang="less">
.landmarkName {
  font-size: 22px;
}

.dialog-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px;
  position: relative;

  .close {
    position: absolute;
    right: -10px;
    top: -15px;
    cursor: pointer;
    width: 18px;
    height: 18px;
    line-height: 15px;
    text-align: center;
    background-color: #f7e7e7;
    border-radius: 50%;
    color: #b12834;
    font-weight: bold;
    font-size: 16px;
  }
}

.icon {
  width: 16px;
  height: 16px;
  margin-right: 12px;
}

.location {
  padding: 4px 15px;
  border-radius: 25px;
  background-color: rgba(255, 255, 255, 0.3);
  margin-right: 10px;
}

.dialog-content {
  padding: 15px;
  color: #000;

  .dialog-content-item {
    margin: 10px 0;

    .label {
      font-size: 16px;
      color: #771921;
      font-weight: bold;
    }
  }
}

.dialog-content .js {
  background-color: #f8c9d1;
  padding: 10px;
  border-radius: 10px;

  .label {
    margin-bottom: 5px;
  }
}

.dialog-content .time-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;

  &>div {
    border-radius: 10px;
  }

  .time {
    background-color: #f7e7e7;
    padding: 10px;
    color: #b12834;
    font-weight: 700;
    flex: 1;
  }

  .activity {
    background-color: #f2f2f0;
    padding: 10px;
    color: #696964;
    flex: 1;
  }
}
</style>
<style lang="less">
.el-dialog {
  padding: 0;
  border-radius: 10px;

  .el-dialog__header {
    padding: 10px 5px;
    background-color: #bc2729;
    color: #fff;
    border-radius: 10px 10px 0 0;
  }
}

</style>
