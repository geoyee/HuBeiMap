import { bbox, coordAll } from "@turf/turf";
import * as Cesium from "cesium";

/**
 * 定位到 features
 * @param {*} features features 集合，或者 feature 对象，FeatureCollection | Feature
 * @param {*} callBack 飞行完执行的回调
 * @returns
 */
export const flyToFeatures = (
    cesiumViewer,
    features,
    callBack
  ) => {
    if (!features) {
      return;
    }
    const bboxPoints = bbox(features);
    Cesium.OrientedBoundingBox.fromPoints(Cesium.Cartesian3.fromDegreesArray(bboxPoints));
    if (bboxPoints) {
      const nw = Cesium.Cartesian3.fromDegrees(bboxPoints[0], bboxPoints[1]);
      const se = Cesium.Cartesian3.fromDegrees(bboxPoints[2], bboxPoints[3]);
      flyToRectangle(cesiumViewer, [nw, se], features, callBack);
    }
  };
  
  /**
   * 定位到矩形
   * @param cesiumViewer Viewer
   * @param cartesians {Cesium.Cartesian3[]} 笛卡尔坐标数组
   * @param callBack  回调函数
   * @param heading {orientation} HeadingPitchRollValues.heading
   * @param pitch HeadingPitchRollValues.pitch
   * @param scale HeadingPitchRollValues.scale
   * @param duration 过渡时间(s)
   * @returns
   */
  export const flyToRectangle = (
    cesiumViewer,
    cartesians,
    feature,
    callBack,
    heading = 0.0,
    pitch = -90,
    scale = 2,
    duration = 1
  ) => {
    if (!cesiumViewer) {
      console.log("三维球未初始化！");
      return;
    }
    if (!Array.isArray(cartesians)) {
      console.log("定位范围不对！");
      return;
    }
    if (scale < 0.1) {
      scale = 1.0;
    }
    // 从所有feature中获取坐标
    const coords = coordAll(feature);
    // 判断有无高度
    const hasHeight = coords[0].length > 2;
    //  拍平坐标数组
    const points = hasHeight
      ? Cesium.Cartesian3.fromDegreesArrayHeights(coords.flat())
      : Cesium.Cartesian3.fromDegreesArray(coords.flat());
    // 生成BoundingSphere
    const boundingSphere = Cesium.BoundingSphere.fromPoints(points);
    cesiumViewer.camera.flyToBoundingSphere(boundingSphere, {
      duration,
      maximumHeight: undefined,
      complete() {
        if (callBack) {
          callBack();
        } else {
          console.log("定位失败！");
        }
      },
      cancel() {
        console.log("定位取消！");
      },
      offset: {
        heading: Math.toRadians(heading),
        pitch: Math.toRadians(pitch),
        range: 0.0
      }
    });
  };
  