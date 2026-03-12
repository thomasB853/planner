import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 设置页面配置
st.set_page_config(
    page_title="个人行程计划",
    page_icon="🗓️",
    layout="wide"
)

# 初始化数据存储
def init_data():
    """初始化行程数据文件"""
    if not os.path.exists("trips.json"):
        with open("trips.json", "w", encoding="utf-8") as f:
            json.dump([], f)

# 加载行程数据
def load_trips():
    """加载所有行程数据"""
    init_data()
    with open("trips.json", "r", encoding="utf-8") as f:
        try:
            trips = json.load(f)
            # 转换日期字符串为datetime对象
            for trip in trips:
                trip["start_date"] = datetime.strptime(trip["start_date"], "%Y-%m-%d")
                trip["end_date"] = datetime.strptime(trip["end_date"], "%Y-%m-%d")
            return trips
        except:
            return []

# 保存行程数据
def save_trip(trip):
    """保存单个行程"""
    trips = load_trips()
    # 转换datetime对象为字符串
    trip_copy = trip.copy()
    trip_copy["start_date"] = trip_copy["start_date"].strftime("%Y-%m-%d")
    trip_copy["end_date"] = trip_copy["end_date"].strftime("%Y-%m-%d")
    
    # 检查是否是编辑（有id）
    for i, t in enumerate(trips):
        if t.get("id") == trip.get("id"):
            trips[i] = trip_copy
            break
    else:
        # 新增行程，生成唯一ID
        trip_copy["id"] = len(trips) + 1 if trips else 1
        trips.append(trip_copy)
    
    with open("trips.json", "w", encoding="utf-8") as f:
        json.dump(trips, f, ensure_ascii=False, indent=4)

# 删除行程
def delete_trip(trip_id):
    """删除指定ID的行程"""
    trips = load_trips()
    # 过滤掉要删除的行程
    trips = [t for t in trips if t.get("id") != trip_id]
    
    # 重新保存
    with open("trips.json", "w", encoding="utf-8") as f:
        json.dump(trips, f, ensure_ascii=False, indent=4)

# 主页面
def main():
    st.title("🗓️ 个人行程计划管理")
    
    # 侧边栏
    st.sidebar.header("功能菜单")
    menu_option = st.sidebar.radio(
        "选择操作",
        ["添加行程", "查看所有行程", "行程统计", "编辑/删除行程"]
    )
    
    # 添加行程
    if menu_option == "添加行程":
        st.subheader("添加新行程")
        
        col1, col2 = st.columns(2)
        with col1:
            trip_name = st.text_input("行程名称*", placeholder="例如：周末爬山")
            trip_type = st.selectbox("行程类型*", ["工作", "休闲", "学习", "旅行", "其他"])
            start_date = st.date_input("开始日期*", datetime.now())
        
        with col2:
            trip_desc = st.text_area("行程描述", placeholder="输入行程详情...")
            end_date = st.date_input("结束日期*", datetime.now() + timedelta(days=1))
            trip_priority = st.slider("优先级 (1-5)", 1, 5, 3)
        
        if st.button("保存行程", type="primary"):
            if not trip_name or not trip_type:
                st.error("请填写必填项（*）！")
            elif end_date < start_date:
                st.error("结束日期不能早于开始日期！")
            else:
                new_trip = {
                    "name": trip_name,
                    "type": trip_type,
                    "description": trip_desc,
                    "start_date": start_date,
                    "end_date": end_date,
                    "priority": trip_priority,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_trip(new_trip)
                st.success(f"✅ 行程「{trip_name}」添加成功！")
                st.balloons()
    
    # 查看所有行程
    elif menu_option == "查看所有行程":
        st.subheader("所有行程列表")
        
        trips = load_trips()
        if not trips:
            st.info("暂无行程数据，快去添加吧！")
        else:
            # 转换为DataFrame方便展示
            df = pd.DataFrame(trips)
            # 只显示关键列
            display_df = df[["id", "name", "type", "start_date", "end_date", "priority"]]
            display_df.columns = ["ID", "行程名称", "类型", "开始日期", "结束日期", "优先级"]
            
            # 添加筛选功能
            st.sidebar.subheader("筛选条件")
            type_filter = st.sidebar.multiselect(
                "按类型筛选",
                options=["工作", "休闲", "学习", "旅行", "其他"],
                default=[]
            )
            
            if type_filter:
                display_df = display_df[display_df["类型"].isin(type_filter)]
            
            # 显示表格
            st.dataframe(display_df, use_container_width=True)
            
            # 导出功能
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 导出行程数据 (CSV)",
                data=csv,
                file_name=f"行程计划_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # 行程统计
    elif menu_option == "行程统计":
        st.subheader("行程数据统计")
        
        trips = load_trips()
        if not trips:
            st.info("暂无行程数据，无法统计！")
        else:
            df = pd.DataFrame(trips)
            
            col1, col2 = st.columns(2)
            with col1:
                # 按类型统计
                type_count = df["type"].value_counts()
                st.write("📊 行程类型分布")
                st.bar_chart(type_count)
            
            with col2:
                # 按优先级统计
                priority_count = df["priority"].value_counts().sort_index()
                st.write("⭐ 行程优先级分布")
                st.line_chart(priority_count)
            
            # 基本统计信息
            st.write("### 基本统计")
            total_trips = len(trips)
            avg_priority = df["priority"].mean()
            upcoming_trips = len([t for t in trips if t["start_date"] >= datetime.now()])
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            stats_col1.metric("总行程数", total_trips)
            stats_col2.metric("平均优先级", f"{avg_priority:.1f}")
            stats_col3.metric("待执行行程", upcoming_trips)
    
    # 编辑/删除行程
    elif menu_option == "编辑/删除行程":
        st.subheader("编辑或删除行程")
        
        trips = load_trips()
        if not trips:
            st.info("暂无行程数据！")
        else:
            # 选择要操作的行程
            trip_options = {f"{t['id']} - {t['name']}": t for t in trips}
            selected_trip_key = st.selectbox(
                "选择要操作的行程",
                list(trip_options.keys())
            )
            
            selected_trip = trip_options[selected_trip_key]
            
            # 显示行程详情
            st.write("#### 行程详情")
            st.write(f"**名称：** {selected_trip['name']}")
            st.write(f"**类型：** {selected_trip['type']}")
            st.write(f"**时间：** {selected_trip['start_date'].strftime('%Y-%m-%d')} 至 {selected_trip['end_date'].strftime('%Y-%m-%d')}")
            st.write(f"**优先级：** {'⭐' * selected_trip['priority']}")
            st.write(f"**描述：** {selected_trip['description']}")
            
            # 编辑表单
            with st.expander("编辑行程"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("行程名称", value=selected_trip['name'])
                    new_type = st.selectbox("行程类型", ["工作", "休闲", "学习", "旅行", "其他"], 
                                          index=["工作", "休闲", "学习", "旅行", "其他"].index(selected_trip['type']))
                    new_start = st.date_input("开始日期", selected_trip['start_date'])
                
                with col2:
                    new_desc = st.text_area("行程描述", value=selected_trip['description'])
                    new_end = st.date_input("结束日期", selected_trip['end_date'])
                    new_priority = st.slider("优先级", 1, 5, selected_trip['priority'])
                
                if st.button("更新行程"):
                    updated_trip = {
                        "id": selected_trip['id'],
                        "name": new_name,
                        "type": new_type,
                        "description": new_desc,
                        "start_date": new_start,
                        "end_date": new_end,
                        "priority": new_priority,
                        "created_at": selected_trip.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                    save_trip(updated_trip)
                    st.success("✅ 行程更新成功！")
            
            # 删除行程
            st.warning("⚠️ 以下操作不可恢复！")
            if st.button("删除此行程", type="secondary"):
                delete_trip(selected_trip['id'])
                st.error(f"❌ 行程「{selected_trip['name']}」已删除！")
                st.rerun()

# 运行应用
if __name__ == "__main__":
    main()