# -*- coding: gb2312 -*-
import json
import os
from openai import OpenAI

# TODO didi

def generatedataset(title, DE):
    os.environ["OPENAI_API_KEY"] = "sk-9DTRcJyDuhIBhuy6Ef61B3C9Df77431e832a0f68E9F827Bd"
    client = OpenAI(base_url="https://api.xty.app/v1")
    result = []
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
             "content": "Text:{}, List:{}".format("An Image Interpolation Method Based on Weighted Subdivision",
                                                  '["Image interpolation","mesh","rational","subdivision"]')
             },
        ]
    )
    print(response.choices[0].message.content)
    result.append({"Text":title, "tag":response.choices[0].message.content})
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    pass
    # �������ݼ�

    # �������ݣ��õ�title��de

    # ��ʼ��ע
    # generatedataset(title, DE)

