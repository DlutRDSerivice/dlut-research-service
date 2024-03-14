# -*- coding: gb2312 -*-

from transformers import BertTokenizer

# �����ʵ��ʶ����
keywords = []
entities = [("directional object detection", "Object"), ("convolutional neural network", "Object")]

# ʾ������
sentence = "A novel directional object detection method for piled objects using a hybrid region-based convolutional neural network."

# ��ʼ��BERT�ִ���
# tokenizer = BertTokenizer.from_pretrained('dslim/bert-base-NER')
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
# �Ծ��ӽ��зִ�
tokenized_sentence = tokenizer.tokenize(sentence)
print(tokenized_sentence)
# ����һ����ִʾ��ӵȳ����б���ʼֵΪ'O'
labels = ['O'] * len(tokenized_sentence)

# Ϊʶ�����ʵ�����BIO��ǩ
for entity, entity_type in entities:
    entity_tokens = tokenizer.tokenize(entity)
    start_index = None
    # �ڷִʺ�ľ����в���ʵ��Ŀ�ʼλ��
    for i in range(len(tokenized_sentence) - len(entity_tokens) + 1):
        if tokenized_sentence[i:i+len(entity_tokens)] == entity_tokens:
            start_index = i
            break
    # ����ҵ�ʵ�壬Ϊ�����BIO��ǩ
    if start_index is not None:
        labels[start_index] = f"B-{entity_type}"
        for i in range(start_index + 1, start_index + len(entity_tokens)):
            labels[i] = f"I-{entity_type}"

# print({"":tokenized_sentence, labels)
# ��ӡ���
for token, label in zip(tokenized_sentence, labels):
    print(f"{token}\t{label}")

