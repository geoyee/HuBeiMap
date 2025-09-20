#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel转JSON脚本
将Excel表格文件转换为JSON格式
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path

def excel_to_json(excel_file_path, output_json_path=None, sheet_name=None, encoding='utf-8'):
    """
    将Excel文件转换为JSON格式
    
    Args:
        excel_file_path (str): Excel文件路径
        output_json_path (str): 输出JSON文件路径，如果为None则自动生成
        sheet_name (str): 工作表名称，如果为None则读取所有工作表
        encoding (str): 输出JSON文件编码格式
    
    Returns:
        dict: 转换后的数据
    """
    
    try:
        # 检查输入文件是否存在
        if not os.path.exists(excel_file_path):
            raise FileNotFoundError(f"Excel文件不存在: {excel_file_path}")
        
        print(f"正在读取Excel文件: {excel_file_path}")
        
        # 读取Excel文件
        if sheet_name:
            # 读取指定工作表，跳过第一行（大标题行），第二行作为列名
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name, skiprows=1, header=0)
            
            # 清理列名，为空列名生成默认名称
            new_columns = []
            for i, col in enumerate(df.columns):
                if pd.isna(col) or str(col).strip() == '' or str(col) == 'Unnamed':
                    new_columns.append(f'列{i+1}')
                else:
                    new_columns.append(str(col).strip())
            
            df.columns = new_columns
            
            # 处理合并单元格：对于"地区"列，向下填充空值
            if '地区' in df.columns:
                df['地区'] = df['地区'].ffill()
            
            # 处理其他可能的合并单元格列
            for col in df.columns:
                if col in ['地区', '市', '县', '区域'] or '地区' in col:
                    df[col] = df[col].ffill()
            
            # 处理NaN值，将其转换为None
            df = df.where(pd.notnull(df), None)
            
            # 创建中英文字段映射
            chinese_to_english = {
                '地区': 'region',
                '地标名称': 'landmark_name', 
                '地标简介': 'description',
                '地标所反映的精神': 'spirit',
                '地标所反映的精神内涵': 'spirit_content',
                '地标所处时代': 'era',
                '反映事件年代': 'event_year'
            }
            
            # 创建英文到中文的映射（反过来）
            field_mapping = {english: chinese for chinese, english in chinese_to_english.items()}
            
            # 重命名列为英文
            df_renamed = df.copy()
            for chinese_name, english_name in chinese_to_english.items():
                if chinese_name in df_renamed.columns:
                    df_renamed = df_renamed.rename(columns={chinese_name: english_name})
            
            # 转换为字典列表
            data = df_renamed.to_dict('records')
            
            # 构建结果，包含字段描述
            result = {
                sheet_name: {
                    'desc': field_mapping,  # 字段映射描述（英文->中文）
                    'data': data  # 实际数据
                }
            }
        else:
            # 读取所有工作表
            excel_file = pd.ExcelFile(excel_file_path)
            result = {}
            
            for sheet in excel_file.sheet_names:
                print(f"正在处理工作表: {sheet}")
                # 跳过第一行（大标题行），第二行作为列名
                df = pd.read_excel(excel_file_path, sheet_name=sheet, skiprows=1, header=0)
                
                # 清理列名，为空列名生成默认名称
                new_columns = []
                for i, col in enumerate(df.columns):
                    if pd.isna(col) or str(col).strip() == '' or 'Unnamed' in str(col):
                        new_columns.append(f'列{i+1}')
                    else:
                        new_columns.append(str(col).strip())
                
                df.columns = new_columns
                
                # 处理合并单元格：对于"地区"列，向下填充空值
                if '地区' in df.columns:
                    df['地区'] = df['地区'].ffill()
                
                # 处理其他可能的合并单元格列
                for col in df.columns:
                    if col in ['地区', '市', '县', '区域'] or '地区' in col:
                        df[col] = df[col].ffill()
                
                # 处理NaN值，将其转换为None
                df = df.where(pd.notnull(df), None)
                
                # 创建中英文字段映射
                chinese_to_english = {
                    '地区': 'region',
                    '地标名称': 'landmark_name', 
                    '地标简介': 'description',
                    '地标所反映的精神': 'spirit',
                    '地标所反映的精神内涵': 'spirit_content',
                    '地标所处时代': 'era',
                    '反映事件年代': 'event_year'
                }
                
                # 创建英文到中文的映射（反过来）
                field_mapping = {english: chinese for chinese, english in chinese_to_english.items()}
                
                # 重命名列为英文
                df_renamed = df.copy()
                for chinese_name, english_name in chinese_to_english.items():
                    if chinese_name in df_renamed.columns:
                        df_renamed = df_renamed.rename(columns={chinese_name: english_name})
                
                # 转换为字典列表
                data = df_renamed.to_dict('records')
                
                # 构建结果，包含字段描述
                result[sheet] = {
                    'desc': field_mapping,  # 字段映射描述（英文->中文）
                    'data': data  # 实际数据
                }
                
                print(f"工作表 '{sheet}' 包含 {len(data)} 行数据")
        
        # 生成输出文件路径
        if output_json_path is None:
            excel_path = Path(excel_file_path)
            output_json_path = excel_path.parent / f"{excel_path.stem}.json"
        
        # 写入JSON文件
        print(f"正在写入JSON文件: {output_json_path}")
        with open(output_json_path, 'w', encoding=encoding) as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"转换完成！JSON文件已保存到: {output_json_path}")
        
        # 显示数据统计信息
        if sheet_name:
            sheet_info = result[sheet_name]
            if isinstance(sheet_info, dict) and 'data' in sheet_info:
                print(f"总共转换了 {len(sheet_info['data'])} 行数据")
            else:
                print(f"总共转换了 {len(sheet_info)} 行数据")
        else:
            total_rows = 0
            for sheet_info in result.values():
                if isinstance(sheet_info, dict) and 'data' in sheet_info:
                    total_rows += len(sheet_info['data'])
                else:
                    total_rows += len(sheet_info)
            print(f"总共转换了 {len(result)} 个工作表，{total_rows} 行数据")
        
        return result
        
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        return None

def main():
    """主函数"""
    
    # 默认Excel文件路径
    default_excel_file = "public/【浩睿咨询】湖北省红色教育资源库0918 - 副本 copy.xlsx"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        excel_file_path = sys.argv[1]
    else:
        excel_file_path = default_excel_file
    
    # 检查输出路径参数
    output_json_path = None
    if len(sys.argv) > 2:
        output_json_path = sys.argv[2]
    
    # 检查工作表名称参数
    sheet_name = None
    if len(sys.argv) > 3:
        sheet_name = sys.argv[3]
    
    print("=" * 50)
    print("Excel转JSON转换工具")
    print("=" * 50)
    print(f"输入文件: {excel_file_path}")
    print(f"输出文件: {output_json_path or '自动生成'}")
    print(f"工作表: {sheet_name or '所有工作表'}")
    print("=" * 50)
    
    # 执行转换
    result = excel_to_json(excel_file_path, output_json_path, sheet_name)
    
    if result:
        print("\n转换成功完成！")
        
        # 显示JSON结构预览
        print("\nJSON结构预览:")
        for sheet_name, sheet_info in result.items():
            print(f"工作表 '{sheet_name}':")
            if isinstance(sheet_info, dict) and 'data' in sheet_info:
                sheet_data = sheet_info['data']
                field_mapping = sheet_info.get('desc', {})
                print(f"  - 列数: {len(sheet_data[0]) if sheet_data else 0}")
                print(f"  - 行数: {len(sheet_data)}")
                if sheet_data:
                    print(f"  - 英文列名: {list(sheet_data[0].keys())}")
                print(f"  - 字段映射: {field_mapping}")
            else:
                # 兼容旧格式
                sheet_data = sheet_info
                if sheet_data:
                    print(f"  - 列数: {len(sheet_data[0]) if sheet_data else 0}")
                    print(f"  - 行数: {len(sheet_data)}")
                    if sheet_data:
                        print(f"  - 列名: {list(sheet_data[0].keys())}")
                else:
                    print("  - 空工作表")
            print()
    else:
        print("\n转换失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
