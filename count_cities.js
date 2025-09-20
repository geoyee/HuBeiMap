const fs = require('fs');

try {
  const data = JSON.parse(fs.readFileSync('public/red.geojson', 'utf8'));
  const cityCount = {};
  
  data.features.forEach(feature => {
    const region = feature.properties.region;
    cityCount[region] = (cityCount[region] || 0) + 1;
  });
  
  console.log('各市建筑数量统计：');
  Object.entries(cityCount)
    .sort((a, b) => b[1] - a[1])
    .forEach(([city, count]) => {
      console.log(`${city}: ${count}个建筑`);
    });
    
  // 输出为 JSON 格式，便于在代码中使用
  console.log('\nJSON 格式：');
  console.log(JSON.stringify(cityCount, null, 2));
  
} catch (error) {
  console.error('错误:', error.message);
}
