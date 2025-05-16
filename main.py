import cityinfo
import config
import time
from time import localtime
from requests import get, post
from datetime import datetime, date

# 微信获取token
def get_access_token():
    app_id = config.app_id
    app_secret = config.app_secret
    post_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    try:
        response = get(post_url)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"获取access_token失败: {e}")
        return None

# 获取城市天气
def get_weather(province, city):
    try:
        city_id = cityinfo.cityInfo[province][city]["AREAID"]
        t = int(round(time.time() * 1000))
        headers = {
            "Referer": f"http://www.weather.com.cn/weather1d/{city_id}.shtml",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        url = f"http://d1.weather.com.cn/dingzhi/{city_id}.html?_={t}"
        response = get(url, headers=headers)
        response.encoding = "utf-8"
        response_data = response.text.split(";")[0].split("=")[-1]
        response_json = eval(response_data)
        weatherinfo = response_json["weatherinfo"]
        return weatherinfo["weather"], weatherinfo["temp"], weatherinfo["tempn"]
    except Exception as e:
        print(f"获取天气信息失败: {e}")
        return None, None, None

# 获取合适长度的每日信息
def get_daily_message(max_length=20, max_retries=3):
    txUrl = "http://apis.tianapi.com/saylove/index"
    key = config.good_Night_Key
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            r = post(txUrl, params={"key": key}, headers=headers)
            r.raise_for_status()
            data = r.json()
            
            if "result" in data and "content" in data["result"]:
                content = data["result"]["content"]
                if len(content) <= max_length:
                    return f"🌞 {content}"  # 拼接表情并返回
                else:
                    print(f"获取的内容长度 {len(content)} 超过限制 {max_length}，尝试重试")
            else:
                print(f"API响应格式异常: {data}")
                
        except Exception as e:
            print(f"第 {attempt+1} 次获取每日信息失败: {e}")
            
        time.sleep(1)  # 简单延迟避免请求过快
        
    return "今日问候语获取失败"  # 所有重试都失败后返回默认值

# 发送每日信息
def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature):
    if access_token is None:
        return
        
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    today = datetime.now().date()
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week = week_list[today.weekday()]
    
    # 计算恋爱天数
    love_date = date(
        int(config.love_date.split("-")[0]),
        int(config.love_date.split("-")[1]),
        int(config.love_date.split("-")[2])
    )
    love_days = (today - love_date).days
    
    # 获取合适长度的每日信息
    good_Night = get_daily_message()
    
    data = {
        "touser": to_user[0],
        "template_id": config.template_id1,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {"value": f"{today} {week}", "color": "#173177"},
            "city": {"value": city_name, "color": "#173177"},
            "weather": {"value": weather, "color": "#173177"},
            "min_temperature": {"value": min_temperature, "color": "#173177"},
            "max_temperature": {"value": max_temperature, "color": "#173177"},
            "love_day": {"value": str(love_days), "color": "#173177"},
            "goodNight": {"value": good_Night, "color": "#173177"}
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    
    try:
        response = post(url, headers=headers, json=data)
        response.raise_for_status()
        print("每日信息推送成功")
    except Exception as e:
        print(f"每日信息推送失败: {e}")
        if response.status_code != 200:
            print(f"微信API返回: {response.text}")

# 计算时间差（秒）
def calculate_Time_Difference(time1, time2):
    t1 = datetime.strptime(time1, '%H:%M:%S')
    t2 = datetime.strptime(time2, '%H:%M:%S')
    return (t1 - t2).total_seconds()

if __name__ == '__main__':
    print(f"开始执行程序: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取accessToken
    accessToken = get_access_token()
    print('token:', accessToken)
    
    # 接收的用户
    user = config.user
    print('user:', user)
    
    # 获取天气信息
    province, city = config.province, config.city
    weather, max_temperature, min_temperature = get_weather(province, city)
    
    if None in (weather, max_temperature, min_temperature):
        print("获取天气失败，程序退出")
    else:
        print(f"天气信息: {city} {weather} {min_temperature}~{max_temperature}")
        send_message(user, accessToken, city, weather, max_temperature, min_temperature)
