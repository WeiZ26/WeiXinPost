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
    # 定义headers变量
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    # 获取天行数据每日一句
    # 注意：这一行和下面的代码应该与上面的代码保持相同的缩进级别
    txUrl = "http://apis.tianapi.com/saylove/index"  # 确保这一行与上面的代码对齐
    key = config.good_Night_Key
    pre_data = {"key": key}
    try:
        r = post(txUrl, params=pre_data, headers=headers)
        r.raise_for_status()
        data = r.json()
        if "result" in data and "content" in data["result"]:
            good_Night = data["result"]["content"]
        else:
            print(f"API响应格式异常: {data}")
            good_Night = "今日问候语获取失败"
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
        response = post(url, headers=headers, json=data)
        response.raise_for_status()
        print("每日信息推送成功")
    except Exception as e:
        print(f"每日信息推送失败: {e}")

# 计算时间差（秒）
def calculate_Time_Difference(time1, time2):
    t1 = datetime.strptime(time1, '%H:%M:%S')
    t2 = datetime.strptime(time2, '%H:%M:%S')
    return (t1 - t2).total_seconds()

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
    send_message(user, accessToken, city, weather, max_temperature, min_temperature)
    isPost = True
