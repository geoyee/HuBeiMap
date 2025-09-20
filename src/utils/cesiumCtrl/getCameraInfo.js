import { Math } from "cesium";
/**
 * 获取相机位置，姿态等
 * @param {*} viewer
 * @returns
 */
export const getcameraInfo = (viewer) => {
    // 获取 相机姿态信息
    const head = viewer.scene.camera.heading;
    const pitch = viewer.scene.camera.pitch;
    const roll = viewer.scene.camera.roll;
    const info = { head: head, pitch: pitch, roll: roll };
    // 获取位置 wgs84的地心坐标系，x,y坐标值以弧度来表示
    const position = viewer.scene.camera.positionCartographic; //with longitude and latitude expressed in radians and height in meters.

    // 弧度转经纬度
    const longitude = Math.toDegrees(position.longitude).toFixed(6);
    const latitude = Math.toDegrees(position.latitude).toFixed(6);
    const height = position.height;
    return { lng: longitude, lat: latitude, h: height, mat: info, cartesian3Position: viewer.scene.camera.position };
};
