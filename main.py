import cityinfo
import config
import time
from time import localtime
from requests import get, post
from datetime import datetime, date

# 微信获取token
def get_access_token():
    # appId
    app_id = config.app_id
    # appSecret
    app_secret = config.app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        response = get(post_url)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"获取access_token失败: {e}")
        return None

# 获取城市天气
def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # 毫秒级时间戳
    t = (int(round(time.time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    try:
        response = get(url, headers=headers)
        response.encoding = "utf-8"
        response_data = response.text.split(";")[0].split("=")[-1]
        response_json = eval(response_data)
        weatherinfo = response_json["weatherinfo"]
        # 天气
        weather = weatherinfo["weather"]
        # 最高气温
        temp = weatherinfo["temp"]
        # 最低气温
        tempn = weatherinfo["tempn"]
        return weather, temp, tempn
    except Exception as e:
        print(f"获取天气信息失败: {e}")
        return None, None, None

# 发送每日信息
def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature):
    if access_token is None:
        return
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    # 星期几
    week = week_list[today.weekday()]
    # 获取在一起的日子的日期格式
    love_year = int(config.love_date.split("-")[0])
    love_month = int(config.love_date.split("-")[1])
    love_day = int(config.love_date.split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取生日的月和日
    birthday_month = int(config.birthday.split("-")[1])
    birthday_day = int(config.birthday.split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    # 获取天行数据每日一句
    txUrl = "http://api.tianapi.com/caihongpi/index"
    key = config.good_Night_Key
    pre_data = {"key": key}
    try:
        r = post(txUrl, params=pre_data, headers=headers)
        r.raise_for_status()
        good_Night = r.json()["newslist"][0]["content"]
        theuser = to_user[0]
        data = {
            "touser": theuser,
            "template_id": config.template_id1,
            "url": "http://weixin.qq.com/download",
            "topcolor": "#FF0000",
            "data": {
                "date": {
                    "value": "{} {}".format(today, week),
                    "color": "#00FFFF"
                },
                "city": {
                    "value": city_name,
                    "color": "#808A87"
                },
                "weather": {
                    "value": weather,
                    "color": "#ED9121"
                },
                "min_temperature": {
                    "value": min_temperature,
                    "color": "#00FF00"
                },
                "max_temperature": {
                    "value": max_temperature,
                    "color": "#FF6100"
                },
                "love_day": {
                    "value": love_days,
                    "color": "#87CEEB"
                },
                "birthday": {
                    "value": birth_day,
                    "color": "#FF8000"
                },
                "goodNight": {
                    "value": good_Night,
                    "color": "#87CEEB"
                }
            }
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        response = post(url, headers=headers, json=data)
        response.raise_for_status()
        print("每日信息推送成功")
    except Exception as e:
        print(f"每日信息推送失败: {e}")

# 发送课程消息
def send_Class_Message(to_user, access_token, classInfo):
    if access_token is None:
        return
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    theuser = to_user[0]
    data = {
        "touser": theuser,
        "template_id": config.template_id2,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "classInfo": {
                "value": classInfo,
                "color": "#FF8000"
            }
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
        print("课程信息推送成功！")
    except Exception as e:
        print(f"课程信息推送失败: {e}")

# 计算时间差（秒）
def calculate_Time_Difference(time1, time2):
    t1 = datetime.strptime(time1, '%H:%M:%S')
    t2 = datetime.strptime(time2, '%H:%M:%S')
    return (t1 - t2).total_seconds()

# 发送晚安心语
def send_Good_Night(to_user, access_token):
    # 这里需要根据实际需求实现晚安心语的发送逻辑
    print("晚安心语发送逻辑待实现")

if __name__ == '__main__':
    # 获取accessToken
    accessToken = get_access_token()
    print('token', accessToken)
    # 接收的用户
    user = config.user
    print('user:', user)
    # 传入省份和市获取天气信息
    province, city = config.province, config.city
    weather, max_temperature, min_temperature = get_weather(province, city)
    isPost = False
    # 公众号推送消息
    if datetime.now().strftime('%H:%M:%S') < config.post_Time:
        send_message(user, accessToken, city, weather, max_temperature, min_temperature)
        isPost = True
    # 课程提醒推送
    # 这里需要取消注释并确保相关函数和配置正确
    # todayClasses = get_Today_Class()
    # time_table = config.time_table
    # for i in range(len(time_table)):
    #     if isPost:
    #         break
    #     reminderTime = time_table[i]
    #     while True:
    #         nowTime = datetime.now().strftime('%H:%M:%S')
    #         print("当前时间:", nowTime)
    #         if reminderTime == nowTime:
    #             if len(todayClasses[i]) != 0:
    #                 classInfo = "课程信息: " + todayClasses[i] + "\n" + "上课时间: " + config.course_Time[i] + "\n"
    #                 print(classInfo)
    #                 send_Class_Message(user, accessToken, classInfo)
    #             isPost = True
    #             break
    #         elif reminderTime < nowTime:
    #             break
    #         # 通过睡眠定时
    #         defference = calculate_Time_Difference(reminderTime, nowTime) - 3
    #         print("课程推送时间差：", defference, "秒")
    #         if defference > 0:
    #             print("开始睡眠: 等待推送第", i + 1, "讲课")
    #             time.sleep(defference)
    #             print("结束睡眠")
    # 晚安心语推送
    # 这里需要取消注释并确保相关函数和配置正确
    # while True:
    #     goodNightTime = config.good_Night_Time
    #     nowTime = datetime.now().strftime('%H:%M:%S')
    #     if goodNightTime == nowTime:
    #         # 发送晚安心语
    #         send_Good_Night(user, accessToken)
    #         print("晚安心语推送成功！")
    #         break
    #     elif goodNightTime < nowTime:
    #         print("当前时间已过晚安心语推送设置的时间！")
    #         break
    #     elif calculate_Time_Difference(goodNightTime, nowTime) > 120:
    #         break
    #     # 通过睡眠定时
    #     defference = calculate_Time_Difference(goodNightTime, nowTime) - 3
    #     print("晚安心语推送时间差：", defference, "秒")
    #     if defference > 0:
    #         print("开始睡眠:等待推送晚安心语")
    #         time.sleep(defference)
    #         print("结束睡眠")
