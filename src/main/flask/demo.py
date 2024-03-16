# -*- coding: gb2312 -*-
import ast
import json
import os
from openai import OpenAI
from pipeline.PaperPipeline import PaperDataset


# TODO didi

def generatedataset(title, DE) -> dict:
    os.environ["OPENAI_API_KEY"] = "sk-9DTRcJyDuhIBhuy6Ef61B3C9Df77431e832a0f68E9F827Bd"
    client = OpenAI(base_url="https://api.xty.app/v1")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # Text �Ǳ��⣬
        # List �ǹؼ����б�
        # ��Щ�ؼ����б�Ϊ�գ����Ϊ�գ�����������ס�
        messages=[
            {"role": "system",
             "content": "You are a AI model. You need to understand a piece of text and based on this text"
                        "to tag the words in this phrase list as 'method' or 'object'."
                        "You only need to return a list like [(word, tag)]."},
            {"role": "user",
             # �˴��Ĳ���Ϊʾ�����ɸ�Ϊ����title �� de
             "content": "Text:{}, List:{}".format(title, DE)
             },
        ]
    )
    result = response.choices[0].message.content.replace("\n", "")
    if ast.literal_eval(result):
        return {"Text":title, "tag":result}



if __name__ == '__main__':

    # �������ݼ�
    wos_datas = PaperDataset(r'C:\Users\AI\Desktop\data\AI', "TI", "DE")
    # �������ݣ��õ�title��de
    result = []
    num:int  = 0
    for i in wos_datas:
        num += 1
        if i.DE == '':
            continue
        result.append(generatedataset(i.TI, i.DE))
        if num % 1000 == 0:
            print("Already process {} paper".format(num))

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)



