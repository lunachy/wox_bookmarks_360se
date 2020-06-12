# encoding=utf8

import sqlite3
import webbrowser
from pathlib import Path

import pinyin
from wox import Wox, WoxAPI


class Main(Wox):
    def get_pinyin_bookmarks(self, query=''):
        """获取书签的拼音数据"""
        db = "360sefav_pinyin.dat"
        tb = "tb_fav"
        update_flag = 0
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        conn360 = sqlite3.connect(self.dat_path)
        cur360 = conn360.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS {tb}(id INT PRIMARY KEY, title_pinyin VARCHAR(1024), "
                    f"title VARCHAR(1024), url VARCHAR(1024))")
        conn.commit()

        # TODO：判断360浏览器书签是否有更新，应该有更好的方式
        cur.execute(f"select count(1) from {tb}")
        ori_cnt = cur.fetchone()[0]
        cur360.execute(f"select count(1) from {tb}")
        new_cnt = cur360.fetchone()[0]
        if new_cnt != ori_cnt:
            update_flag = 1

        if update_flag == 1:
            cur.execute(f"delete from {tb}")
            conn.commit()
            cur360.execute(f"select title, url from {tb} where is_folder=0 order by create_time desc")
            items = [(pinyin.get(title, format="strip"), title, url) for (title, url) in cur360.fetchall()]

            cur.executemany(f"insert into {tb} (title_pinyin, title, url) values(?,?,?)", items)
            conn.commit()
        cur.execute(f"select title, url from {tb} where title_pinyin like '%{query}%' or url like '%{query}%'")
        ret = cur.fetchall()
        cur360.close()
        conn360.close()

        cur.close()
        conn.close()
        return ret

    def query(self, key):
        self.dat_path = next((Path.home() / r'AppData\Roaming\360se6\User Data\Default').glob('*/360sefav.dat'), '')
        default_result = [{"Title": "None", "SubTitle": f"Query: {key}", "IcoPath": "Images/app.ico"}]
        results = []
        if not key:
            return results
        if not self.dat_path:
            return default_result

        ret = self.get_pinyin_bookmarks(key)
        if not ret:
            return default_result
        for (title, url) in ret:
            results.append({
                "Title": title,
                "SubTitle": "{}".format(url),
                "IcoPath": "Images/app.ico",
                "JsonRPCAction": {
                    # 这里除了自已定义的方法，还可以调用Wox的API。调用格式如下：Wox.xxxx方法名
                    # 方法名字可以从这里查阅https://github.com/qianlifeng/Wox/blob/master/Wox.Plugin/IPublicAPI.cs 直接同名方法即可
                    "method": "open_url",
                    # 参数必须以数组的形式传过去
                    "parameters": [url],
                    # 是否隐藏窗口
                    "dontHideAfterAction": True}
            })

        return results

    def open_url(self, url):
        webbrowser.open(url)
        # todo:doesn't work when move this line up
        WoxAPI.change_query(url)


if __name__ == "__main__":
    Main()
