# Copyright (c) Microsoft. All rights reserved.
# some codes are from: https://github.com/namisan/mt-dnn
# please cite the (arXiv preprint arXiv:2002.07972) if you use the script
# by Xiaodong Liu 
# xiaodl@microsoft.com
# 10/08/2021

import os
import argparse
from random import shuffle
import json
import pandas as pd
import random

def load_boolq(file):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            label = data['label'] if 'label' in data else False
            label = 1 if label else 0
            uid = data['idx']
            sample = {'uid': uid, 'premise': data['passage'], 'hypothesis': data['question'], 'label': label}
            rows.append(sample)
    return rows

def load_cb(file):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            label = data['label'] if 'label' in data else 0
            uid = data['idx']
            sample = {'uid': uid, 'premise': data['premise'], 'hypothesis': data['hypothesis'], 'label': label}
            rows.append(sample)
    return rows

def load_multirc(file):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            pidx = data['idx']
            passage = data['passage']['text']
            questionts = data['passage']['questions']
            assert type(questionts) is list
            for question in questionts:
                q = question['question']
                qidx = question['idx']
                answers = question['answers']
                for answer in answers:
                    a = answer['text']
                    aidx = answer['idx']
                    label = answer['label'] if 'label' in answer else 0
                    uid = "{}_{}_{}".format(pidx, qidx, aidx)
                    sample = {'uid': uid, 'premise': passage, 'hypothesis': q, 'label': label, 'answer': a}
                    rows.append(sample)
        return rows

def load_wic(file):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            label = data['label'] if 'label' in data else False
            label = 1 if label else 0
            uid = data['idx']
            word = data['word']
            premise = data['sentence1']
            hyp = data['sentence2']
            sample = {'uid': uid, 'premise': word, 'hypothesis': premise, 'hypothesis_extra': hyp, 'label': label}
            rows.append(sample)
    return rows

def load_record(file):
    rows = []
    is_training =True if ("train" in file or "val" in file) else False
    with open(file, encoding="utf8") as f:
        cnt = 0
        for line in f:
            data = json.loads(line)
            passage = data['passage']['text']
            passage = passage.replace('\n', ' ')
            passage_idx = data['idx']
            entities = data['passage']['entities']
            entities_set = set([passage[entity["start"] : entity["end"] + 1] for entity in entities])
            qas = data['qas']
            for qa in qas:
                query = qa['query']
                answers_dict = {}
                answers_set =  set()
                if "answers" in qa:
                    answers_dict = {(answer["start"], answer["end"]): answer["text"] for answer in qa["answers"]}
                    answers_set= set(answer["text"] for answer in qa["answers"])
                query_idx = qa['idx']
                if is_training:
                    negative_set = entities_set - answers_set
                    # enumerate all the nagative set
                    positives = list(answers_set)
                    for negative in negative_set:
                        orders = [0, 1]
                        # shuffle the order of pos/negative samples
                        if "train" in file: shuffle(orders)
                        query_n = query.replace("@placeholder", negative)
                        positive = random.sample(positives, 1).pop()
                        query_p = query.replace("@placeholder", positive)
                        queries = [query_n, query_p]
                        queries = [queries[idx] for idx in orders]
                        new_answers = [negative, positive]
                        new_answers = [new_answers[idx] for idx in orders]
                        label = 1 if orders[0] == 0 else 0
                        sample = {'uid': str(query_idx), 'premise': passage, 'hypothesis': queries[0], 'hypothesis_extra': queries[1], 'label': label, "answer": str(new_answers)}
                        rows.append(sample)
                else:
                    for entity in entities_set:
                        label = False
                        if len(answers_dict) > 0:
                            if entity in answers_set:
                                label = True
                        updated_query = query.replace("@placeholder", entity)
                        uid = str(query_idx)
                        label = 1 if label else 0
                        sample = {'uid': uid, 'premise': passage, 'hypothesis': updated_query, 'hypothesis_extra': updated_query, 'label': label, "answer": entity}
                        rows.append(sample)
    return rows

def load_record_eval(file):
    rows = []
    with open(file, encoding="utf8") as f:
        cnt = 0
        for line in f:
            data = json.loads(line)
            passage = data['passage']['text']
            passage = passage.replace('\n', ' ')
            passage_idx = data['idx']
            entities = data['passage']['entities']
            entities_set = set([passage[entity["start"] : entity["end"] + 1] for entity in entities])
            qas = data['qas']
            for qa in qas:
                query = qa['query']
                answers_dict = {}
                answers_set =  set()
                if "answers" in qa:
                    answers_dict = {(answer["start"], answer["end"]): answer["text"] for answer in qa["answers"]}
                    answers_set= set(answer["text"] for answer in qa["answers"])
                query_idx = qa['idx']
                for entity in entities_set:
                    label = False
                    if len(answers_dict) > 0:
                        if entity in answers_set:
                            label = True
                    updated_query = query.replace("@placeholder", entity)
                    uid = str(query_idx)
                    label = 1 if label else 0
                    sample = {'uid': uid, 'premise': passage, 'hypothesis': updated_query, 'label': label, "answer": entity}
                    rows.append(sample)
    return rows

def load_copa(file):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            label = data['label'] if 'label' in data else 0
            uid = data['idx']
            # the token replacement idea is from RoBERTa
            # please cite RoBERTa paper if you use this
            # explanation by xiaodl@microsoft.com
            token = "because" if data["question"] ==  "cause" else "so"
            hyp1 = '{} {}'.format(token, data['choice1'])
            hyp2 = '{} {}'.format(token,  data['choice2'])
            sample = {'uid': uid, 'premise': data['premise'], 'hypothesis': hyp1, 'hypothesis_extra': hyp2, 'label': label}
            rows.append(sample)
    return rows

def load_copa_v0(file):
    ### ranking objective
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            label = data['label'] if 'label' in data else 0
            uid = data['idx']
            token = "because" if data["question"] ==  "cause" else "so"
            hyp1 = '{} {}'.format(token, data['choice1'])
            hyp2 = '{} {}'.format(token,  data['choice2'])
            hyp = [hyp1, hyp2]
            labels = [0, 0]
            labels[label] = 1
            for idx in range(0, len(hyp)):
                hp = hyp[idx]
                lab = labels[idx]
                sample = {'uid': uid, 'premise': data['premise'], 'hypothesis': hp, 'label': lab}
                rows.append(sample)
    return rows

def load_wsc(file, is_train=True):
    rows = []
    with open(file, encoding="utf8") as f:
        for line in f:
            data = json.loads(line.strip())
            premise = data['text']
            tokens = data['text'].split()
            target = data['target']
            tokens[target['span2_index']] = target['span1_text']
            hypothesis = ' '.join(tokens)
            label = str(data.get('label', "false")).lower()
            label = 1 if label == "true" else 0
            sample = {'uid': data['idx'], 'premise': premise, 'hypothesis': hypothesis, 'label': label}
            rows.append(sample)
    return rows

TASKS = {
    'boolq': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'cb': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'multirc': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'record': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'copa': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'wic': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'recordeval': ["train.jsonl", "val.jsonl", "test.jsonl"],
    'wsc': ["train.jsonl", "val.jsonl", "test.jsonl"],
}

LOAD_FUNCS = {
    'boolq': load_boolq,
    'cb': load_cb,
    'multirc': load_multirc,
    'record': load_record,
    'copa': load_copa,
    'wic': load_wic,
    'recordeval': load_record_eval,
    'wsc': load_wsc,
}

def save(data, fout):
    with open(fout, 'w', encoding='utf-8') as writer:
        writer.write("\n".join(data))
